# Utilities Split Refactor

## Purpose

This branch refactors the original `utilities.py` module into smaller, purpose-specific modules.

The goal is to improve maintainability and make future changes easier by separating unrelated functionality while preserving existing behavior.

This refactor is primarily architectural. It is not intended to change the output of generated PDFs or alter the behavior of card creation.

## Scope

### Included

- Split utility functions into focused modules under `src/`
- Update project-wide imports to reference the new module locations
- Preserve existing public behavior and CLI functionality
- Add tests and documentation to support the new structure

### Intentionally Not Included

- Refactoring `page_manager.py`
- Redesigning page generation logic
- Changing PDF layout algorithms
- Large-scale cleanup beyond the utilities split 

`page_manager.py` remains responsible for page-level generation and registration mark handling. Any future architectural changes involving page management should be handled separately.

## New Module Organization

### `src/paths.py`

Responsible for project paths and filesystem-related helpers.

Examples:

- Project root discovery
- Asset paths
- Output paths
- Directory/file helpers

---

### `src/pdf.py`

Responsible for PDF generation workflows.

Examples:

- Creating PDF output
- Managing generated page collections
- Converting generated pages into final output

---

### `src/layouts.py`

Responsible for loading and working with layout definitions.

Examples:

- Loading layout JSON
- Resolving card sizes
- Resolving paper sizes
- Resolving specialty layouts
- Layout-related helper functions

Note:

Layout responsibilities overlap with PDF generation and page management because layouts define the geometry used when placing cards.

---

### `src/images.py`

Responsible for general image manipulation.

Examples:

- Image resizing
- Image transformations
- Image processing unrelated to cropping

---

### `src/crop.py`

Responsible for image cropping operations.

This module currently contains a small number of tightly related functions.

Future consolidation into `images.py` may be considered if cropping functionality remains small.

---

### `src/draw.py`

Responsible for drawing operations.

Examples:

- Drawing cards onto pages
- Drawing outlines
- Rendering visual elements

Some overlap exists with `images.py` because SCM creates pages by manipulating images rather than drawing directly to a PDF canvas.

---

### `src/offset.py`

Responsible for saved image offsets.

Examples:

- Saving offsets
- Loading offsets
- Applying offsets to generated pages

---

### `src/measurements.py`

Responsible for measurement parsing and unit conversion.

Examples:

- Parsing strings such as `3mm` or `0.125in`
- Converting between units
- Pixel calculations

---

### `src/enums.py`

Contains shared enumerations.

Examples:

- Registration modes
- Orientation
- Fit modes
- Other shared constants represented as enums

## Source Roadmap

The refactor reorganizes the previous monolithic `utilities.py` module into focused modules under `src/`. This roadmap lists the current ownership of constants, classes, and functions after the split.

This is intended as a guide for reviewers and future contributors. Some internal implementation details may continue to move as the project evolves.

---

### `src/draw.py`

#### Functions
- `draw_card_with_bleed`
- `draw_card_layout`
- `draw_card_layouts`
- `draw_outline`
- `draw_outlines`

---

### `src/enums.py`

#### Classes
- `Registration`
- `Orientation`
- `OrientationMode`
- `Variant`
- `Unit`
- `FitMode`

---

### `src/images.py`

#### Constants
- `MINIMUM_BLEED`

#### Functions
- `calculate_max_print_bleed`
- `fill_rounded_corners`
- `load_card_image`
- `convert_inch_to_crop`
- `parse_dimension_string`
- `parse_crop_string`
- `crop_and_scale_image`

---

### `src/layouts.py`

#### Constants
- `CUTTING_TEMPLATES_DIR_ENV`
- `EXTRA_LAYOUTS_ENV`
- `EXTRA_LAYOUTS_PATH`
- `LAYOUTS_FILENAME`
- `LAYOUTS_PATH`

#### Classes
- `RegistrationSettings`
- `VariantRegistrationSettings`
- `DefaultSettings`
- `CardSizeDef`
- `PaperSizeDef`
- `CardLayout`
- `SpecialtyCardSizeDef`
- `SpecialtyPaperSizeDef`
- `SpecialtyLayoutDef`
- `LayoutConfig`

#### Functions
- `extra_layout_paths`
- `find_extra_layout_owner`
- `merge_extra_layouts`
- `resolve_cutting_templates_dir`
- `resolve_card_size_alias`
- `resolve_paper_size_alias`
- `get_all_card_size_names`
- `get_all_paper_size_names`
- `get_all_specialty_layout_names`
- `load_layout_config`
- `biased_sort`

`biased_sort` is currently retained as a layout-related helper. It may be relocated in a future cleanup if a more general utility module is introduced.

---

### `src/measurements.py`

#### Constants
- `MM_PER_INCH`
- `PT_PER_INCH`
- `_UNIT_PATTERN`

#### Functions
- `parse_unit_string`
- `size_to_mm`
- `size_to_in`
- `size_to_pt`
- `size_to_pixel`

---

### `src/offset.py`

#### Constants
- `DATA_PATH`
- `OFFSET_DATA_PATH`

#### Classes
- `OffsetData`

#### Functions
- `save_offset`
- `load_saved_offset`
- `offset_images`

---

### `src/page_manager.py`

#### Constants
- `BORDERLESS_EXPANSION_MM`
- `BORDERLESS_INSET_MM`
- `MAX_REG_INSET_MM`
- `MAX_REG_LENGTH_MM`
- `MAX_REG_THICKNESS_MM`
- `MIN_REG_INSET_MM`
- `MIN_REG_LENGTH_MM`
- `MIN_REG_THICKNESS_MM`
- `REG_PADDING_MM`

#### Classes
- `CardLayout`

#### Functions
- `generate_reg_mark`
- `normalize_page_size`
- `compute_grid_fit`
- `select_best_margins`
- `compute_card_positions`
- `generate_layout`

---

### `src/paths.py`

#### Constants
- `RELATIVE_ROOT`
- `VALID_MIMETYPES`

#### Classes
- `Paths`

#### Functions
- `check_paths_subset`
- `delete_hidden_files_in_directory`
- `get_directory`
- `ensure_directory`
- `ensure_output_directory_exists`
- `get_image_file_paths`
- `get_back_card_image_path`
- `resolve_image_with_any_extension`

---

### `src/pdf.py`

#### Functions
- `create_template_name`
- `add_front_back_pages`
- `find_best_orientation`
- `generate_pdf`

## Known Boundary Areas

Some responsibilities intentionally remain somewhat flexible because of how SCM operates.

### PDF vs Images

SCM does not directly place vector objects onto a PDF canvas. Instead:

1. Card images are placed onto page images.
2. Page images are converted into PDF pages.

Because of this, responsibilities between `pdf.py`, `draw.py`, and `images.py` overlap.

### Layouts vs Page Generation

Layouts define where cards belong, but page generation determines how those positions are used.

Some layout calculations currently interact with:

- `layouts.py`
- `draw.py`
- `pdf.py`
- `page_manager.py`

Further separation may require a larger redesign beyond the scope of this refactor.

## Review Notes

This branch intentionally favors a conservative architectural split over a complete redesign.

The priority is:

1. Preserve existing behavior.
2. Improve module boundaries.
3. Make future refactors smaller and safer.
4. Avoid introducing unrelated changes into the same PR.

--- 

## Future Work

Potential future improvements:

- Further separation of page generation from image manipulation
- Consolidation of small modules where boundaries are no longer useful
- Migration from mixed `str`/`Path` usage to consistent `Path` usage
- Possible redesign of page management responsibilities

---

## AI Disclaimer 
AI assistance was used in this refactor, including the generation of this document. All of the code was typed by hand (even the code directly copied from `utilities.py`) to help me better understand the
project as a whole. ChatGPT was primarily used to assist with naming conventions and identifying modernization methods, as well as a ton of sanity checks (even though it *really* wanted to make `src/bleed.py` for some reason). For example, we had a riveting discussion on what to name the `Paths` class, whether it should even be a class, and what the scope of its content should be. Super exciting stuff.
