import json
import os
import platform
import re
from pathlib import Path

import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
SYMBOLS_DIR = ASSETS_DIR / "mana_symbols"
MANIFEST_PATH = ASSETS_DIR / "mana_symbols_manifest.json"

SCRYFALL_SYMBOLOGY_URL = "https://api.scryfall.com/symbology"


def _configure_macos_cairo_path() -> None:
    if platform.system() != "Darwin":
        return

    candidates = ["/opt/homebrew/lib", "/usr/local/lib"]
    existing = [path for path in candidates if os.path.isdir(path)]
    if not existing:
        return

    current = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    current_parts = [part for part in current.split(":") if part]
    merged_parts = current_parts[:]
    for path in existing:
        if path not in merged_parts:
            merged_parts.append(path)

    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join(merged_parts)


def _sanitize_filename(symbol_name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]+", "_", symbol_name).strip("_")
    if not safe:
        safe = "symbol"
    return f"{safe}.png"


def _fetch_symbol_data() -> list[dict[str, str]]:
    response = requests.get(SCRYFALL_SYMBOLOGY_URL, timeout=20)
    response.raise_for_status()
    payload = response.json()

    symbol_data: list[dict[str, str]] = []
    seen_names: set[str] = set()

    for item in payload.get("data", []):
        symbol = item.get("symbol")
        if not symbol or not symbol.startswith("{") or not symbol.endswith("}"):
            continue

        symbol_name = symbol[1:-1].strip().upper()
        svg_uri = item.get("svg_uri")
        if not symbol_name:
            continue
        if not svg_uri:
            continue

        # Keep mana-related symbols plus commonly used game symbols seen in rules text.
        if item.get("represents_mana") or symbol_name in {"T", "Q", "E", "S", "CHAOS"}:
            if symbol_name in seen_names:
                continue
            seen_names.add(symbol_name)
            symbol_data.append({
                "name": symbol_name,
                "svg_uri": svg_uri,
            })

    symbol_data.sort(key=lambda item: item["name"])
    return symbol_data


def _download_symbol_png(svg_uri: str, output_path: Path) -> bool:
    try:
        _configure_macos_cairo_path()
        import cairosvg

        response = requests.get(svg_uri, timeout=20)
        response.raise_for_status()
        svg_bytes = response.content
        if len(svg_bytes) == 0:
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)
        cairosvg.svg2png(bytestring=svg_bytes, write_to=str(output_path))
        return True
    except Exception:
        return False


def main() -> None:
    SYMBOLS_DIR.mkdir(parents=True, exist_ok=True)

    symbol_data = _fetch_symbol_data()
    manifest: dict[str, str] = {}
    failures: list[str] = []

    for symbol in symbol_data:
        symbol_name = symbol["name"]
        filename = _sanitize_filename(symbol_name)
        output_path = SYMBOLS_DIR / filename
        ok = _download_symbol_png(symbol["svg_uri"], output_path)
        if ok:
            manifest[symbol_name] = f"mana_symbols/{filename}"
        else:
            failures.append(symbol_name)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Downloaded {len(manifest)} symbols to {SYMBOLS_DIR}")
    print(f"Wrote manifest: {MANIFEST_PATH}")
    if failures:
        print(f"Failed symbols ({len(failures)}): {', '.join(failures)}")


if __name__ == "__main__":
    main()
