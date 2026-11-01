"""Build the editing workbook from the canonical CSVs.

Usage (from the repo root):
    pip install openpyxl
    python scripts/make_workbook.py            # data/*.csv + vocab/*.csv -> workbook/historical_polities.xlsx
Run it once to create the workbook, or again whenever the CSVs were changed outside Excel (it overwrites the workbook).
The normal loop is the other direction: edit the workbook, then run scripts/export.py.

Workbook layout:
  - one sheet per table, same name and columns as the CSV (vocabularies: "vocab_<name>");
  - dropdowns on every enum and foreign-key column, fed by the vocabulary sheets (they grow automatically up to row 20,000);
  - grey "_" helper columns showing labels next to IDs (formulas; never exported);
  - "_about" (instructions) and "_lists" (hidden enum lists) are helper sheets and are not exported.
"""
import argparse, csv, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import SPEC, ENUM, ATTR_VOCAB
from export import NUMERIC, WORKBOOK, sheet_name

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter

MAXROW = 20000     # dropdown sources and validations cover this many rows
HEAD = Font(bold=True, color='FFFFFF')
HEAD_FILL = PatternFill('solid', fgColor='305496')
HELP_HEAD_FILL = PatternFill('solid', fgColor='808080')
HELP_FILL = PatternFill('solid', fgColor='EDEDED')
SHEET_ORDER = ['polities', 'spans', 'phases', 'measures', 'ratings', 'polity_attributes', 'rulers', 'polity_names',
               'relations', 'lineages', 'sources', 'retired_ids']
GRADES = ['S', 'A', 'B', 'C', 'D']
ENUM_LISTS = {  # name of the hidden list -> values (from the validator, so they always agree)
    'precision': sorted(ENUM['precision']), 'certainty': ['certain', 'probable', 'disputed'],
    'evidence_tier': ['A', 'B', 'C'], 'name_type': ['official', 'conventional', 'historiographic', 'alternative'],
    'relation_type': sorted(ENUM['relation_type']), 'attribute': list(ATTR_VOCAB),
    'attribute_role': ['ruling', 'majority', 'official', 'seat', 'secondary', 'symbolic'],
    'ruler_role': sorted(ENUM['ruler_role']), 'rating_method': ['legacy', 'manual', 'ai_assisted'],
    'gender': ['m', 'f', 'n'], 'bool': ['true', 'false'], 'grade': GRADES,
}
VOCAB_SHEETS = {  # list name -> sheet holding the ids in column A
    'regions': 'vocab_regions', 'countries': 'vocab_countries', 'ethnic_groups': 'vocab_ethnic_groups',
    'languages': 'vocab_languages', 'religions': 'vocab_religions', 'places': 'vocab_places',
    'government_types': 'vocab_government_types', 'titles': 'vocab_titles',
    'polities': 'polities', 'lineages': 'lineages', 'sources': 'sources',
}
# column -> (list name, strict?)   strict=False lets a value outside the list through with a warning (e.g. "enwiki;zhwiki")
DROPDOWNS = {
    'polities': {'region_id': ('regions', 1), 'region2_id': ('regions', 1), 'lineage_id': ('lineages', 1),
                 'evidence_tier': ('evidence_tier', 1)},
    'spans': {'polity_id': ('polities', 1)},
    'phases': {'polity_id': ('polities', 1)},
    'ratings': {**{d: ('grade', 1) for d in ('dur', 'area', 'pop', 'econ', 'mil', 'cult', 'tech', 'gov', 'soc')},
                'method': ('rating_method', 1)},
    'polity_attributes': {'polity_id': ('polities', 1), 'attribute': ('attribute', 1), 'value_id': ('BY_ATTRIBUTE', 1),
                          'role': ('attribute_role', 1), 'is_primary': ('bool', 1)},
    'rulers': {'polity_id': ('polities', 1), 'role': ('ruler_role', 1), 'title_id': ('titles', 1), 'is_acting': ('bool', 1)},
    'polity_names': {'polity_id': ('polities', 1), 'name_type': ('name_type', 1)},
    'relations': {'from_id': ('polities', 1), 'to_id': ('polities', 1), 'type': ('relation_type', 1)},
    'vocab_places': {'country': ('countries', 1)},
    'vocab_titles': {'gender': ('gender', 1)},
    'vocab_countries': {'is_current': ('bool', 1)},
}
COMMON = {'start_precision': ('precision', 1), 'end_precision': ('precision', 1), 'certainty': ('certainty', 1),
          'source': ('sources', 0)}
# helper label columns (inserted right after the named column). S09b: written as plain text computed here,
# not as formulas: 66,000 lookup formulas made Excel freeze. Labels refresh when the workbook is rebuilt
# (python scripts/export.py --refresh, or make_workbook.py).
HELPERS = {
    'spans': {'polity_id': ('_polity', 'polities')},
    'phases': {'polity_id': ('_polity', 'polities')},
    'polity_attributes': {'polity_id': ('_polity', 'polities'), 'value_id': ('_value', 'attribute_values')},
    'rulers': {'polity_id': ('_polity', 'polities'), 'title_id': ('_title', 'titles')},
    'polity_names': {'polity_id': ('_polity', 'polities')},
    'relations': {'from_id': ('_from', 'polities'), 'to_id': ('_to', 'polities')},
    'polities': {'region_id': ('_region', 'regions')},
}

def build_labels(repo):
    """id -> 'English / 中文' for every lookup the helper columns need."""
    def rows(p):
        with open(os.path.join(repo, p), encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f))
    def pl(r):
        en = r['name_en'] + (f" ({r['qualifier_en']})" if r['qualifier_en'] else '')
        zh = r['name_zh'] + (f"（{r['qualifier_zh']}）" if r['qualifier_zh'] else '')
        return f'{en} / {zh}'
    L = {'polities': {r['polity_id']: pl(r) for r in rows('data/polities.csv')},
         'titles': {t['id']: f"{t['en']} / {t['zh']}" for t in rows('vocab/titles.csv')},
         'regions': {t['id']: f"{t['en']} / {t['zh']}" for t in rows('vocab/regions.csv')},
         'attribute_values': {}}
    for v in ATTR_VOCAB.values():
        L['attribute_values'].update({t['id']: f"{t['en']} / {t['zh']}" for t in rows(f'vocab/{v}.csv')})
    return L

ABOUT = [
    ('Historical Polities v2 — editing workbook', True),
    ('', False),
    ('How to edit', True),
    ('1. Edit the sheets here. Each sheet is one table; the columns are defined in docs/schema.md.', False),
    ('2. Save, then run:  python scripts/export.py   (from the repo folder). It writes data/*.csv and vocab/*.csv and runs the validator.', False),
    ('3. Fix any errors the validator reports, export again, then upload the repo to the v2 branch (checklist in notes/HANDOFF.md).', False),
    ('', False),
    ('Conventions', True),
    ('• Grey columns starting with "_" only show labels next to IDs, as plain text. They are never exported. They do not update while you edit; run  python scripts/export.py --refresh  to export and rebuild the workbook with fresh labels.', False),
    ('• Sheets starting with "_" (this one, _lists) are helpers and are never exported.', False),
    ('• Dropdowns come from the vocab_ sheets. To add a new term (a religion, a capital, a title…), add a row to the vocab sheet first.', False),
    ('• Years: whole numbers, BCE negative, no year 0. An empty end means "present". Empty precision = exact; empty certainty = certain.', False),
    ('• New IDs: take the next free number (P01361, R023498, …). Never reuse or renumber an ID; a removed polity goes into retired_ids.', False),
    ('• "source" may hold several keys separated by ";" (e.g. enwiki;zhwiki); the dropdown will warn but allow it.', False),
    ('• The CSVs in git are the canonical record. If they are changed outside Excel, rebuild this workbook with scripts/make_workbook.py.', False),
]

def read(path):
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.reader(f))

def typed(v, col):
    if v != '' and col in NUMERIC:
        try:
            return int(v)
        except ValueError:
            try:
                return float(v)
            except ValueError:
                return v
    return v

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--out', default=WORKBOOK)
    a = ap.parse_args()
    wb = Workbook()
    about = wb.active
    about.title = '_about'
    for i, (text, bold) in enumerate(ABOUT, 1):
        c = about.cell(row=i, column=1, value=text)
        c.font = Font(bold=bold, size=14 if i == 1 else 11)
    about.column_dimensions['A'].width = 140

    # hidden enum lists
    lists = wb.create_sheet('_lists')
    for j, (name, vals) in enumerate(ENUM_LISTS.items(), 1):
        lists.cell(row=1, column=j, value=name).font = Font(bold=True)
        for i, v in enumerate(vals, 2):
            lists.cell(row=i, column=j, value=v)
        col = get_column_letter(j)
        wb.defined_names[f'list_{name}'] = DefinedName(f'list_{name}', attr_text=f"_lists!${col}$2:${col}${len(vals) + 1}")
    lists.sheet_state = 'hidden'
    for name, sheet in VOCAB_SHEETS.items():
        wb.defined_names[f'list_{name}'] = DefinedName(f'list_{name}', attr_text=f"'{sheet}'!$A$2:$A${MAXROW}")
    labels = build_labels(a.repo)
    for attr, vocab in ATTR_VOCAB.items():     # dependent dropdown for polity_attributes.value_id: INDIRECT(attribute)
        wb.defined_names[attr] = DefinedName(attr, attr_text=f"'{VOCAB_SHEETS[vocab]}'!$A$2:$A${MAXROW}")

    paths = sorted(SPEC, key=lambda p: (p.startswith('vocab/'),
                   SHEET_ORDER.index(sheet_name(p)) if sheet_name(p) in SHEET_ORDER else 99, p))
    for path in paths:
        name = sheet_name(path)
        rows = read(os.path.join(a.repo, path))
        header, body = rows[0], rows[1:]
        helpers = HELPERS.get(name, {})
        layout = []      # (header, source index or helper formula fn)
        for i, h in enumerate(header):
            layout.append((h, i))
            if h in helpers:
                layout.append((helpers[h][0], (helpers[h][1], i)))
        ws = wb.create_sheet(name)
        col_of = {}
        for j, (h, src) in enumerate(layout, 1):
            c = ws.cell(row=1, column=j, value=h)
            c.font = HEAD
            c.fill = HELP_HEAD_FILL if h.startswith('_') else HEAD_FILL
            col_of[h] = get_column_letter(j)
        for i, r in enumerate(body, 2):
            for j, (h, src) in enumerate(layout, 1):
                if isinstance(src, int):
                    v = typed(r[src], h)
                    if v != '':
                        ws.cell(row=i, column=j, value=v)
                else:
                    lookup, k = src
                    if r[k]:
                        c = ws.cell(row=i, column=j, value=labels[lookup].get(r[k], '?'))
                        c.fill = HELP_FILL
        n_rows = len(body) + 1
        last = max(MAXROW, n_rows + 5000)     # dropdowns reach well past the data
        # dropdowns
        dd = {**{k: v for k, v in COMMON.items() if k in header}, **DROPDOWNS.get(name, {})}
        if name.startswith('vocab_') and 'parent' in header:
            dd['parent'] = (name, 1)
        for colname, (lst, strict) in dd.items():
            L = col_of[colname]
            if lst == 'BY_ATTRIBUTE':
                formula = f'INDIRECT(${col_of["attribute"]}2)'
            elif lst == name:      # vocab parent -> same sheet
                formula = f"'{name}'!$A$2:$A${MAXROW}"
            else:
                formula = f'list_{lst}'
            dv = DataValidation(type='list', formula1=formula, allow_blank=True,
                                errorStyle='stop' if strict else 'warning', showErrorMessage=True,
                                errorTitle='Not in the list', error=f'Use a value from the dropdown ({lst}).')
            dv.add(f'{L}2:{L}{last}')
            ws.add_data_validation(dv)
        # cosmetics
        ws.freeze_panes = 'B2'
        ws.auto_filter.ref = f'A1:{get_column_letter(len(layout))}{max(n_rows, 2)}'
        for j, (h, src) in enumerate(layout, 1):
            sample = [len(str(r[src])) for r in body[:300] if isinstance(src, int) and src < len(r)]
            width = 36 if h.startswith('_') else (max([len(h)] + sample) if sample else len(h) + 2)
            ws.column_dimensions[get_column_letter(j)].width = min(max(width + 2, 8), 60)
    os.makedirs(os.path.dirname(os.path.join(a.repo, a.out)), exist_ok=True)
    wb.save(os.path.join(a.repo, a.out))
    print(f'Wrote {a.out}: {len(paths)} table sheets + _about, _lists (no formulas)')

if __name__ == '__main__':
    main()
