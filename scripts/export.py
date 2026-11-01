"""Export the editing workbook to the canonical CSVs (schema v1.1), then run the validator.

Usage (from the repo root):
    pip install openpyxl
    python scripts/export.py                      # workbook/historical_polities.xlsx -> data/*.csv, vocab/*.csv
    python scripts/export.py --no-validate        # skip the validator run
    python scripts/export.py --refresh            # after a clean export, rebuild the workbook (fresh grey labels)
Rules:
  - Sheets whose name starts with "_" and columns whose header starts with "_" are helpers: not exported.
  - Sheet "<table>" -> data/<table>.csv; sheet "vocab_<name>" -> vocab/<name>.csv.
  - Cells are trimmed; numbers are written without trailing ".0"; TRUE/FALSE -> true/false.
  - Rows are sorted by primary key, so diffs stay small. Completely empty rows are dropped.
"""
import argparse, csv, os, subprocess, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import SPEC            # single source of truth for files and column order

WORKBOOK = 'workbook/historical_polities.xlsx'
NUMERIC = {'start', 'end', 'span_no', 'area_kkm2', 'area_year', 'population_m', 'population_year',
           'legacy_score', 'sort', 'lat', 'lon'}
ATTR_ORDER = {'ethnic_group': 0, 'language': 1, 'religion': 2, 'capital': 3, 'government_type': 4}

def _int(v):
    try:
        return int(v)
    except ValueError:
        return 0

SORT = {  # CSV path -> key(row)
    'data/polities.csv': lambda r: r['polity_id'],
    'data/spans.csv': lambda r: (r['polity_id'], _int(r['span_no'])),
    'data/polity_names.csv': lambda r: (r['polity_id'], r['name_type'], r['start'], r['name_en'], r['name_zh']),
    'data/lineages.csv': lambda r: r['lineage_id'],
    'data/relations.csv': lambda r: (r['from_id'], r['to_id'], r['type'], r['start']),
    'data/polity_attributes.csv': lambda r: (r['polity_id'], ATTR_ORDER.get(r['attribute'], 9), r['value_id'], r['role'], r['start']),
    'data/measures.csv': lambda r: r['scope_id'],
    'data/phases.csv': lambda r: r['phase_id'],
    'data/ratings.csv': lambda r: r['scope_id'],
    'data/rulers.csv': lambda r: r['ruler_id'],
    'data/sources.csv': lambda r: r['source_id'],
    'data/retired_ids.csv': lambda r: r['id'],
    'vocab/enums.csv': lambda r: (r['field'], _int(r['sort'])),
}

def sheet_name(path):
    folder, name = path.split('/')
    name = name[:-4]
    return name if folder == 'data' else f'vocab_{name}'

def cell_text(v, col):
    if v is None:
        return ''
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else repr(v)
    if isinstance(v, int):
        return str(v)
    s = unicodedata.normalize('NFC', str(v)).strip()
    if s.upper() in ('TRUE', 'FALSE') and col in ('is_primary', 'is_acting', 'is_current'):
        s = s.lower()
    return s

def export(workbook, repo):
    from openpyxl import load_workbook
    wb = load_workbook(os.path.join(repo, workbook), read_only=True, data_only=True)
    missing = []
    for path, cols in SPEC.items():
        name = sheet_name(path)
        if name not in wb.sheetnames:
            missing.append(name)
            continue
        ws = wb[name]
        rows_iter = ws.iter_rows(values_only=True)
        header = [str(h).strip() if h is not None else '' for h in next(rows_iter, [])]
        keep = [(i, h) for i, h in enumerate(header) if h and not h.startswith('_')]
        want = [c for c, _ in cols]
        if [h for _, h in keep] != want:
            print(f'  ! {name}: columns {[h for _, h in keep]} differ from schema {want}; exported as found, the validator will report it')
        rows = []
        for raw in rows_iter:
            r = {h: cell_text(raw[i] if i < len(raw) else None, h) for i, h in keep}
            if any(r.values()):
                rows.append(r)
        if path in SORT:
            rows.sort(key=SORT[path])
        elif 'id' in [h for _, h in keep]:
            rows.sort(key=lambda r: r['id'])
        out = os.path.join(repo, path)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=[h for _, h in keep], lineterminator='\n')
            w.writeheader()
            w.writerows(rows)
        print(f'  {path:<32} {len(rows):>6} rows')
    if missing:
        print(f'  ! sheets missing from the workbook (CSVs left unchanged): {missing}')
    wb.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--workbook', default=WORKBOOK)
    ap.add_argument('--no-validate', action='store_true')
    ap.add_argument('--refresh', action='store_true', help='rebuild the workbook from the CSVs after an export with 0 errors')
    a = ap.parse_args()
    print(f'Exporting {a.workbook} …')
    export(a.workbook, a.repo)
    if not a.no_validate:
        print()
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'validate.py'),
                            '--repo', a.repo])
        if a.refresh:
            if r.returncode == 0:
                print('\nRebuilding the workbook with fresh labels … (close it in Excel first)')
                subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_workbook.py'),
                                '--repo', a.repo, '--out', a.workbook], check=True)
            else:
                print('\nWorkbook not rebuilt: fix the errors above first.')
        sys.exit(r.returncode)

if __name__ == '__main__':
    main()
