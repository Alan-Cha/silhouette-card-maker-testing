# Extra Layouts

Drop any number of `*.json` files here to extend `layouts.json` with additional card sizes,
paper sizes, and layouts, without modifying this repo. Files are merged in filename order;
see `merge_extra_layouts()` in `utilities.py` for the merge rules.

This directory is empty by default — nothing here changes behavior until you add a file. For
an example of a project that defines its own card sizes this way, see
[scm-extras](https://github.com/Alan-Cha/scm-extras).
