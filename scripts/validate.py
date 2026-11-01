"""Validator for the Historical Polities v2 data (schema v1.1, §4 checks V1–V16).

Standard library only, so it runs anywhere (locally and in GitHub Actions).
Usage:  python scripts/validate.py [--repo .] [--max 20] [--strict]
Exit code 1 if there are errors (or warnings with --strict).
"""
import argparse, csv, collections, datetime, os, re, sys

# ---------------------------------------------------------------- specification
REQ, OPT = True, False
SPEC = {  # file -> [(column, required)]
    'data/polities.csv': [('polity_id', REQ), ('name_en', REQ), ('name_zh', REQ), ('qualifier_en', OPT), ('qualifier_zh', OPT),
        ('lineage_id', OPT), ('region_id', REQ), ('region2_id', OPT), ('present_day_codes', REQ), ('founder_en', OPT),
        ('founder_zh', OPT), ('evidence_tier', REQ), ('note_en', OPT), ('note_zh', OPT)],
    'data/spans.csv': [('polity_id', REQ), ('span_no', REQ), ('start', REQ), ('end', OPT), ('start_precision', OPT),
        ('end_precision', OPT), ('certainty', OPT), ('source', OPT), ('note_en', OPT), ('note_zh', OPT)],
    'data/polity_names.csv': [('polity_id', REQ), ('name_type', REQ), ('name_en', OPT), ('name_zh', OPT), ('start', OPT),
        ('end', OPT), ('source', OPT), ('note_en', OPT), ('note_zh', OPT)],
    'data/lineages.csv': [('lineage_id', REQ), ('name_en', REQ), ('name_zh', REQ), ('note_en', OPT), ('note_zh', OPT)],
    'data/relations.csv': [('from_id', REQ), ('to_id', REQ), ('type', REQ), ('start', OPT), ('end', OPT), ('certainty', OPT),
        ('source', OPT), ('note_en', OPT), ('note_zh', OPT)],
    'data/polity_attributes.csv': [('polity_id', REQ), ('attribute', REQ), ('value_id', REQ), ('role', OPT), ('start', OPT),
        ('end', OPT), ('is_primary', REQ), ('certainty', OPT), ('source', OPT), ('note_en', OPT), ('note_zh', OPT)],
    'data/measures.csv': [('scope_id', REQ), ('area_kkm2', OPT), ('area_year', OPT), ('population_m', OPT),
        ('population_year', OPT), ('certainty', OPT), ('source', OPT), ('note_en', OPT), ('note_zh', OPT)],
    'data/phases.csv': [('phase_id', REQ), ('polity_id', REQ), ('name_en', REQ), ('name_zh', OPT), ('start', REQ), ('end', OPT),
        ('note_en', OPT), ('note_zh', OPT), ('legacy_score', OPT)],
    'data/ratings.csv': [('scope_id', REQ)] + [(d, REQ) for d in ('dur', 'area', 'pop', 'econ', 'mil', 'cult', 'tech', 'gov', 'soc')]
        + [(f'{d}_why_{l}', OPT) for d in ('dur', 'area', 'pop', 'econ', 'mil', 'cult', 'tech', 'gov', 'soc') for l in ('en', 'zh')]
        + [('method', REQ), ('rubric_version', REQ), ('prompt_version', OPT), ('rated_on', OPT), ('note_en', OPT), ('note_zh', OPT)],
    'data/rulers.csv': [('ruler_id', REQ), ('polity_id', REQ), ('role', REQ), ('title_id', REQ), ('name_en', REQ), ('name_zh', REQ),
        ('start', OPT), ('end', OPT), ('start_precision', OPT), ('end_precision', OPT), ('is_acting', REQ), ('certainty', OPT),
        ('source', OPT), ('note_en', OPT), ('note_zh', OPT)],
    'data/sources.csv': [('source_id', REQ), ('citation', REQ), ('url', OPT), ('accessed', OPT), ('note', OPT)],
    'data/retired_ids.csv': [('id', REQ), ('replaced_by', OPT), ('reason_en', OPT), ('reason_zh', OPT), ('session', OPT)],
}
VBASE = [('id', REQ), ('en', REQ), ('zh', REQ), ('parent', OPT), ('note_en', OPT), ('note_zh', OPT)]
VOCAB = {  # file -> (id prefix, extra columns)
    'regions': ('reg.', [('sort', OPT)]),
    'countries': ('', [('is_current', REQ)]),
    'ethnic_groups': ('eth.', []), 'languages': ('lang.', []), 'religions': ('rel.', []),
    'places': ('place.', [('modern_en', OPT), ('modern_zh', OPT), ('country', OPT), ('lat', OPT), ('lon', OPT)]),
    'government_types': ('gov.', [('roles', REQ), ('definition_en', OPT), ('definition_zh', OPT)]),
    'titles': ('title.', [('gender', REQ), ('rank_note', OPT)]),
}
for f, (_, extra) in VOCAB.items():
    # countries keep is_current before the notes; other vocabularies append their extra columns
    SPEC[f'vocab/{f}.csv'] = VBASE[:4] + extra + VBASE[4:] if f == 'countries' else VBASE + extra
SPEC['vocab/enums.csv'] = [('field', REQ), ('value', REQ), ('en', REQ), ('zh', REQ), ('sort', OPT)]

ENUM = {
    'precision': {'exact', 'circa', 'decade', 'century'},
    'certainty': {'certain', 'probable', 'disputed'},
    'evidence_tier': {'A', 'B', 'C'},
    'name_type': {'official', 'conventional', 'historiographic', 'alternative'},
    'relation_type': {'succeeded_by', 'restoration_of', 'split_from', 'merged_into', 'vassal_of', 'member_of', 'claims_succession_of'},
    'attribute': {'ethnic_group', 'language', 'religion', 'capital', 'government_type'},
    'ruler_role': {'monarch', 'head_of_state', 'head_of_government', 'party_leader', 'governor_general', 'regent',
                   'rival_claimant', 'effective_ruler'},
    'rating_method': {'legacy', 'manual', 'ai_assisted'},
    'gender': {'m', 'f', 'n'},
    'bool': {'true', 'false'},
}
ATTR_VOCAB = {'ethnic_group': 'ethnic_groups', 'language': 'languages', 'religion': 'religions', 'capital': 'places',
              'government_type': 'government_types'}
ATTR_ROLES = {'ethnic_group': {'ruling', 'majority'}, 'language': {'official', 'majority'},
              'religion': {'official', 'ruling', 'majority'}, 'capital': {'seat', 'secondary', 'symbolic'}, 'government_type': {''}}
DIMS = ('dur', 'area', 'pop', 'econ', 'mil', 'cult', 'tech', 'gov', 'soc')
GRADES = {'S', 'A', 'B', 'C', 'D'}
DUR_T, AREA_T, POP_T = (500, 200, 100, 50), (1e7, 3e6, 1e6, 1e5), (1e8, 3e7, 1e7, 3e6)
WINDOW = {'': 0, 'exact': 0, 'circa': 10, 'decade': 9, 'century': 99}   # §6.1 (proposed), years of possible shift
RE_ID = {'polity': re.compile(r'P\d{5}$'), 'phase': re.compile(r'P\d{5}-\d{2}$'), 'ruler': re.compile(r'R\d{6}$'),
         'lineage': re.compile(r'L\d{4}$'), 'iso3': re.compile(r'[A-Z]{3}$')}
SLUG = re.compile(r'[a-z0-9_.]+$')

# ---------------------------------------------------------------- helpers
class Report:
    def __init__(self):
        self.items = collections.defaultdict(list)     # (check, level) -> messages
    def err(self, check, msg):
        self.items[(check, 'error')].append(msg)
    def warn(self, check, msg):
        self.items[(check, 'warning')].append(msg)
    def count(self, level):
        return sum(len(v) for (c, l), v in self.items.items() if l == level)

def grade(v, t):
    for g, x in zip('SABC', t):
        if v >= x:
            return g
    return 'D'

def era_years(a, b):
    """Inclusive count of years from a to b, historical numbering (no year 0)."""
    return b - a + 1 - (1 if a < 0 < b else 0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--max', type=int, default=20, help='messages shown per check')
    ap.add_argument('--strict', action='store_true', help='treat warnings as errors')
    a = ap.parse_args()
    R = Report()
    today = datetime.date.today().year
    T = {}

    # ---------- V1: files, headers, required cells ----------
    for f, cols in SPEC.items():
        path = os.path.join(a.repo, f)
        if not os.path.exists(path):
            R.err('V1', f'{f}: file missing'); T[f] = []; continue
        with open(path, encoding='utf-8', newline='') as fh:
            raw = fh.read()
        if raw.startswith('﻿'):
            R.err('V1', f'{f}: has a BOM (must be UTF-8 without BOM)')
        if '\r\n' in raw:
            R.err('V1', f'{f}: CRLF line endings (must be LF)')
        rows = list(csv.DictReader(raw.lstrip('﻿').splitlines()))
        header = next(csv.reader([raw.lstrip('﻿').splitlines()[0]])) if raw.strip() else []
        want = [c for c, _ in cols]
        if header != want:
            R.err('V1', f'{f}: header {header} != expected {want}')
        for i, r in enumerate(rows, start=2):
            for c, req in cols:
                v = r.get(c) or ''
                if v != v.strip() or '  ' in v:
                    R.err('V1', f'{f}:{i} {c}: stray whitespace')
                if req and not v.strip():
                    R.err('V1', f'{f}:{i} {c}: required value missing')
            if None in r:
                R.err('V1', f'{f}:{i}: more cells than header columns')
        T[f] = rows
    D = lambda n: T[f'data/{n}.csv']
    Vv = lambda n: T[f'vocab/{n}.csv']

    # ---------- V2: keys and ID formats ----------
    def unique(f, keyf, label):
        seen = {}
        for i, r in enumerate(T[f], start=2):
            k = keyf(r)
            if k in seen:
                R.err('V2', f'{f}:{i} duplicate {label} {k} (also row {seen[k]})')
            seen[k] = i
    unique('data/polities.csv', lambda r: r['polity_id'], 'polity_id')
    unique('data/spans.csv', lambda r: (r['polity_id'], r['span_no']), 'span')
    unique('data/phases.csv', lambda r: r['phase_id'], 'phase_id')
    unique('data/rulers.csv', lambda r: r['ruler_id'], 'ruler_id')
    unique('data/measures.csv', lambda r: r['scope_id'], 'scope_id')
    unique('data/ratings.csv', lambda r: r['scope_id'], 'scope_id')
    unique('data/lineages.csv', lambda r: r['lineage_id'], 'lineage_id')
    unique('data/sources.csv', lambda r: r['source_id'], 'source_id')
    unique('data/retired_ids.csv', lambda r: r['id'], 'id')
    unique('data/polity_attributes.csv', lambda r: (r['polity_id'], r['attribute'], r['value_id'], r['role'], r['start']), 'attribute row')
    unique('data/polity_names.csv', lambda r: (r['polity_id'], r['name_type'], r['name_en'], r['name_zh'], r['start']), 'name row')
    unique('data/relations.csv', lambda r: (r['from_id'], r['to_id'], r['type'], r['start']), 'relation')
    unique('vocab/enums.csv', lambda r: (r['field'], r['value']), 'enum value')
    vocab_ids = {}
    for vf, (prefix, _) in VOCAB.items():
        unique(f'vocab/{vf}.csv', lambda r: r['id'], 'id')
        for i, t in enumerate(Vv(vf), start=2):
            ok = RE_ID['iso3'].match(t['id']) if vf == 'countries' else (t['id'].startswith(prefix) and SLUG.match(t['id']))
            if not ok:
                R.err('V2', f'vocab/{vf}.csv:{i} bad id {t["id"]!r}')
        vocab_ids[vf] = {t['id'] for t in Vv(vf)}
    for f, col, kind in (('data/polities.csv', 'polity_id', 'polity'), ('data/phases.csv', 'phase_id', 'phase'),
                         ('data/rulers.csv', 'ruler_id', 'ruler'), ('data/lineages.csv', 'lineage_id', 'lineage')):
        for i, r in enumerate(T[f], start=2):
            if r[col] and not RE_ID[kind].match(r[col]):
                R.err('V2', f'{f}:{i} bad {col} {r[col]!r}')

    pol = {r['polity_id']: r for r in D('polities')}
    phase_by_id = {r['phase_id']: r for r in D('phases')}
    sources = {r['source_id'] for r in D('sources')}
    lineages = {r['lineage_id'] for r in D('lineages')}

    # ---------- V3: foreign keys ----------
    def fk(f, i, col, val, pool, what):
        if val and val not in pool:
            R.err('V3', f'{f}:{i} {col} {val!r} not found in {what}')
    for i, r in enumerate(D('polities'), start=2):
        f = 'data/polities.csv'
        fk(f, i, 'region_id', r['region_id'], vocab_ids['regions'], 'regions')
        fk(f, i, 'region2_id', r['region2_id'], vocab_ids['regions'], 'regions')
        fk(f, i, 'lineage_id', r['lineage_id'], lineages, 'lineages')
        for c in r['present_day_codes'].split(';') if r['present_day_codes'] else []:
            fk(f, i, 'present_day_codes', c, vocab_ids['countries'], 'countries')
    for n in ('spans', 'polity_attributes', 'polity_names', 'phases', 'rulers'):
        for i, r in enumerate(D(n), start=2):
            fk(f'data/{n}.csv', i, 'polity_id', r['polity_id'], pol, 'polities')
    for i, r in enumerate(D('relations'), start=2):
        fk('data/relations.csv', i, 'from_id', r['from_id'], pol, 'polities')
        fk('data/relations.csv', i, 'to_id', r['to_id'], pol, 'polities')
        if r['from_id'] == r['to_id']:
            R.err('V3', f'data/relations.csv:{i} from_id = to_id')
    for i, r in enumerate(D('polity_attributes'), start=2):
        if r['attribute'] in ATTR_VOCAB:
            fk('data/polity_attributes.csv', i, 'value_id', r['value_id'], vocab_ids[ATTR_VOCAB[r['attribute']]], ATTR_VOCAB[r['attribute']])
    for i, r in enumerate(D('rulers'), start=2):
        fk('data/rulers.csv', i, 'title_id', r['title_id'], vocab_ids['titles'], 'titles')
    for n in ('measures', 'ratings'):
        for i, r in enumerate(D(n), start=2):
            if r['scope_id'] not in pol and r['scope_id'] not in phase_by_id:
                R.err('V3', f'data/{n}.csv:{i} scope_id {r["scope_id"]!r} is neither a polity nor a phase')
    for i, r in enumerate(D('phases'), start=2):
        if not r['phase_id'].startswith(r['polity_id'] + '-'):
            R.err('V3', f'data/phases.csv:{i} phase_id {r["phase_id"]} does not belong to {r["polity_id"]}')
    for i, r in enumerate(Vv('places'), start=2):
        fk('vocab/places.csv', i, 'country', r['country'], vocab_ids['countries'], 'countries')
    for vf in VOCAB:
        parents = {t['id']: t['parent'] for t in Vv(vf)}
        for i, t in enumerate(Vv(vf), start=2):
            fk(f'vocab/{vf}.csv', i, 'parent', t['parent'], parents, vf)
            seen, cur = set(), t['id']
            while cur and cur in parents:
                if cur in seen:
                    R.err('V3', f'vocab/{vf}.csv:{i} parent cycle at {t["id"]}'); break
                seen.add(cur); cur = parents[cur]
    for f, cols in SPEC.items():
        if 'source' in dict(cols):
            for i, r in enumerate(T[f], start=2):
                for s in r['source'].split(';') if r['source'] else []:
                    fk(f, i, 'source', s, sources, 'sources')
    for i, r in enumerate(D('retired_ids'), start=2):
        fk('data/retired_ids.csv', i, 'replaced_by', r['replaced_by'], set(pol) | lineages, 'polities/lineages')

    # ---------- V4: enum values ----------
    enums_csv = {(r['field'], r['value']) for r in Vv('enums')}
    def en(f, i, col, val, kind, label_field=None):
        if val and val not in ENUM[kind]:
            R.err('V4', f'{f}:{i} {col} {val!r} not in {sorted(ENUM[kind])}')
        elif val and label_field and (label_field, val) not in enums_csv:
            R.err('V4', f'{f}:{i} {col} {val!r} has no bilingual label in vocab/enums.csv ({label_field})')
    for f, cols in SPEC.items():
        names = dict(cols)
        for i, r in enumerate(T[f], start=2):
            for c in ('start_precision', 'end_precision'):
                if c in names: en(f, i, c, r[c], 'precision', 'precision')
            if 'certainty' in names: en(f, i, 'certainty', r['certainty'], 'certainty', 'certainty')
    for i, r in enumerate(D('polities'), start=2): en('data/polities.csv', i, 'evidence_tier', r['evidence_tier'], 'evidence_tier', 'evidence_tier')
    for i, r in enumerate(D('polity_names'), start=2): en('data/polity_names.csv', i, 'name_type', r['name_type'], 'name_type', 'name_type')
    for i, r in enumerate(D('relations'), start=2): en('data/relations.csv', i, 'type', r['type'], 'relation_type', 'relation_type')
    for i, r in enumerate(D('rulers'), start=2):
        en('data/rulers.csv', i, 'role', r['role'], 'ruler_role', 'ruler_role')
        en('data/rulers.csv', i, 'is_acting', r['is_acting'], 'bool')
    for i, r in enumerate(D('polity_attributes'), start=2):
        f = 'data/polity_attributes.csv'
        en(f, i, 'attribute', r['attribute'], 'attribute', 'attribute')
        en(f, i, 'is_primary', r['is_primary'], 'bool')
        if r['attribute'] in ATTR_ROLES and r['role'] not in ATTR_ROLES[r['attribute']]:
            R.err('V4', f'{f}:{i} role {r["role"]!r} not allowed for {r["attribute"]}')
        elif r['role'] and ('attribute_role', r['role']) not in enums_csv:
            R.err('V4', f'{f}:{i} role {r["role"]!r} has no bilingual label in vocab/enums.csv')
    for i, r in enumerate(D('ratings'), start=2):
        en('data/ratings.csv', i, 'method', r['method'], 'rating_method', 'rating_method')
        for d in DIMS:
            if r[d] and r[d] not in GRADES:
                R.err('V4', f'data/ratings.csv:{i} {d} {r[d]!r} is not a grade S–D')
    for i, t in enumerate(Vv('titles'), start=2): en('vocab/titles.csv', i, 'gender', t['gender'], 'gender', 'gender')
    for i, t in enumerate(Vv('countries'), start=2): en('vocab/countries.csv', i, 'is_current', t['is_current'], 'bool')
    for i, t in enumerate(Vv('government_types'), start=2):
        for ro in t['roles'].split(';'):
            if ro not in ENUM['ruler_role']:
                R.err('V4', f'vocab/government_types.csv:{i} unknown role {ro!r}')
    title_gender = {t['id']: t['gender'] for t in Vv('titles')}
    for i, r in enumerate(D('rulers'), start=2):
        if r['role'] in ('head_of_state', 'head_of_government', 'party_leader', 'governor_general') and title_gender.get(r['title_id']) not in ('n', None):
            R.warn('V4', f'data/rulers.csv:{i} {r["ruler_id"]}: gendered title {r["title_id"]} for role {r["role"]} (A.4)')

    # ---------- V5: years ----------
    def yr(f, i, col, v):
        if v == '':
            return None
        if not re.fullmatch(r'-?\d+', v):
            R.err('V5', f'{f}:{i} {col} {v!r} is not an integer year'); return None
        y = int(v)
        if y == 0:
            R.err('V5', f'{f}:{i} {col} is 0 (no year 0)')
        if y > today:
            R.err('V5', f'{f}:{i} {col} {y} is in the future')
        return y
    for f, cols in SPEC.items():
        names = dict(cols)
        if 'start' in names and 'end' in names:
            for i, r in enumerate(T[f], start=2):
                s, e = yr(f, i, 'start', r['start']), yr(f, i, 'end', r['end'])
                if s is not None and e is not None and s > e:
                    R.err('V5', f'{f}:{i} start {s} > end {e}')
        for c in ('area_year', 'population_year'):
            if c in names:
                for i, r in enumerate(T[f], start=2):
                    yr(f, i, c, r[c])
    for i, r in enumerate(D('rulers'), start=2):
        if not r['start'] and not r['end']:
            R.err('V5', f'data/rulers.csv:{i} both start and end missing (A.2)')
    for i, r in enumerate(D('measures'), start=2):
        for c in ('area_kkm2', 'population_m'):
            if r[c] and not re.fullmatch(r'\d+(\.\d+)?', r[c]):
                R.err('V5', f'data/measures.csv:{i} {c} {r[c]!r} is not a non-negative number')

    # spans per polity
    spans = collections.defaultdict(list)
    for r in D('spans'):
        try:
            spans[r['polity_id']].append((int(r['span_no']), int(r['start']), int(r['end']) if r['end'] else None, r))
        except ValueError:
            pass
    open_end = lambda e: today if e is None else e

    # ---------- V6: spans ----------
    for pid in pol:
        sp = sorted(spans.get(pid, []))
        if not sp:
            R.err('V6', f'{pid}: no span'); continue
        if [x[0] for x in sp] != list(range(1, len(sp) + 1)):
            R.err('V6', f'{pid}: span_no not 1..n')
        for (n1, s1, e1, _), (n2, s2, e2, _) in zip(sp, sp[1:]):
            if e1 is None:
                R.err('V6', f'{pid}: span {n1} is open-ended but is not the last span')
            elif s2 <= e1:
                R.err('V6', f'{pid}: span {n2} starts before span {n1} ends')
            elif era_years(e1, s2) - 2 > 25:
                R.err('V6', f'{pid}: gap of {era_years(e1, s2) - 2} years between spans {n1} and {n2} (> 25, §3.3)')

    # ---------- V7: phases tile spans ----------
    phases = collections.defaultdict(list)
    for r in D('phases'):
        try:
            phases[r['polity_id']].append((int(r['start']), int(r['end']) if r['end'] else None, r['phase_id']))
        except ValueError:
            pass
    nxt = lambda y: 1 if y == -1 else y + 1
    for pid in pol:
        sp = sorted(spans.get(pid, []))
        ph = sorted(phases.get(pid, []), key=lambda x: (x[0], open_end(x[1])))
        if not ph:
            R.err('V7', f'{pid}: no phases'); continue
        if not sp:
            continue
        # walk spans and phases together
        k = 0
        for n, s, e, _ in sp:
            cursor = s
            while k < len(ph) and ph[k][0] <= open_end(e):
                ps, pe, phid = ph[k]
                if ps != cursor:
                    R.err('V7', f'{phid}: starts {ps}, expected {cursor} (gap or overlap)')
                if pe is None and e is not None:
                    R.err('V7', f'{phid}: open-ended but span {n} ends {e}')
                if pe is not None and pe > open_end(e):
                    R.err('V7', f'{phid}: ends {pe}, after span {n} ends {e}')
                cursor = nxt(pe) if pe is not None else None
                k += 1
                if cursor is None:
                    break
            if e is None:
                if cursor is not None:
                    R.err('V7', f'{pid}: last phase must be open-ended like its span')
            elif cursor != nxt(e):
                R.err('V7', f'{pid}: phases do not reach the end of span {n} ({e})')
        for ps, pe, phid in ph[k:]:
            R.err('V7', f'{phid}: outside every span')

    # ---------- V8: one primary per (polity, attribute) ----------
    prim = collections.defaultdict(int); present = set()
    for r in D('polity_attributes'):
        present.add((r['polity_id'], r['attribute']))
        prim[(r['polity_id'], r['attribute'])] += r['is_primary'] == 'true'
    for k in present:
        if prim[k] != 1:
            R.err('V8', f'{k[0]} {k[1]}: {prim[k]} primary rows (need exactly 1)')

    # ---------- V9: unique labels ----------
    for lang, fmt in (('en', '{} ({})'), ('zh', '{}（{}）')):
        seen = {}
        for r in D('polities'):
            lab = fmt.format(r['name_' + lang], r['qualifier_' + lang]) if r['qualifier_' + lang] else r['name_' + lang]
            if lab in seen:
                R.err('V9', f'{lang} label {lab!r} used by {seen[lab]} and {r["polity_id"]}')
            seen[lab] = r['polity_id']

    # ---------- V10: dates inside spans ----------
    def inside(pid, s, e):
        sp = spans.get(pid)
        if not sp:
            return 'whole'
        s = s if s is not None else sp[0][1]
        e = open_end(e)
        rng = [(a_, open_end(b_)) for _, a_, b_, _ in sp]
        if any(a_ <= s and e <= b_ for a_, b_ in rng):
            return 'inside'
        if any(not (e < a_ or s > b_) for a_, b_ in rng):
            return 'partly'
        return 'outside'
    for n, idc in (('rulers', 'ruler_id'), ('polity_attributes', None), ('polity_names', None)):
        for i, r in enumerate(D(n), start=2):
            if not r['start'] and not r['end']:
                continue
            try:
                s = int(r['start']) if r['start'] else None
                e = int(r['end']) if r['end'] else None
            except ValueError:
                continue
            where = inside(r['polity_id'], s, e)
            if where in ('partly', 'outside'):
                R.warn('V10', f'data/{n}.csv:{i} {r.get(idc) or r["polity_id"]} {r["start"]}–{r["end"] or "present"} {where} the spans of {r["polity_id"]}')
            if n == 'rulers' and e is None and r['end'] == '' and spans.get(r['polity_id']) and sorted(spans[r['polity_id']])[-1][2] is not None:
                R.err('V5', f'data/rulers.csv:{i} {r["ruler_id"]}: open end (present) but polity {r["polity_id"]} has ended')
    for i, r in enumerate(D('relations'), start=2):
        if r['start']:
            for side in ('from_id', 'to_id'):
                if r[side] in pol and inside(r[side], int(r['start']), int(r['end']) if r['end'] else int(r['start'])) == 'outside':
                    R.warn('V10', f'data/relations.csv:{i} {r["type"]} {r["start"]}–{r["end"]} outside the spans of {r[side]}')

    # ---------- V11: retired IDs ----------
    retired = {r['id'] for r in D('retired_ids')}
    for f, cols in SPEC.items():
        if not f.startswith('data/') or f == 'data/retired_ids.csv':
            continue
        for i, r in enumerate(T[f], start=2):
            for c in ('polity_id', 'from_id', 'to_id', 'scope_id', 'lineage_id'):
                if c in r and (r[c] in retired or r[c][:6] in retired):
                    R.err('V11', f'{f}:{i} uses retired ID {r[c]}')

    # ---------- V12: unused vocabulary ----------
    used = collections.defaultdict(set)
    for r in D('polities'):
        used['regions'] |= {r['region_id'], r['region2_id']}
        used['countries'] |= set(r['present_day_codes'].split(';'))
    for r in D('polity_attributes'):
        used[ATTR_VOCAB.get(r['attribute'], '')].add(r['value_id'])
    for r in D('rulers'):
        used['titles'].add(r['title_id'])
    for t in Vv('places'):
        used['countries'].add(t['country'])
    for vf in VOCAB:
        if vf == 'government_types':
            continue        # seeded from Appendix B before use
        parents = {t['parent'] for t in Vv(vf)}
        for t in Vv(vf):
            if t['id'] not in used[vf] and t['id'] not in parents:
                R.warn('V12', f'vocab/{vf}.csv: {t["id"]} is not used')

    # ---------- V13: AI-assisted ratings need a prompt version ----------
    for i, r in enumerate(D('ratings'), start=2):
        if r['method'] == 'ai_assisted' and not r['prompt_version']:
            R.err('V13', f'data/ratings.csv:{i} ai_assisted rating without prompt_version')

    # ---------- V14: missing Chinese ----------
    EXEMPT = {('data/phases.csv', 'name'), ('data/phases.csv', 'note'),   # until Stage 3
              ('data/polities.csv', 'qualifier')}                          # a qualifier may exist in one language only
    for f, cols in SPEC.items():
        names = [c for c, _ in cols]
        pairs = [c[:-3] for c in names if c.endswith('_en') and c[:-3] + '_zh' in names]
        for base in pairs:
            if (f, base) in EXEMPT:
                continue
            for i, r in enumerate(T[f], start=2):
                if r[base + '_en'] and not r[base + '_zh']:
                    R.warn('V14', f'{f}:{i} {base}_zh missing')

    # ---------- V15 / V16: quantitative grades ----------
    meas = {r['scope_id']: r for r in D('measures')}
    def age_at(pid, end_year):
        tot = 0
        for _, s, e, _ in sorted(spans.get(pid, [])):
            e = open_end(e)
            if s > end_year:
                break
            tot += era_years(s, min(e, end_year)) - 1    # durations: end - start (legacy convention, era-corrected)
        return tot
    span_prec = {}
    for pid, sp in spans.items():
        sp = sorted(sp)
        span_prec[pid] = (sp[0][3]['start_precision'], sp[-1][3]['end_precision'])
    for i, r in enumerate(D('ratings'), start=2):
        sid = r['scope_id']
        if sid in pol:
            pid, end_year = sid, open_end(sorted(spans.get(sid, [(0, 0, 0, {})]))[-1][2]) if spans.get(sid) else None
        elif sid in phase_by_id:
            ph = phase_by_id[sid]; pid = ph['polity_id']
            end_year = open_end(int(ph['end'])) if ph['end'] else (open_end(sorted(spans[pid])[-1][2]) if spans.get(pid) else None)
        else:
            continue
        if end_year is None or not spans.get(pid):
            continue
        age = age_at(pid, end_year)
        g = grade(age, DUR_T)
        if r['dur'] in GRADES and r['dur'] != g:
            R.err('V15', f'data/ratings.csv:{i} {sid}: dur {r["dur"]} but age {age} years → {g}')
        # V16 borderline
        ps, pe = span_prec.get(pid, ('', ''))
        w = WINDOW.get(ps or '', 0) + (WINDOW.get(pe or '', 0) if sid in pol else 0)
        if w and {grade(age - w, DUR_T), grade(age + w, DUR_T)} != {g}:
            R.warn('V16', f'{sid}: duration {age} ± {w} years could change the grade ({grade(age - w, DUR_T)}–{grade(age + w, DUR_T)}); review by hand')
        m = meas.get(sid)
        if m:
            if m['area_kkm2'] and r['area'] in GRADES and grade(float(m['area_kkm2']) * 1e3, AREA_T) != r['area']:
                R.err('V15', f'data/ratings.csv:{i} {sid}: area {r["area"]} but {m["area_kkm2"]} thousand km² → {grade(float(m["area_kkm2"]) * 1e3, AREA_T)}')
            if m['population_m'] and r['pop'] in GRADES and grade(float(m['population_m']) * 1e6, POP_T) != r['pop']:
                R.err('V15', f'data/ratings.csv:{i} {sid}: pop {r["pop"]} but {m["population_m"]} million → {grade(float(m["population_m"]) * 1e6, POP_T)}')

    # ---------- report ----------
    checks = sorted({c for c, _ in R.items}, key=lambda c: int(c[1:]))
    print(f'Historical Polities v2 validator · {len(pol)} polities, {len(D("phases"))} phases, {len(D("rulers"))} rulers · present = {today}')
    for c in ['V%d' % n for n in range(1, 17)]:
        e, w = R.items.get((c, 'error'), []), R.items.get((c, 'warning'), [])
        status = 'FAIL' if e else ('warn' if w else 'ok')
        print(f'{c:>4} {status:<4} errors {len(e):>5}  warnings {len(w):>5}')
        for m in (e + w)[:a.max]:
            print(f'       - {m}')
        if len(e + w) > a.max:
            print(f'       … {len(e + w) - a.max} more')
    ne, nw = R.count('error'), R.count('warning')
    print(f'Total: {ne} errors, {nw} warnings')
    sys.exit(1 if ne or (a.strict and nw) else 0)

if __name__ == '__main__':
    main()
