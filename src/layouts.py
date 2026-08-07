# ==============================================================================
# layouts.py
#     Handles the card/page layout system for all card/paper types.
# ==============================================================================
from __future__ import annotations

import json
import os

from src.measurements import size_to_mm
from src.paths import Paths
from src.enums import Orientation

from typing import Any
from pathlib import Path
from pydantic import BaseModel, model_validator

LAYOUTS_FILENAME = "layouts.json"
LAYOUTS_PATH = Paths.assets / LAYOUTS_FILENAME

# Optional extra layout definitions to merge on top of layouts.json. Lets a layout-consuming
# project layer its own card sizes, paper sizes, and layouts on top of this repo's without
# modifying it. Opt-in: both are empty/unset by default, so load_layout_config() behaves
# exactly as if this didn't exist. Two ways to supply extra files, merged in this order:
#   1. Drop any number of *.json files into EXTRA_LAYOUTS_DIR (merged in filename order) -
#      no configuration needed, just copy a file in.
#   2. Point EXTRA_LAYOUTS_ENV at one or more file paths (os.pathsep-separated, merged in
#      order) - for files that live outside EXTRA_LAYOUTS_DIR.
EXTRA_LAYOUTS_PATH = Paths.assets / "extra_layouts"
EXTRA_LAYOUTS_ENV = "SCM_EXTRA_LAYOUTS"

# Optional override for where cutting templates get written/read (default: SCRIPT_DIR-relative
# cutting_templates/ directories in generate_dxf.py and dxf_to_studio3.py).
CUTTING_TEMPLATES_DIR_ENV = "SCM_CUTTING_TEMPLATES_DIR"

# ============================
# Classes
# ============================
# These classes set up structure to properly import the JSONs.


class RegistrationSettings(BaseModel):
    inset: str | None = None
    thickness: str | None = None
    length: str | None = None


class VariantRegistrationSettings(BaseModel):
    default: RegistrationSettings
    borderless: RegistrationSettings


class DefaultSettings(BaseModel):
    card_radius: str
    registration: VariantRegistrationSettings


class CardSizeDef(BaseModel):
    width: str
    height: str
    radius: str | None = None
    aliases: list[str] | None = None


class PaperSizeDef(BaseModel):
    width: str
    height: str
    aliases: list[str] | None = None

    @model_validator(mode="after")
    def validate_orientation(self) -> "PaperSizeDef":
        if size_to_mm(self.width) < size_to_mm(self.height):
            raise ValueError(
                f"Paper width ({self.width}) must be >= height ({self.height}). Paper sizes are stored as landscape."
            )
        return self


class CardLayout(BaseModel):
    orientation: Orientation
    registration_orientation: Orientation | None = None
    version: int
    num_rows: int | None = None
    num_cols: int | None = None
    registration: RegistrationSettings | None = None


class SpecialtyCardSizeDef(BaseModel):
    name: str | None = None
    width: str | None = None
    height: str | None = None
    radius: str | None = None


class SpecialtyPaperSizeDef(BaseModel):
    name: str | None = None
    width: str | None = None
    height: str | None = None


class SpecialtyLayoutDef(BaseModel):
    card_size: SpecialtyCardSizeDef
    paper_size: SpecialtyPaperSizeDef
    orientation: Orientation = Orientation.LANDSCAPE
    registration_orientation: Orientation | None = None
    version: int = 1
    num_rows: int | None = None
    num_cols: int | None = None
    registration: RegistrationSettings | None = None


class LayoutConfig(BaseModel):
    ppi: int
    defaults: DefaultSettings
    card_sizes: dict[str, CardSizeDef]
    paper_sizes: dict[str, PaperSizeDef]
    layouts: dict[
        str, dict[str, dict[str, CardLayout]]
    ]  # layouts[paper][card][variant]
    specialty_layouts: dict[str, SpecialtyLayoutDef] | None = None


# ============================
# Extra Layouts
# ============================
def extra_layout_paths() -> list[Path]:
    dir_paths = sorted(EXTRA_LAYOUTS_PATH.glob("*.json"))
    env_paths = [
        Path(p) for p in os.getenv(EXTRA_LAYOUTS_ENV, "").split(os.pathsep) if p
    ]
    return dir_paths + env_paths


def find_extra_layout_owner(section: str, key: str) -> Path | None:
    for path in extra_layout_paths():
        with path.open("r") as f:
            if key in json.load(f).get(section, {}):
                return path
    return None


def merge_extra_layouts(raw_config: dict[str, Any]) -> dict[str, Any]:
    for path in extra_layout_paths():
        with path.open("r") as f:
            extra = json.load(f)

        for section in ("card_sizes", "paper_sizes"):
            for key, value in extra.get(section, {}).items():
                if key in raw_config[section]:
                    raise ValueError(f"'{key}' in {section} of {path} already defined.")
                raw_config[section][key] = value

        for paper, cards in extra.get("layouts", {}).items():
            for card, variants in cards.items():
                for variant, layout_def in variants.items():
                    if variant in raw_config["layouts"].get(paper, {}).get(
                        card, {}
                    ):
                        raise ValueError(
                            f"Layout '{paper}'/'{variant}' in {path} already defined."
                        )
                    raw_config["layouts"].setdefault(paper, {}).setdefault(
                        card, {}
                    )[variant] = layout_def
    return raw_config


# ============================
# Resolvers
# ============================
def resolve_cutting_templates_dir(default: Path) -> Path:
    override = os.getenv(CUTTING_TEMPLATES_DIR_ENV)
    return Path(override) if override else default


def resolve_card_size_alias(layout_config: LayoutConfig, card_size: str) -> str:
    for name, card_def in layout_config.card_sizes.items():
        if card_def.aliases and (card_size in card_def.aliases):
            print(
                f"Card size '{card_size}' is an alias of '{name}'. Using '{name}' card size and cutting template."
            )
    return card_size


def resolve_paper_size_alias(layout_config: LayoutConfig, paper_size: str) -> str:
    for name, paper_def in layout_config.paper_sizes.items():
        if paper_def.aliases and (paper_size in paper_def.aliases):
            print(
                f"Paper size '{paper_size}' is an alias of '{name}'. Using '{name}' paper size and cutting template."
            )
            return name
    return paper_size


# ============================
# Get All's
# ============================
def get_all_card_size_names(layout_config: LayoutConfig) -> list[str]:
    names = list(layout_config.card_sizes.keys())
    for card_def in layout_config.card_sizes.values():
        if card_def.aliases:
            names.extend(card_def.aliases)
    return biased_sort(names, ["standard", "poker", "bridge"])


def get_all_paper_size_names(layout_config: LayoutConfig) -> list[str]:
    names = list(layout_config.paper_sizes.keys())
    for paper_def in layout_config.paper_sizes.values():
        if paper_def.aliases:
            names.extend(paper_def.aliases)
    return biased_sort(names, ["letter", "tabloid", "a4", "a3", "arch_b"])


def get_all_specialty_layout_names(layout_config: LayoutConfig) -> list[str]:
    if layout_config.specialty_layouts:
        return sorted(layout_config.specialty_layouts.keys())
    return []


# ============================
# Load Config
# ============================
def load_layout_config() -> LayoutConfig:
    with open(LAYOUTS_PATH, "r") as f:
        raw_config = json.load(f)
    merge_extra_layouts(raw_config)
    return LayoutConfig(**raw_config)


# ============================
# Misc
# ============================
def biased_sort(items: list[str], priority: list[str]) -> list[str]:
    priority_items = [s for s in priority if s in items]
    rest = sorted(
        (s for s in items if s not in priority), key=lambda s: (s[0].isdigit(), s)
    )
    return priority_items + rest
