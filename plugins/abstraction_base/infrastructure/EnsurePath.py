from pathlib import Path

def EnsurePath(path: Path) -> None:
    path.mkdir(parents = True, exist_ok = True)
