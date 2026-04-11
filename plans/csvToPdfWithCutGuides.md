## Plan: Markdown to PDF with Cut Guides

Create a new CLI script (`translated_text_boxes_to_pdf.py`) that generates printable PDFs from Markdown input. Each entry (separated by `---`) becomes a text box (2.25" × 1.25") with dynamic font sizing and preserved formatting (**bold**, *italic*), arranged on pages with cut guides for all supported paper sizes.

---

**Input Format**

Markdown file with entries separated by `---`:
```markdown
### Card Name {mana cost}

*Card Type — Subtype*

Rules text with **bold keywords** and line breaks preserved.

**Power/Toughness or Loyalty**

---

### Next Card...
```

---

**Steps**

**Phase 1: Layout Configuration**
1. Add `"text_box"` card size to [assets/layouts.json](assets/layouts.json): `{"width": 675, "height": 375}` (2.25" × 1.25" at 300 PPI)
2. Add `text_box` layout positions for each paper size (Letter: 4×6, A4: 4×5, A3: 6×8, Tabloid: 6×7, ArchB: 7×8 grid)

**Phase 2: Markdown Parsing & Text Rendering** *(parallel with Phase 1)*
3. Add `parse_markdown_entries()` to utilities.py — split file by `---`, extract entries
4. Add `fit_text_to_box()` to [utilities.py](utilities.py) — dynamic font sizing using `ImageDraw.multiline_textbbox()`, binary search from 24pt down to 6pt minimum
5. Add `draw_text_box()` to utilities.py — render text box with border, left-aligned text, padding 8-10px; support **bold** and *italic* formatting via font switching (arial.ttf, arialbd.ttf, ariali.ttf)

**Phase 3: PDF Generation**
6. Add `generate_md_pdf()` to utilities.py — load blank page images, iterate entries, place text boxes using layout positions, draw box borders as cut guides, handle pagination, save multi-page PDF *(depends on steps 1-5)*
7. Create `translated_text_boxes_to_pdf.py` with Click CLI — options: `--input_path`, `--output_path`, `--paper_size`, `--ppi`, `--quality` *(depends on step 6)*

---

**Markdown Formatting Support**

| Markdown | Rendered As |
|----------|-------------|
| `### Title` | Bold header line (larger font if space allows) |
| `**bold**` | Bold text (arialbd.ttf) |
| `*italic*` | Italic text (ariali.ttf) |
| Line breaks | Preserved as-is |
| `---` | Entry separator (not rendered) |

---

**Relevant Files**
- [utilities.py](utilities.py) — Add `parse_markdown_entries()`, `fit_text_to_box()`, `draw_text_box()`, `generate_md_pdf()` functions
- [assets/layouts.json](assets/layouts.json) — Add `text_box` size and layout positions
- `translated_text_boxes_to_pdf.py` *(new)* — CLI entry point following [create_pdf.py](create_pdf.py) pattern
- [assets/arial.ttf](assets/arial.ttf) — Regular font
- `assets/arialbd.ttf` *(may need to add)* — Bold font for `**text**`
- `assets/ariali.ttf` *(may need to add)* — Italic font for `*text*`

---

**Verification**
1. Generate PDF from sample markdown, visually verify text fits, formatting preserved, boxes readable
2. Test **bold** and *italic* rendering renders correctly
3. Test pagination with 50+ entries
4. Test all paper sizes (Letter, A4, A3, Tabloid, ArchB)
5. Run `python translated_text_boxes_to_pdf.py --help` to verify CLI documentation
6. Edge case: Test with very long text to verify truncation with "..." at 6pt minimum

---

**Decisions**
- New standalone script (`translated_text_boxes_to_pdf.py`) for cleaner separation
- Use markdown format for rich text support (bold, italic, line breaks)
- Entries separated by `---` horizontal rules
- `### Header` lines rendered as bold title within each box
- Draw thin black border (1px) on each box as cut guide
- If text too long at 6pt minimum → truncate with ellipsis

---

**Further Considerations**
1. **Font availability**: Need to verify bold/italic Arial variants exist in assets, or fall back to simulating with regular font. *Recommendation: Check system fonts or bundle font variants*

2. **Header formatting**: Should `### Title` be rendered on a separate line with larger font, or same size as body text? *Recommendation: Bold, same line height, to maximize space for rules text*
