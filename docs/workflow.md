# Editing workflow

The Excel workbook is where you edit. The CSVs in `data/` and `vocab/` are the canonical record in git. Two scripts move data between them, and one checks it.

```
workbook/historical_polities.xlsx  --export.py-->  data/*.csv, vocab/*.csv  --validate.py-->  0 errors?  -->  upload to v2
                                   <--make_workbook.py--   (only when the CSVs changed outside Excel)
```

## One-time setup
```
pip install openpyxl
```
(`validate.py` needs nothing extra; `export.py` and `make_workbook.py` need openpyxl.)

## Normal loop
1. Open `workbook/historical_polities.xlsx`, edit, save, close Excel.
2. In the repo folder run `python scripts/export.py --refresh` (or `py scripts\export.py --refresh`). It writes the CSVs, runs the validator and, if there are no errors, rebuilds the workbook so the grey labels are up to date. Close the workbook in Excel first. Without `--refresh` the workbook is left as it is.
3. Fix any errors, then export again.
4. Upload `repo/` to the `v2` branch (checklist in `notes/HANDOFF.md`). GitHub runs the validator again.

## Workbook conventions
- One sheet per table, same name and columns as the CSV; vocabularies are the `vocab_…` sheets. Column meanings: `docs/schema.md`.
- **Dropdowns** on every enum and ID column. To use a new term (religion, capital, title…), add it to its `vocab_…` sheet first; it then appears in the dropdowns. In `polity_attributes`, the `value_id` dropdown follows the `attribute` chosen in the same row.
- **Grey `_` columns** show the label for the ID next to them, as plain text (not formulas, which made Excel freeze). They don't update while you edit; `export.py --refresh` brings them up to date. They and the `_about` / `_lists` sheets are never exported.
- **New IDs:** next free number (`P01361`, `R023498`, `P00001-04` for a new phase). Never reuse or renumber. A removed or merged polity goes into `retired_ids`.
- **A new polity** needs, at minimum: a `polities` row, a `spans` row, at least one `phases` row covering the span, and a `ratings` row; the validator lists anything missing.
- Years are whole numbers, BCE negative, no year 0; an empty end means "present"; an empty precision means exact.
- `source` can list several keys with `;` (the dropdown warns but accepts it).

## Rebuilding the workbook
If CSVs were changed outside Excel (e.g. by a script in a Claude session), rebuild with `python scripts/make_workbook.py`. This overwrites the workbook, so export any unsaved workbook edits first.
