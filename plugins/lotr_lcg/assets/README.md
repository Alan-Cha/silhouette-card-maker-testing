# Local LOTR Back Assets

Place your local LOTR back scans in this directory before running `plugins/lotr_lcg/fetch.py`.

Expected filenames:

- `Player Card Back.jpg`
- `Encounter Card Back.jpg`

These image files are intentionally ignored by git and are not part of the plugin source. The reason is simple: official card-back scans are game assets, so users should provide their own local copies instead of redistributing them through the repository.

Once those files are present, the plugin will automatically copy the correct back into `game/back/` when you fetch:

- `ringsdb` and `ringsdb_fellowship` use `Player Card Back.jpg`
- `ringsdb_scenario` uses `Encounter Card Back.jpg`
