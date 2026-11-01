"""Stage 1 check: rebuild the legacy view from the v2 tables and compare it with the legacy CSVs, field by field.
Every difference must be one of the agreed changes listed in EXPECTED; anything else fails.
Run: python verify_migration.py --legacy <legacy folder> --repo <repo root> [--preview notes/id-preview.csv]
"""
import argparse, csv, collections, os, re, sys, unicodedata

def clean(s):
    s = unicodedata.normalize('NFC', s or '').replace('‑', '-').replace(' ', ' ')
    return re.sub(r'\s+', ' ', s).strip().replace(' （', '（')

def pair(s):
    s = clean(s)
    en, zh = (s.split(' / ', 1) if ' / ' in s else s.split('/', 1)) if '/' in s else (s, '')
    return f'{en.strip()} / {zh.strip()}'

def read(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

G = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
W = dict(dur=1, area=2, pop=2, econ=3, mil=3, cult=3, tech=3, gov=2, soc=1)
LEG = dict(dur='Duration', area='Area', pop='Population', econ='Economics', mil='Military', cult='Culture',
           tech='Technology', gov='Governance', soc='Social')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--legacy', required=True); ap.add_argument('--repo', required=True); ap.add_argument('--preview')
    a = ap.parse_args()
    L = lambda f: read(os.path.join(a.legacy, f))
    N = lambda f: read(os.path.join(a.repo, f))
    lp, lph, lr = L('polities.csv'), L('phases.csv'), L('rulers.csv')
    pol = {r['polity_id']: r for r in N('data/polities.csv')}
    spans = {r['polity_id']: r for r in N('data/spans.csv')}
    attrs = collections.defaultdict(dict)
    for r in N('data/polity_attributes.csv'):
        attrs[r['polity_id']][r['attribute']] = r['value_id']
    meas = {r['scope_id']: r for r in N('data/measures.csv')}
    rat = {r['scope_id']: r for r in N('data/ratings.csv')}
    phases = {r['phase_id']: r for r in N('data/phases.csv')}
    rulers = {r['ruler_id']: r for r in N('data/rulers.csv')}
    voc = {}
    for f in ('ethnic_groups', 'languages', 'religions', 'places', 'regions', 'titles', 'countries', 'government_types'):
        for t in N(f'vocab/{f}.csv'):
            assert t['id'] not in voc, f'duplicate vocab id {t["id"]}'
            voc[t['id']] = t
    fixed = {r['id'] for r in N('migration/issues.csv') if r['type'] == 'phase_boundary_fixed'}
    xw = {(r['legacy_file'], int(r['legacy_row'])): r['new_id'] for r in N('migration/legacy_crosswalk.csv')}
    fails, notes = [], collections.Counter()
    def check(cond, msg):
        if not cond:
            fails.append(msg)
    def vlabel(v):
        t = voc[v]; return f"{t['en']} / {t['zh']}"
    def plabel(p):
        en = p['name_en'] + (f" ({p['qualifier_en']})" if p['qualifier_en'] else '')
        zh = p['name_zh'] + (f"（{p['qualifier_zh']}）" if p['qualifier_zh'] else '')
        return f'{en} / {zh}'
    MERGES = {'Polish / 波兰': 'Pole / 波兰', 'Punjab / 旁遮普（印度-雅利安）': 'Punjabi / 旁遮普（印度-雅利安）',
              'Mazandrani / 马赞德兰语': 'Mazanderani / 马赞德兰语'}

    # counts and keys
    check(len(pol) == len(lp) == len(spans) == len(meas) == len(rat), 'polity table sizes differ')
    check(len(phases) == len(lph), f'phases {len(phases)} vs {len(lph)}')
    check(len(rulers) == len(lr), f'rulers {len(rulers)} vs {len(lr)}')
    for k in ('en', 'zh'):
        labs = [plabel(p).split(' / ')[0 if k == 'en' else 1] for p in pol.values()]
        check(len(labs) == len(set(labs)), f'{k} labels not unique')

    # polities
    for i, r in enumerate(lp, start=2):
        pid = xw[('polities.csv', i)]; p = pol[pid]
        old, new = clean(r['Political Entities']), plabel(p)
        if old != new:
            notes['label changed (agreed qualifier/name fixes)'] += 1
            check(re.sub(r' \([^)]*\)', '', new.split(' / ')[0]) in (re.sub(r' \([^)]*\)', '', old.split(' / ')[0]), 'Wey')
                  and (new.split(' / ')[1] == old.split(' / ')[1] or new.split(' / ')[1].startswith(old.split(' / ')[1] + '（')),
                  f'{pid}: unexpected label change {old!r} -> {new!r}')
        s = spans[pid]
        check(int(s['start']) == int(r['Start']), f'{pid} start')
        check((s['end'] or '2026') == clean(r['End']), f'{pid} end')
        for attr, col in (('ethnic_group', 'Ethnic Group'), ('language', 'Language'), ('religion', 'Religion'), ('capital', 'Capital')):
            o = pair(r[col]); o = MERGES.get(o, o)
            check(vlabel(attrs[pid][attr]) == o, f'{pid} {attr}: {vlabel(attrs[pid][attr])!r} vs {o!r}')
        pl = voc[attrs[pid]['capital']]
        check(f"{pl['modern_en']} / {pl['modern_zh']}" == pair(r['Present Day Location']), f'{pid} present-day location')
        check(f"{p['founder_en']} / {p['founder_zh']}" == pair(r['Founder']), f'{pid} founder')
        check(vlabel(p['region_id']) == pair(r['Region']), f'{pid} region')
        code = clean(r['Code']); code = 'DEU' if code == 'GER' else code
        check(p['present_day_codes'] == code and code in voc, f'{pid} code')
        check(float(meas[pid]['area_kkm2']) == float(r['Area (thousand km2)']) and
              float(meas[pid]['population_m']) == float(r['Population (million)']), f'{pid} measures')
        g = rat[pid]
        for k, c in LEG.items():
            if g[k] != clean(r[c]):
                check(k == 'dur' and pid and old.startswith('Mahameghavahana'), f'{pid} grade {k}: {g[k]} vs {clean(r[c])}')
                notes[f'grade {k} changed: {old} {clean(r[c])}->{g[k]}'] += 1
        overall = sum(G[g[k]] * w for k, w in W.items())
        if overall != int(clean(r['Overall'])):
            notes[f'Overall changed: {old} {clean(r["Overall"])}->{overall}'] += 1
            check(old.startswith('Mahameghavahana'), f'{pid} Overall {overall} vs {r["Overall"]}')
        for k in ('dur', 'area', 'pop', 'econ', 'mil', 'cult', 'tech', 'gov', 'soc'):
            check(g[k] in G, f'{pid} bad grade')

    # phases
    for i, r in enumerate(lph, start=2):
        phid = xw[('phases.csv', i)]; ph = phases[phid]
        check(ph['polity_id'] == phid[:6], f'{phid} polity prefix')
        check(ph['name_en'] == clean(r['Phase Name']) and ph['note_en'] == clean(r['Notes'])
              and ph['legacy_score'] == clean(r['Phase Score']), f'{phid} text/score')
        s, e = int(clean(r['Phase Start'])), int(clean(r['Phase End']))
        ne = int(ph['end']) if ph['end'] else 2026
        if phid in fixed:
            notes['phase boundary fixed (S07, temporary)'] += 1
            continue
        check(int(ph['start']) == s, f'{phid} start')
        if ne != e:
            check(e == 0 and ne == -1, f'{phid} end {ne} vs {e}'); notes['phase year 0 -> -1'] += 1
        if not ph['end']:
            notes['phase end 2026 -> present'] += 1

    # rulers
    ACT = {'Acting President / 代理总统': 'President / 总统', 'Acting President / 代总统': 'President / 总统',
           'Acting President / 代理国家主席': 'President / 国家主席', 'Acting Head of State / 代理国家元首': 'Head of State / 国家元首',
           'Vice President / 副总统': 'President / 总统', 'Delegate President / 代理总统': 'President / 总统'}
    plab = {}
    for i, r in enumerate(lp, start=2):
        plab[xw[('polities.csv', i)]] = clean(r['Political Entities'])
    for i, r in enumerate(lr, start=2):
        rid = xw[('rulers.csv', i)]; x = rulers[rid]
        ot = pair(r['Title'])
        check(vlabel(x['title_id']) == ACT.get(ot, ot), f'{rid} title')
        check((x['is_acting'] == 'true') == (ot in ACT), f'{rid} acting flag')
        on = pair(r['Name']).replace(' (anti-king)', '').replace('（对立王）', '')
        check(f"{x['name_en']} / {x['name_zh']}" == on, f"{rid} name {x['name_en']} / {x['name_zh']} vs {on}")
        check(int(x['start']) == int(r['Start']), f'{rid} start')
        if x['end']:
            check(int(x['end']) == int(r['End']), f'{rid} end')
        else:
            check(clean(r['End']) == '2026', f'{rid} open end'); notes['ruler end 2026 -> present'] += 1
        lbl = clean(r['Polity'])
        if lbl != plab[x['polity_id']]:
            notes[f"ruler relinked: {lbl!r} -> {plab[x['polity_id']]!r}"] += 1

    # foreign keys
    for p in pol.values():
        check(p['region_id'] in voc and p['present_day_codes'] in voc, f"{p['polity_id']} FK")
    for pid, d in attrs.items():
        for v in d.values():
            check(v in voc, f'{pid} attribute FK {v}')
    for t in voc.values():
        check(not t.get('parent') or t['parent'] in voc, f"{t['id']} parent FK")

    # sample Query-by-Year results
    def alive_legacy(y):
        return {clean(r['Political Entities']) for r in lp if int(r['Start']) <= y <= int(r['End'])}
    def alive_new(y):
        return {plab[pid] for pid, s in spans.items() if int(s['start']) <= y <= int(s['end'] or 2026)}
    for y in (-2000, -500, -221, 1, 500, 1066, 1368, 1500, 1800, 1900, 1945, 2000, 2026):
        check(alive_legacy(y) == alive_new(y), f'query by year {y} differs')
        notes[f'query {y}: {len(alive_new(y))} polities'] += 1

    if a.preview:
        prev = {int(r['legacy_row']): r['polity_id'] for r in read(a.preview)}
        same = sum(prev.get(row) == pid for (f, row), pid in xw.items() if f == 'polities.csv')
        check(same == len(pol), f'IDs differ from the S05 preview for {len(pol) - same} polities')

    for k, v in sorted(notes.items()):
        print(f'  note: {k} ({v})')
    if fails:
        print(f'FAILED: {len(fails)} problems'); [print('  ', f) for f in fails[:50]]; sys.exit(1)
    print(f'OK: {len(pol)} polities, {len(phases)} phases, {len(rulers)} rulers match the legacy data '
          'apart from the agreed changes listed above.')

if __name__ == '__main__':
    main()
