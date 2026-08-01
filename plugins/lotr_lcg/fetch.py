import sys
from os import path

from click import Choice, argument, command, option

# Add parent directory to path to allow imports when run as a script
REPO_ROOT = path.abspath(path.join(path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

from plugins.lotr_lcg.deck_formats import DeckFormat, parse_deck
from plugins.lotr_lcg.hallofbeorn import ScenarioMode
from plugins.lotr_lcg.ringsdb import get_handle_card
from utilities import ensure_directory

front_directory = path.join(REPO_ROOT, "game", "front")
double_sided_directory = path.join(REPO_ROOT, "game", "double_sided")


@command()
@argument("deck_path")
@argument("format", type=Choice([t.value for t in DeckFormat], case_sensitive=False))
@option(
    "--scenario_mode",
    default=ScenarioMode.NORMAL.value,
    type=Choice([t.value for t in ScenarioMode], case_sensitive=False),
    show_default=True,
    help="Encounter card counts to use when fetching scenarios.",
)
def cli(deck_path: str, format: DeckFormat, scenario_mode: str):
    ensure_directory(front_directory)
    ensure_directory(double_sided_directory)

    parse_deck(
        deck_path,
        format,
        get_handle_card(front_directory, double_sided_directory),
        scenario_mode=scenario_mode,
    )


if __name__ == "__main__":
    cli()
