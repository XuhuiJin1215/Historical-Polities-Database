"""Stage 1 migration: legacy CSVs (main branch) -> v2 tables (schema v1.0).

One-off script, kept for traceability. Run:
    pip install pypinyin babel pycountry
    python migrate.py --legacy <folder with polities.csv, phases.csv, rulers.csv> --out <repo root>
Writes data/, vocab/ and migration/ under --out. Re-running regenerates the same output.
After Stage 1 the workbook becomes the editing surface and this script is not run again.
"""
import argparse, csv, os, re, unicodedata, collections
from pypinyin import lazy_pinyin
from babel import Locale
import pycountry

PRESENT = 2026            # legacy convention: an end year of 2026 means "present"
GRADES = 'SABCD'

# ---------- helpers ----------
def clean(s):
    s = unicodedata.normalize('NFC', s or '')
    s = s.replace('‑', '-').replace('‐', '-').replace(' ', ' ').replace('　', ' ')
    return re.sub(r'\s+', ' ', s).strip().replace(' （', '（')

def split_pair(s):
    """'English / 中文' -> (en, zh). Tolerates missing spaces around the slash."""
    s = clean(s)
    if ' / ' in s:
        en, zh = s.split(' / ', 1)
    elif '/' in s:
        en, zh = s.split('/', 1)
    else:
        en, zh = s, ''
    return en.strip(), zh.strip()

def ascii_slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r"['’ʻ`]", '', s.lower())
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_') or 'x'

def pinyin_slug(zh):
    return ascii_slug(''.join(lazy_pinyin(zh))) if zh else ''

def year(s):
    y = int(clean(s))
    return y

def era_duration(start, end):
    """Years between start and end with historical numbering (no year 0)."""
    return end - start - (1 if start < 0 < end else 0)

def grade(v, thresholds):
    for g, t in zip('SABC', thresholds):
        if v >= t:
            return g
    return 'D'

DUR_T, AREA_T, POP_T = (500, 200, 100, 50), (1e7, 3e6, 1e6, 1e5), (1e8, 3e7, 1e7, 3e6)

def read(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def write(path, cols, rows, key=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if key:
        rows = sorted(rows, key=key)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\n', extrasaction='raise')
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, '') for c in cols})

class Vocab:
    """Collects terms keyed by an arbitrary natural key; assigns readable slug IDs."""
    def __init__(self, prefix):
        self.prefix, self.terms, self.by_key, self.used = prefix, [], {}, set()
    def add(self, key, en, zh, extra_slug_parts=(), **cols):
        if key in self.by_key:
            return self.by_key[key]
        base = f'{self.prefix}.{ascii_slug(en)}' if self.prefix else ascii_slug(en)
        cands = [base] + [f'{base}_{p}' for p in extra_slug_parts if p]
        tid = next((c for c in cands if c not in self.used), None)
        if tid is None:                       # last resort; reported as an issue
            n = 2
            while f'{base}_{n}' in self.used:
                n += 1
            tid = f'{base}_{n}'
            ISSUES.append(dict(type='vocab_slug_fallback', id=tid, detail=f'{en} / {zh}: numeric suffix used'))
        self.used.add(tid)
        t = dict(id=tid, en=en, zh=zh, **cols)
        self.terms.append(t)
        self.by_key[key] = tid
        return tid

ISSUES = []
def issue(t, i, d):
    ISSUES.append(dict(type=t, id=i, detail=d))

# ---------- fixed decisions (S05) ----------
QMAP = {'诸侯国': 'state', '十六国': 'Sixteen Kingdoms', '十国': 'Ten Kingdoms', '三国': 'Three Kingdoms'}
RULER_POLITY_FIX = {   # legacy ruler/phase polity label -> polities.csv label (S01: 7 mismatches)
    'Electorate of Brunswick-Lüneburg / 不伦瑞克-吕讷堡选侯国': 'Electorate of Brunswick-Lunenburg / 不伦瑞克-吕讷堡选侯国',
    'Khazar Khaganate / 可萨汗国': 'Khazar Khanate / 可萨汗国',
    'Kingdom / 刚果王国': 'Kingdom of Kongo / 刚果王国',
    'Kingdom of Shirvan / 希尔万沙王国': 'Kingdom of Shirvan / 希尔万沙王朝',
    '': 'Republic of Bosnia and Herzegovina / 波斯尼亚和黑塞哥维那共和国',   # Alija Izetbegović 1992–1995
}
CODE_FIX = {'GER': 'DEU'}
PHASE_FIX = {   # S07, temporary, to be rechecked: phase_id -> (start, end); None keeps the value
    'P01046-02': (1931, None),   # Brazil: 1889–1930 / 1930–1945
    'P01062-03': (1938, None),   # Republic of China: 1927–1937 / 1937–1945
    'P01091-03': (1962, None),   # Dominican Republic (Third Republic): 1930–1961 / 1961–1966
    'P01113-02': (1956, None),   # Austria (Second Republic): 1945–1955 / 1955–1979
    'P01214-02': (1995, None),   # Malawi: 1966–1994 / 1994–
    'P00215-03': (None, 1137),   # Gwynedd: 943–1282 contained 1138–1216
    'P00215-04': (None, 1282),   #   -> 943–1137 / 1138–1282 (no phase invented for 1217–1282)
}
COUNTRY_NAME_FIX = {  # ISO/CLDR names that read badly on the site: code -> (en, zh)
    'COD': ('Democratic Republic of the Congo', '刚果民主共和国'), 'COG': ('Republic of the Congo', '刚果共和国'),
    'PSE': ('Palestine', '巴勒斯坦'), 'VAT': ('Vatican City', '梵蒂冈'), 'RUS': ('Russia', '俄罗斯'),
    'FSM': ('Micronesia', '密克罗尼西亚联邦'),
}
VOCAB_MERGE = {   # (legacy column, EN variant) -> canonical EN; logged as issues of type vocab_merged
    ('Ethnic Group', 'Polish'): 'Pole',          # 6 x Pole, 5 x Polish (same ZH 波兰)
    ('Ethnic Group', 'Punjab'): 'Punjabi',       # ethnonym rather than region name (same ZH)
    ('Language', 'Mazandrani'): 'Mazanderani',   # standard spelling (same ZH 马赞德兰语)
}

def label(name, qual, lang):
    if not qual:
        return name
    return f'{name} ({qual})' if lang == 'en' else f'{name}（{qual}）'

# ---------- title -> role ----------
PARTY_ACR = r'\b(CCP|CPSU|CPV|LPRP|MPP|KSČ|SED|WPV|BSPP|FRELIMO|MPLA|MDP|LCY|PZPR|PPSh|PDPA|YSP|BCP|PCR|WPK|CPK|SRSP|WPE|IRB|SRB)\b|Kuomintang'
EFF = r'Shōgun|Head of (Oda|Tokugawa) Clan|Military Dictator|Druk Desi|^Desi$|Chairman of CMC'   # S07: effective_ruler
HOG = r'Prime Minister|Premier|Chancellor|Taoiseach|President of the Council\b(?! of State)|Council of Ministers|President of the Ministry|Council of People\'s Commissars|Chief Minister|State Counsellor|Kuhina Nui|Grand Pensionary|Kalön Tripa|Daijō-daijin|Naidaijin|State Minister|President of the Executive Council|Provisional Chief of Government|Chief Administrative Officer|Prince\'s Representative|Vice-President|Viceroy'
HOS = r'President|Chairman|Head of State|Chief of State|Consul|Captain Regent|Doge|Archon|Judge|Lawspeaker|Dictator|Director|Triumvir|Landammann|Stadtholder|Protector|Junta|Gonfaloniere|Leader|Führer|Caudillo|Generalissimo|Chief Executive|Supreme Chief|Coordinator|Commander|Secretary|State Elder|Grand Bailiff|O le Ao o le Malo|Officer|Member of the|Governor|Head of the Federal Military Government|Chief of the Executive Power'
REG = r'Regent|Sesshō|Sessei|Shikken|Kampaku'
FEMALE_EN = r'\b(Queen|Empress|Sultana|Maharani|Rani|Basilissa|Basilinna|Lady|Duchess|Archduchess|Countess|Princess)\b'

def title_role(en):
    if re.search(EFF, en):
        return 'effective_ruler', 'rule'
    if re.search(PARTY_ACR, en) or re.match(r'(General|First|Regional|Assistant Regional) Secretary of', en):
        return 'party_leader', 'rule'
    if re.search(r'Governor[- ]General|Officer Administering the Government', en):
        return 'governor_general', 'rule'
    if re.search(REG, en) and not re.search(r'Captain Regent|President of the Regency', en):
        return 'regent', 'rule'
    if re.search(HOG, en):
        return 'head_of_government', 'rule'
    if re.search(HOS, en) and not re.search(r'King-President|Co-Prince', en):
        return 'head_of_state', 'rule'
    return 'monarch', 'default'

def title_gender(en, zh, role):
    if re.search(FEMALE_EN, en) or zh.startswith('女') or re.search('女王|女皇|皇后|皇太后', zh):
        return 'f'
    if role == 'monarch':
        return 'm'
    if role == 'regent':
        return 'm' if (en == 'King Regent' or zh == '摄政王') else 'n'
    return 'n'

ROLE_OVERRIDE = {   # S07: (polity legacy label, title EN) -> role
    ('Islamic Republic of Iran / 伊朗伊斯兰共和国', 'President'): 'head_of_government',  # Supreme Leader is head of state
    ('Japan (Azuchi–Momoyama Period) / 日本（安土桃山时代）', 'Kampaku'): 'effective_ruler',  # Hideyoshi
}

ACTING = {('Acting President', '代理总统'): ('President', '总统'),
          ('Acting President', '代总统'): ('President', '总统'),
          ('Acting President', '代理国家主席'): ('President', '国家主席'),
          ('Acting Head of State', '代理国家元首'): ('Head of State', '国家元首'),
          ('Vice President', '副总统'): ('President', '总统'),        # S07: Gran Colombia stand-ins
          ('Delegate President', '代理总统'): ('President', '总统')}  # S07: Chile

GOV_TYPES = [  # Appendix B
    ('gov.mon.absolute', 'Absolute monarchy', '君主专制', '', 'Hereditary monarch with unchecked supreme authority', 'monarch;regent;rival_claimant'),
    ('gov.mon.feudal', 'Feudal monarchy', '封建君主制', '', 'Monarch whose authority runs through hereditary vassal lords', 'monarch'),
    ('gov.mon.elective', 'Elective monarchy', '选举君主制', '', 'Monarch chosen by a body of electors (HRE, Poland–Lithuania)', 'monarch'),
    ('gov.mon.constitutional', 'Constitutional monarchy', '君主立宪制', '', 'Monarch bound by a constitution, with a separate head of government', 'monarch;head_of_government'),
    ('gov.mon.realm', 'Commonwealth realm', '英联邦王国', '', 'Shares the British monarch; represented locally by a Governor-General', 'monarch;governor_general;head_of_government'),
    ('gov.mon.dual', 'Dual rule (shogunate type)', '二元统治（幕府型）', '', 'A nominal sovereign alongside an effective military ruler (Kamakura shogunate)', 'effective_ruler;monarch'),
    ('gov.theocracy', 'Theocracy', '神权政体', '', 'Supreme authority held by a religious office (Papal States, Ganden Phodrang)', 'monarch;regent'),
    ('gov.confed.tribal', 'Tribal confederation / khaganate', '部落联盟 / 汗国', '', 'Nomadic or tribal peoples united under a supreme ruler (Xiongnu, Göktürks)', 'monarch'),
    ('gov.rep.oligarchic', 'Oligarchic republic', '寡头共和制', '', 'Rule by elected magistrates drawn from a narrow elite (Roman Republic, Venice, Genoa)', 'head_of_state'),
    ('gov.rep.classical_democracy', 'Classical democracy', '古典民主制', '', 'Citizen assembly as the sovereign body (Athens)', 'head_of_state'),
    ('gov.rep.parliamentary', 'Parliamentary republic', '议会共和制', '', 'Head of government responsible to parliament; separate head of state', 'head_of_state;head_of_government'),
    ('gov.rep.presidential', 'Presidential republic', '总统共和制', '', 'President is both head of state and head of government', 'head_of_state'),
    ('gov.rep.semi_presidential', 'Semi-presidential republic', '半总统共和制', '', 'Executive president with a constitutionally subordinate PM (France, Fifth Republic)', 'head_of_state'),
    ('gov.rep.directorial', 'Directorial republic', '委员会制共和国', '', 'A collective executive council (Switzerland)', 'head_of_state'),
    ('gov.party', 'One-party state', '一党制国家', '', 'A single legal ruling party holds a monopoly on power', 'party_leader;head_of_state;head_of_government'),
    ('gov.party.communist', 'Communist state', '共产主义国家', 'gov.party', 'A one-party state ruled by a communist party', 'party_leader;head_of_state;head_of_government'),
    ('gov.military', 'Military regime', '军政府', '', 'Armed forces govern directly', 'head_of_state'),
    ('gov.theo_republic', 'Theocratic republic', '神权共和制', '', 'A republic in which a religious leader holds supreme authority (Islamic Republic of Iran)', 'head_of_state;head_of_government'),
    ('gov.provisional', 'Provisional government', '临时政府', '', 'Interim authority pending a constitutional settlement', 'head_of_state'),
]

GOV_DEF_ZH = {'gov.mon.absolute': '世袭君主掌握不受制约的最高权力',
    'gov.mon.feudal': '君主权力通过世袭封臣贵族层层行使',
    'gov.mon.elective': '君主由选举团体选出（如神圣罗马帝国、波兰-立陶宛）',
    'gov.mon.constitutional': '君主受宪法约束，另设政府首脑',
    'gov.mon.realm': '与英国共奉同一君主，由总督在当地代表君主',
    'gov.mon.dual': '名义君主与掌握实权的军事统治者并存（如镰仓幕府）',
    'gov.theocracy': '最高权力由宗教职位掌握（如教皇国、甘丹颇章）',
    'gov.confed.tribal': '游牧或部落民族在最高统治者之下联合（如匈奴、突厥）',
    'gov.rep.oligarchic': '由狭小精英阶层中选出的官员执政（如罗马共和国、威尼斯、热那亚）',
    'gov.rep.classical_democracy': '公民大会为最高权力机构（如雅典）',
    'gov.rep.parliamentary': '政府首脑对议会负责，另设国家元首',
    'gov.rep.presidential': '总统兼任国家元首和政府首脑',
    'gov.rep.semi_presidential': '总统掌握行政权，总理在宪法上从属于总统（如法兰西第五共和国）',
    'gov.rep.directorial': '由集体行政委员会执政（如瑞士）',
    'gov.party': '唯一合法的执政党垄断政权',
    'gov.party.communist': '由共产党执政的一党制国家',
    'gov.military': '由军队直接执政',
    'gov.theo_republic': '宗教领袖掌握最高权力的共和国（如伊朗伊斯兰共和国）',
    'gov.provisional': '宪政安排确定前的过渡性政权'}

ENUMS = [  # field, value, en, zh
    ('attribute', 'ethnic_group', 'Ethnic group', '民族'), ('attribute', 'language', 'Language', '语言'),
    ('attribute', 'religion', 'Religion / ideology', '宗教 / 意识形态'), ('attribute', 'capital', 'Capital', '首都'),
    ('attribute', 'government_type', 'Government type', '政体'),
    ('attribute_role', 'ruling', 'Ruling', '统治集团'), ('attribute_role', 'majority', 'Majority', '多数民众'),
    ('attribute_role', 'official', 'Official', '官方'), ('attribute_role', 'seat', 'Seat of government', '政府驻地'),
    ('attribute_role', 'secondary', 'Secondary capital', '陪都'), ('attribute_role', 'symbolic', 'Principal capital', '象征性首都'),
    ('ruler_role', 'monarch', 'Monarch', '君主'), ('ruler_role', 'head_of_state', 'Head of state', '国家元首'),
    ('ruler_role', 'head_of_government', 'Head of government', '政府首脑'), ('ruler_role', 'party_leader', 'Party leader', '党的领导人'),
    ('ruler_role', 'governor_general', 'Governor-General', '总督'), ('ruler_role', 'regent', 'Regent', '摄政'),
    ('ruler_role', 'rival_claimant', 'Rival claimant', '对立君主'),
    ('ruler_role', 'effective_ruler', 'Effective leader', '实际领导人'),
    ('relation_type', 'succeeded_by', 'Succeeded by', '继承者'), ('relation_type', 'restoration_of', 'Restoration of', '复辟自'),
    ('relation_type', 'split_from', 'Split from', '分裂自'), ('relation_type', 'merged_into', 'Merged into', '并入'),
    ('relation_type', 'vassal_of', 'Vassal of', '藩属于'), ('relation_type', 'member_of', 'Member of', '成员于'),
    ('relation_type', 'claims_succession_of', 'Claims succession of', '自称继承'),
    ('name_type', 'official', 'Official name', '正式名称'), ('name_type', 'conventional', 'Conventional name', '通称'),
    ('name_type', 'historiographic', 'Historiographic name', '史学名称'), ('name_type', 'alternative', 'Alternative name', '别称'),
    ('precision', 'exact', 'Exact', '确切'), ('precision', 'circa', 'Circa', '约'), ('precision', 'decade', 'Decade', '年代'),
    ('precision', 'century', 'Century', '世纪'),
    ('certainty', 'certain', 'Certain', '确定'), ('certainty', 'probable', 'Probable', '可能'), ('certainty', 'disputed', 'Disputed', '有争议'),
    ('evidence_tier', 'A', 'Documented', '文献记载'), ('evidence_tier', 'B', 'Tradition-attested', '传世文献'),
    ('evidence_tier', 'C', 'Archaeologically inferred', '考古推断'),
    ('rating_method', 'legacy', 'Legacy', '旧版'), ('rating_method', 'manual', 'Manual', '人工'),
    ('rating_method', 'ai_assisted', 'AI-assisted', 'AI 辅助'),
    ('gender', 'm', 'Male', '男'), ('gender', 'f', 'Female', '女'), ('gender', 'n', 'Neutral', '中性'),
    ('dimension', 'dur', 'Duration', '存续时间'), ('dimension', 'area', 'Area', '领土面积'),
    ('dimension', 'pop', 'Population', '人口规模'), ('dimension', 'econ', 'Economy', '经济'),
    ('dimension', 'mil', 'Military', '军事'), ('dimension', 'cult', 'Culture', '文化'),
    ('dimension', 'tech', 'Technology', '科技'), ('dimension', 'gov', 'Governance', '制度与治理'),
    ('dimension', 'soc', 'Social welfare', '社会民生'),
]

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--legacy', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    P = read(os.path.join(a.legacy, 'polities.csv'))
    PH = read(os.path.join(a.legacy, 'phases.csv'))
    R = read(os.path.join(a.legacy, 'rulers.csv'))
    D, V, M = (os.path.join(a.out, x) for x in ('data', 'vocab', 'migration'))
    xwalk = []

    # --- polities: names, ordering, IDs ---
    recs = []
    for i, r in enumerate(P, start=2):
        lab = clean(r['Political Entities'])
        en, zh = split_pair(lab)
        m = re.fullmatch(r'(.*?)\s*\(([^)]+)\)', en)
        en_n, en_q = (m.group(1), m.group(2)) if m else (en, '')
        m = re.fullmatch(r'(.*?)（([^）]+)）', zh)
        zh_n, zh_q = (m.group(1), m.group(2)) if m and (en_q or m.group(2) in QMAP) else (zh, '')
        zh_n, en_n = zh_n.strip(), en_n.strip()
        if zh_n + (f'（{zh_q}）' if zh_q else '') != zh:
            issue('label_whitespace', '', f'{lab}: space before the Chinese qualifier removed')
        recs.append(dict(row=i, src=r, legacy_label=lab, start=year(r['Start']), end=year(r['End']),
                         name_en=en_n, qualifier_en=en_q, name_zh=zh_n, qualifier_zh=zh_q))
    recs.sort(key=lambda d: (d['start'], d['end'], d['name_en'].casefold(), d['qualifier_en'].casefold(), d['name_zh']))
    by_label = {}
    for n, d in enumerate(recs, 1):
        d['id'] = f'P{n:05d}'
        by_label[d['legacy_label']] = d
        xwalk.append(dict(legacy_file='polities.csv', legacy_row=d['row'], legacy_key=d['legacy_label'], new_id=d['id']))

    # label fixes (S05)
    for d in recs:
        if not d['qualifier_en'] and d['qualifier_zh'] in QMAP:
            d['qualifier_en'] = QMAP[d['qualifier_zh']]
        if d['name_zh'] == '卫' and d['qualifier_zh'] == '诸侯国':
            d['name_en'] = 'Wey'
        if d['name_en'] == 'Later Jin' and d['name_zh'] == '后晋':
            d['qualifier_en'] = 'Five Dynasties'
        if d['name_en'] == 'Later Jin' and d['name_zh'] == '后金':
            d['qualifier_en'] = 'Jurchen'
    for zhn in ('秘鲁共和国', '阿尔巴尼亚共和国', '缅甸联邦'):
        grp = [x for x in recs if x['name_zh'] == zhn and not x['qualifier_zh']]
        targets = grp if zhn == '缅甸联邦' else [min(grp, key=lambda x: x['start'])]
        for x in targets:
            x['qualifier_zh'] = f"{x['start']}–{x['end']}"
    for lang in ('en', 'zh'):
        c = collections.Counter(label(d['name_' + lang], d['qualifier_' + lang], lang) for d in recs)
        dup = [k for k, v in c.items() if v > 1]
        assert not dup, f'duplicate {lang} labels: {dup}'

    # --- vocabularies from polities ---
    regions, countries = Vocab('reg'), {}
    eth, lang_v, rel, places = Vocab('eth'), Vocab('lang'), Vocab('rel'), Vocab('place')
    loc_zh = Locale.parse('zh_Hans')
    def country(code):
        code = CODE_FIX.get(code, code)
        if code not in countries:
            c = pycountry.countries.get(alpha_3=code)
            assert c, f'unknown ISO code {code}'
            countries[code] = dict(id=code, en=getattr(c, 'common_name', None) or c.name,
                                   zh=loc_zh.territories.get(c.alpha_2, ''), is_current='true')
            if code in COUNTRY_NAME_FIX:
                countries[code]['en'], countries[code]['zh'] = COUNTRY_NAME_FIX[code]
        return code
    region_order = []
    place_keys = []
    for d in recs:
        c_en, c_zh = split_pair(d['src']['Capital'])
        m_en, m_zh = split_pair(d['src']['Present Day Location'])
        place_keys.append((c_en != m_en, d['id'], c_en, c_zh, m_en, m_zh, d['src']['Code']))
    for _, _, c_en, c_zh, m_en, m_zh, code in sorted(place_keys):
        places.add((c_en, c_zh, m_en, m_zh), c_en, c_zh, (ascii_slug(m_en), pinyin_slug(c_zh)),
                   parent='', modern_en=m_en, modern_zh=m_zh, country=country(clean(code)), lat='', lon='')
    polities, spans, attrs, measures, ratings = [], [], [], [], []
    G = {g: 5 - i for i, g in enumerate(GRADES)}
    for d in recs:
        r = d['src']
        reg_en, reg_zh = split_pair(r['Region'])
        if (reg_en, reg_zh) not in regions.by_key:
            region_order.append((reg_en, reg_zh))
        rid = regions.add((reg_en, reg_zh), reg_en, reg_zh)
        code = clean(r['Code'])
        if code in CODE_FIX:
            issue('code_fixed', d['id'], f'Code {code} -> {CODE_FIX[code]}')
        cc = country(code)
        f_en, f_zh = split_pair(r['Founder'])
        end = '' if d['end'] == PRESENT else str(d['end'])
        polities.append(dict(polity_id=d['id'], name_en=d['name_en'], name_zh=d['name_zh'],
                             qualifier_en=d['qualifier_en'], qualifier_zh=d['qualifier_zh'],
                             region_id=rid, present_day_codes=cc, founder_en=f_en, founder_zh=f_zh,
                             evidence_tier='A'))
        spans.append(dict(polity_id=d['id'], span_no=1, start=d['start'], end=end))
        d['span'] = (d['start'], d['end'])
        # attributes
        for attr, col, voc, role in (('ethnic_group', 'Ethnic Group', eth, 'ruling'),
                                     ('language', 'Language', lang_v, 'official'),
                                     ('religion', 'Religion', rel, 'official')):
            en, zh = split_pair(r[col])
            if (col, en) in VOCAB_MERGE:
                issue('vocab_merged', d['id'], f"{col}: '{en}' -> '{VOCAB_MERGE[(col, en)]}'")
                en = VOCAB_MERGE[(col, en)]
            vid = voc.add((en, zh), en, zh, (pinyin_slug(zh),), parent='')
            attrs.append(dict(polity_id=d['id'], attribute=attr, value_id=vid, role=role, is_primary='true'))
        c_en, c_zh = split_pair(r['Capital'])
        m_en, m_zh = split_pair(r['Present Day Location'])
        pid = places.by_key[(c_en, c_zh, m_en, m_zh)]
        attrs.append(dict(polity_id=d['id'], attribute='capital', value_id=pid, role='symbolic', is_primary='true'))
        # measures and ratings
        area, pop = clean(r['Area (thousand km2)']), clean(r['Population (million)'])
        measures.append(dict(scope_id=d['id'], area_kkm2=area, population_m=pop))
        dur_g = grade(era_duration(d['start'], d['end']), DUR_T)
        legacy = {k: clean(r[c]) for k, c in (('dur', 'Duration'), ('area', 'Area'), ('pop', 'Population'),
                  ('econ', 'Economics'), ('mil', 'Military'), ('cult', 'Culture'), ('tech', 'Technology'),
                  ('gov', 'Governance'), ('soc', 'Social'))}
        if dur_g != legacy['dur']:
            issue('duration_grade_corrected', d['id'], f"{d['legacy_label']}: {legacy['dur']} -> {dur_g} "
                  f"({era_duration(d['start'], d['end'])} years without year 0)")
        assert grade(float(area) * 1e3, AREA_T) == legacy['area'] and grade(float(pop) * 1e6, POP_T) == legacy['pop']
        rt = dict(scope_id=d['id'], **legacy, method='legacy', rubric_version='legacy')
        rt['dur'] = dur_g
        ratings.append(rt)
        d['overall_legacy'] = int(clean(r['Overall']))

    # parents: 'X（Y）' -> term whose zh is X
    for voc in (eth, lang_v, rel):
        zh_index = collections.defaultdict(list)
        for t in voc.terms:
            zh_index[t['zh']].append(t['id'])
        for t in voc.terms:
            m = re.fullmatch(r'(.+?)（.+）', t['zh'])
            if m and len(zh_index.get(m.group(1), [])) == 1:
                t['parent'] = zh_index[m.group(1)][0]
    # vocab review issues: one language matches, the other differs
    for voc, nm in ((eth, 'ethnic_groups'), (lang_v, 'languages'), (rel, 'religions')):
        for side, other in (('en', 'zh'), ('zh', 'en')):
            g = collections.defaultdict(list)
            for t in voc.terms:
                g[t[side]].append(t)
            for k, ts in g.items():
                if len(ts) > 1:
                    issue(f'vocab_variant_{nm}', ';'.join(t['id'] for t in ts),
                          f"same {side.upper()} '{k}', different {other.upper()}: " + ' | '.join(t[other] for t in ts))
    g = collections.defaultdict(list)
    for t in places.terms:
        g[(t['en'], t['zh'])].append(t)
    for k, ts in g.items():
        if len(ts) > 1:
            issue('place_homonym', ';'.join(t['id'] for t in ts),
                  f"capital name {k[0]} / {k[1]} used for different present-day sites: " + ' | '.join(t['modern_en'] for t in ts)
                  + ' (kept as separate places; confirm)')

    # --- phases ---
    span_by_id = {d['id']: d['span'] for d in recs}
    def resolve(lbl):
        lbl = clean(lbl)
        lbl = RULER_POLITY_FIX.get(lbl, lbl)
        return by_label.get(lbl)
    phase_rows = collections.defaultdict(list)
    for i, r in enumerate(PH, start=2):
        d = resolve(r['Polity'])
        assert d, f'phase row {i}: polity not found: {r["Polity"]!r}'
        if clean(r['Polity']) != d['legacy_label']:
            issue('relinked_phase', d['id'], f"phases.csv row {i}: '{clean(r['Polity'])}' -> '{d['legacy_label']}'")
        s, e = year(r['Phase Start']), year(r['Phase End'])
        if e == 0:
            issue('year0_fixed', d['id'], f'phases.csv row {i}: end 0 -> -1')
            e = -1
        if s == 0:
            issue('year0_fixed', d['id'], f'phases.csv row {i}: start 0 -> 1')
            s = 1
        phase_rows[d['id']].append(dict(row=i, start=s, end=e, src=r))
    phases = []
    for pid, rows in phase_rows.items():
        rows.sort(key=lambda x: (x['start'], x['end'], x['row']))
        ps, pe = span_by_id[pid]
        for n, x in enumerate(rows, 1):
            phid = f'{pid}-{n:02d}'
            x['id'] = phid
            if phid in PHASE_FIX:
                fs, fe = PHASE_FIX[phid]
                issue('phase_boundary_fixed', phid, f"{x['start']}–{x['end']} -> {fs or x['start']}–{fe or x['end']} (temporary, recheck)")
                x['start'], x['end'] = fs or x['start'], fe or x['end']
            r = x['src']
            phases.append(dict(phase_id=phid, polity_id=pid, name_en=clean(r['Phase Name']), start=x['start'],
                               end='' if (x['end'] == PRESENT and pe == PRESENT) else x['end'],
                               note_en=clean(r['Notes']), legacy_score=clean(r['Phase Score'])))
            xwalk.append(dict(legacy_file='phases.csv', legacy_row=x['row'],
                              legacy_key=f"{clean(r['Polity'])} | {clean(r['Phase Name'])}", new_id=phid))
        if rows[0]['start'] != ps or rows[-1]['end'] != pe:
            issue('phase_edges', pid, f'phases run {rows[0]["start"]}..{rows[-1]["end"]}, polity {ps}..{pe}')
        for x1, x2 in zip(rows, rows[1:]):
            if x2['start'] <= x1['end']:
                issue('phase_overlap', pid, f"{x1['start']}–{x1['end']} overlaps {x2['start']}–{x2['end']}")
            elif x2['start'] > (1 if x1['end'] == -1 else x1['end'] + 1):
                issue('phase_gap', pid, f"gap between {x1['end']} and {x2['start']}")
    missing = [d['id'] for d in recs if d['id'] not in phase_rows]
    for m_ in missing:
        issue('no_phases', m_, 'polity has no phases')

    # --- rulers ---
    titles = Vocab('title')
    title_review = collections.Counter()
    relinked, paren = collections.Counter(), 0
    rrows = []
    for i, r in enumerate(R, start=2):
        d = resolve(r['Polity'])
        assert d, f'ruler row {i}: polity not found: {r["Polity"]!r}'
        if clean(r['Polity']) != d['legacy_label']:
            relinked[(clean(r['Polity']), d['legacy_label'], d['id'])] += 1
        t_en, t_zh = split_pair(r['Title'])
        acting = (t_en, t_zh) in ACTING
        if acting:
            t_en, t_zh = ACTING[(t_en, t_zh)]
        n_en, n_zh = split_pair(r['Name'])
        role, how = title_role(t_en)
        role = ROLE_OVERRIDE.get((d['legacy_label'], t_en), role)
        if '(anti-king)' in n_en or '（对立王）' in n_zh:
            role = 'rival_claimant'
            n_en = clean(n_en.replace('(anti-king)', ''))
            n_zh = clean(n_zh.replace('（对立王）', ''))
        tid = titles.add((t_en, t_zh), t_en, t_zh, (pinyin_slug(t_zh),), parent='',
                         gender=title_gender(t_en, t_zh, title_role(t_en)[0]), rank_note='')
        title_review[(tid, t_en, t_zh, title_role(t_en)[0], how)] += 1
        if re.search(r'\(|（', n_en + n_zh):
            paren += 1
        rrows.append(dict(row=i, d=d, role=role, title_id=tid, name_en=n_en, name_zh=n_zh,
                          start=year(r['Start']), end=year(r['End']), is_acting='true' if acting else 'false',
                          t=(t_en, t_zh)))
    for (old, new, pid), k in relinked.items():
        issue('relinked_ruler', pid, f"{k} rulers.csv rows: '{old}' -> '{new}'")
    issue('ruler_name_parenthetical', '', f'{paren} ruler names contain bracketed text (e.g. 姬发（周武王）, regnal or temple names); kept unchanged for Stage 2')
    # end 2026 -> present, unless a later holder of the same title in the same polity exists (then 2026 is a real end)
    later = collections.defaultdict(list)
    for x in rrows:
        later[(x['d']['id'], x['title_id'])].append(x['start'])
    rulers = []
    rrows.sort(key=lambda x: (x['d']['id'], x['start'], x['end'], x['row']))
    for n, x in enumerate(rrows, 1):
        rid = f'R{n:06d}'
        end = x['end']
        if end == PRESENT and x['d']['end'] == PRESENT:
            if any(s > x['start'] for s in later[(x['d']['id'], x['title_id'])]):
                issue('ruler_end_2026_kept', rid, f"{x['name_en']} ({x['t'][0]}): a later holder exists, so 2026 kept as a real end")
            else:
                end = ''
        ps, pe = x['d']['span']
        if x['end'] < ps or x['start'] > pe:
            issue('ruler_out_of_span', rid, f"{x['name_en']} {x['start']}–{x['end']} wholly outside {x['d']['legacy_label']} {ps}–{pe}")
        elif x['start'] < ps or x['end'] > pe:
            issue('ruler_partly_out_of_span', rid, f"{x['name_en']} {x['start']}–{x['end']} vs {x['d']['legacy_label']} {ps}–{pe}")
        rulers.append(dict(ruler_id=rid, polity_id=x['d']['id'], role=x['role'], title_id=x['title_id'],
                           name_en=x['name_en'], name_zh=x['name_zh'], start=x['start'], end=end,
                           is_acting=x['is_acting']))
        xwalk.append(dict(legacy_file='rulers.csv', legacy_row=x['row'],
                          legacy_key=f"{x['d']['legacy_label']} | {x['name_en']}", new_id=rid))

    # --- write ---
    C = lambda *c: list(c)
    write(f'{D}/polities.csv', C('polity_id', 'name_en', 'name_zh', 'qualifier_en', 'qualifier_zh', 'lineage_id',
          'region_id', 'region2_id', 'present_day_codes', 'founder_en', 'founder_zh', 'evidence_tier', 'note_en', 'note_zh'),
          polities, key=lambda r: r['polity_id'])
    write(f'{D}/spans.csv', C('polity_id', 'span_no', 'start', 'end', 'start_precision', 'end_precision', 'certainty',
          'source', 'note_en', 'note_zh'), spans, key=lambda r: (r['polity_id'], r['span_no']))
    write(f'{D}/polity_names.csv', C('polity_id', 'name_type', 'name_en', 'name_zh', 'start', 'end', 'source',
          'note_en', 'note_zh'), [])
    write(f'{D}/lineages.csv', C('lineage_id', 'name_en', 'name_zh', 'note_en', 'note_zh'), [])
    write(f'{D}/relations.csv', C('from_id', 'to_id', 'type', 'start', 'end', 'certainty', 'source', 'note_en', 'note_zh'), [])
    order = {'ethnic_group': 0, 'language': 1, 'religion': 2, 'capital': 3, 'government_type': 4}
    write(f'{D}/polity_attributes.csv', C('polity_id', 'attribute', 'value_id', 'role', 'start', 'end', 'is_primary',
          'certainty', 'source', 'note_en', 'note_zh'), attrs,
          key=lambda r: (r['polity_id'], order[r['attribute']], r['value_id'], r['role'], r.get('start', '')))
    write(f'{D}/measures.csv', C('scope_id', 'area_kkm2', 'area_year', 'population_m', 'population_year', 'certainty',
          'source', 'note_en', 'note_zh'), measures, key=lambda r: r['scope_id'])
    write(f'{D}/phases.csv', C('phase_id', 'polity_id', 'name_en', 'name_zh', 'start', 'end', 'note_en', 'note_zh',
          'legacy_score'), phases, key=lambda r: r['phase_id'])
    dims = ['dur', 'area', 'pop', 'econ', 'mil', 'cult', 'tech', 'gov', 'soc']
    write(f'{D}/ratings.csv', ['scope_id'] + dims + [f'{x}_why_{l}' for x in dims for l in ('en', 'zh')] +
          ['method', 'rubric_version', 'prompt_version', 'rated_on', 'note_en', 'note_zh'], ratings, key=lambda r: r['scope_id'])
    write(f'{D}/rulers.csv', C('ruler_id', 'polity_id', 'role', 'title_id', 'name_en', 'name_zh', 'start', 'end',
          'start_precision', 'end_precision', 'is_acting', 'certainty', 'source', 'note_en', 'note_zh'), rulers,
          key=lambda r: r['ruler_id'])
    write(f'{D}/sources.csv', C('source_id', 'citation', 'url', 'accessed', 'note'), [
        dict(source_id='britannica', citation='Encyclopaedia Britannica', url='https://www.britannica.com/'),
        dict(source_id='enwiki', citation='English Wikipedia', url='https://en.wikipedia.org/'),
        dict(source_id='zhwiki', citation='Chinese Wikipedia', url='https://zh.wikipedia.org/')], key=lambda r: r['source_id'])
    write(f'{D}/retired_ids.csv', C('id', 'replaced_by', 'reason_en', 'reason_zh', 'session'), [])

    base = ['id', 'en', 'zh', 'parent', 'note_en', 'note_zh']
    reg_terms = regions.terms
    for t in reg_terms:
        t['sort'] = 0
    # regions sorted by a fixed geographic order would be nicer; keep alphabetical sort numbers for now
    for n, t in enumerate(sorted(reg_terms, key=lambda t: t['en']), 1):
        t['sort'] = n
    write(f'{V}/regions.csv', base + ['sort'], reg_terms, key=lambda r: r['id'])
    write(f'{V}/countries.csv', ['id', 'en', 'zh', 'parent', 'is_current', 'note_en', 'note_zh'], list(countries.values()), key=lambda r: r['id'])
    write(f'{V}/ethnic_groups.csv', base, eth.terms, key=lambda r: r['id'])
    write(f'{V}/languages.csv', base, lang_v.terms, key=lambda r: r['id'])
    write(f'{V}/religions.csv', base, rel.terms, key=lambda r: r['id'])
    write(f'{V}/places.csv', base + ['modern_en', 'modern_zh', 'country', 'lat', 'lon'], places.terms, key=lambda r: r['id'])
    write(f'{V}/government_types.csv', base + ['roles', 'definition_en', 'definition_zh'],
          [dict(id=i, en=e, zh=z, parent=p, definition_en=de, definition_zh=GOV_DEF_ZH[i], roles=ro) for i, e, z, p, de, ro in GOV_TYPES],
          key=lambda r: r['id'])
    write(f'{V}/titles.csv', base + ['gender', 'rank_note'], titles.terms, key=lambda r: r['id'])
    write(f'{V}/enums.csv', ['field', 'value', 'en', 'zh', 'sort'],
          [dict(field=f, value=v, en=e, zh=z, sort=n) for n, (f, v, e, z) in enumerate(ENUMS, 1)],
          key=lambda r: (r['field'], int(r['sort'])))

    write(f'{M}/legacy_crosswalk.csv', ['legacy_file', 'legacy_row', 'legacy_key', 'new_id'], xwalk,
          key=lambda r: (r['legacy_file'], int(r['legacy_row'])))
    write(f'{M}/title_roles_review.csv', ['title_id', 'en', 'zh', 'role', 'how', 'rows'],
          [dict(title_id=k[0], en=k[1], zh=k[2], role=k[3], how=k[4], rows=v) for k, v in title_review.items()],
          key=lambda r: (r['how'] != 'default', -int(r['rows'])))
    write(f'{M}/issues.csv', ['type', 'id', 'detail'], ISSUES, key=lambda r: (r['type'], r['id']))
    print(f'polities {len(polities)}, phases {len(phases)}, rulers {len(rulers)}, attributes {len(attrs)}')
    print('vocab:', {n: len(v.terms) for n, v in (('regions', regions), ('ethnic', eth), ('languages', lang_v),
          ('religions', rel), ('places', places), ('titles', titles))}, 'countries', len(countries))
    print('issues:', dict(collections.Counter(x['type'] for x in ISSUES)))

if __name__ == '__main__':
    main()
