# Historical Polities v2 — Data Standards

**Status:** **v1.2** (amendments to frozen v1.0) · 2026-10-31
Version history: v0.1 (S01) draft → v0.2 (S02) member rule, ruler appendix → v0.3 (S03) duration and Overall, government types → v1.0 (S04) final decisions → **v1.1 (S05)** area/population stored in `measures.csv`; all nine grades stored per phase; §6.1 uncertain dates (proposed) → **v1.2 (S07)** ruler role `effective_ruler`. From now on, changes are made by amendment: note what changed and why in a session report, and bump the version (v1.1, …).
**Legend:** ✅ agreed · 🟡 proposed, needs confirmation · ❓ open question. In v1.0 all rules are agreed unless marked; the remaining ❓ items are optional future extensions.

This document defines what counts as a polity, where one polity ends and the next begins, and how every field is recorded. Every later step depends on it. When the standard and the data disagree, either the data is fixed or the standard is amended here, with the change noted in a session report.

---

## 1. Core concepts

| Term | Definition |
|---|---|
| **Polity** 政权 | ✅ A political regime or dynasty exercising high sovereignty and de facto independence over a territory. The unit is the *regime/dynasty*, not the long-run "country" (e.g. the French Third and Fifth Republics are separate polities). |
| **Span** 存续区间 | ✅ A continuous period during which a polity exists. Most polities have one span; a restored polity can have several, separated by gaps (§3.3). |
| **Lineage** 谱系 | ✅ An optional grouping of consecutive polities that historiography treats as successive forms of the same state tradition in the same core territory (e.g. *France*: Kingdom of France → First Republic → … → Fifth Republic). A polity belongs to at most one lineage. A lineage is a navigation aid, not a polity, and carries no ratings. |
| **Phase** 阶段 | A sub-period of a polity used for dynamic attributes and ratings. Phases tile the polity's spans without overlap. |

## 2. Inclusion criteria

A polity is included if it meets **all** of I1–I4.

**I1 — De facto independence** ✅
The regime controls its own internal administration, armed forces, revenue and, in practice, foreign relations and war. Nominal suzerainty does not disqualify (e.g. the Tahirids under the Abbasids; member states of the Holy Roman Empire that conducted their own diplomacy and wars).

**I2 — Exclusions** ✅
Not included: colonies, protectorates, states bound by a subsidiary alliance (or equivalent surrender of foreign policy), and occupation administrations. A polity **ends** in the year it loses control of its foreign relations (protectorate, subsidiary alliance), even if its ruling house continues. This matches existing practice: Hyderabad State ends 1798; the Khanate of Khiva and Emirate of Bukhara end 1873.
✅ *Puppet states* (formally independent but externally controlled, e.g. Manchukuo) are **excluded**: they lack sovereignty.

**I3 — Effective territorial control** ✅
The regime proclaimed or was recognised as a state and held a defined territory for at least about one year. Short-lived regimes count (Ran Wei 350–352, Great Shun 1643–1646). There is **no minimum size or duration**. For reference, Cliopatria's thresholds (≥ 5,000 km², ≥ 50 years) would exclude 75 and 417 of the current 1,360 polities respectively, which is not consistent with this project's aims.

**I4 — Evidence tier** ✅ (provisional; revisit with real cases)
Every polity carries an evidence tier, shown as a badge on the site:

| Tier | Meaning | Example |
|---|---|---|
| **A — Documented** | Contemporary written records of rulers or administration | Akkadian Empire, Western Han |
| **B — Tradition-attested** | Known mainly from later written tradition, with some archaeological support | Xia |
| **C — Archaeologically inferred** | State-level organisation inferred without readable records. Requires all of: a settlement hierarchy of ≥ 3 levels, monumental public architecture, and evidence of central administration (seals, standard weights, storage) | candidate early civilisations (Step 7) |

Tier C lets early civilisations that loosely match the definition of a polity be included under one consistent bar.

**I5 — Member and vassal states** ✅
This applies well beyond the HRE. The current data contains member or vassal states in at least six systems: the HRE, Zhou China, the Abbasid caliphate, Rus under the Golden Horde, Ottoman tributaries, and Mughal successor states. One general test applies to all of them, plus a significance filter for systems with very many members.

*General test.* A member or vassal state qualifies while it meets **all** of:
- **V1 — Internal succession:** rulers succeed by the state's own dynastic or constitutional process. Investiture or confirmation by the overlord is fine as a formality; appointment or removal at will is not.
- **V2 — Own means:** it keeps its own army and revenue. Tribute payments are fine.
- **V3 — Own external action:** in practice it makes war and treaties on its own account, at least within its region.

The state **ends** in the year it fails any of these (the overlord appoints its rulers, takes over its foreign relations, or garrisons it as a protectorate).

*Significance filter*, for systems with hundreds of members. It is derived from your existing entries:

| System | Filter | Fit with current data |
|---|---|---|
| HRE, German lands (before 1806) | Holds an **electoral vote** or a royal title | Exact. The included electorates start in the year of their electoral dignity: Saxony 1356 (Golden Bull), Bavaria 1623, Brunswick-Lüneburg 1692, Hesse 1803; Bohemia (royal title); Austria (dominant power). |
| HRE, Imperial Italy | Sovereign duchies, grand duchies and republics where imperial authority was nominal | Matches Milan, Savoy, Modena, Parma, Ferrara, Urbino, Florence/Tuscany |
| Zhou China | States in the *Shiji* tables 十二诸侯年表 and 六国年表, plus Yue and **Zhongshan** 中山 ✅ | Matches all 17 current 诸侯国 entries (verify). Zhongshan is to be added in Stage 7: a Warring States power that claimed kingship (323 BCE) and fought Yan and Zhao until Zhao conquered it (296 BCE). Ba 巴 and Shu 蜀 were not Zhou members; they are assessed as independent polities under I1–I4 in Stage 7. |
| Other systems | No extra filter: the general test is enough | — |

*What the filters would add (gap candidates for Stage 7):* the Electorate of the Palatinate; the Electorate of Brandenburg before 1618; ✅ the three ecclesiastical electorates (Mainz, Cologne, Trier); Zhongshan.

*Current entries that conflict with the general test* (✅ deferred to Stage 2):

| Entry | Current end | Issue |
|---|---|---|
| Principality of Wallachia | 1417 | Ends at Ottoman tribute, but under V1–V3 tribute alone doesn't end a polity. The Crimean Khanate (Ottoman vassal from 1475) and Republic of Ragusa (Ottoman tributary) continue, as do the Rus principalities under the Golden Horde. |
| Principality of Moldavia | 1498 | Same as Wallachia |
| Kingdom of Mysore | 1831 | Subsidiary status from 1799 (I2) |
| Thanjavur Maratha Kingdom | 1855 | British control from about 1799 (I2, verify) |
| Carnatic Sultanate | 1801 | Check the date of British dependence (I2, verify) |

## 3. Polity boundaries — where one polity ends and the next begins

### 3.1 A new polity begins when any of these occurs ✅
These rules are derived from how the current data is already split.

- **R1 — State form or title re-proclaimed:** a change of constitutional form or a formal new state title, or a union that creates a new state. Examples: Roman Kingdom → Republic → Empire; Tsardom of Russia → Russian Empire (1721); Kingdom of Great Britain → United Kingdom (1801); successive numbered republics.
- **R2 — Ruling house replaced by force:** conquest, usurpation, or a coup installing a different house. Examples: England 1066; Sicily under Savoy (1713).
- **R3 — Collapse and re-foundation:** the state loses its core or capital and is re-established elsewhere or after an interregnum, where historiography treats the result as a distinct regime. Examples: Western/Eastern Han, Northern/Southern Song, Western/Eastern Jin, Western/Eastern Zhou.

### 3.2 These do NOT start a new polity ✅
- Legal succession within a house, including cadet branches (Kingdom of France 987–1792 across Capetian, Valois and Bourbon).
- A new house installed through the state's own constitutional process, such as election or invitation (Greece 1863, if confirmed — see §3.4).
- A capital move without collapse; a change of conventional name (recorded in `polity_names`); territorial growth or loss.

### 3.3 Interruptions and restorations ✅
A restoration **continues the earlier polity** (same ID, new span) only if all of these hold:
1. The same ruling house or its legal heir returns.
2. The same state title is used.
3. The prior constitutional order is reinstated, not replaced.
4. The interruption lasts ≤ 25 years (about one generation).

Otherwise, the restored regime is a **new polity** linked by `restoration_of`. The regime that fills a gap (e.g. the Kingdom of Etruria) is always its own polity if it meets §2.

### 3.4 Test cases ✅
The proposed outcomes are agreed. Rows marked *verify* need a factual check, done when the case is applied in Stage 2.

| Case | Current | Proposed outcome | Rule |
|---|---|---|---|
| Grand Duchy of Tuscany 1569–1801 / 1814–1860 | 2 polities | **1 polity, 2 spans** (Ferdinand III himself returned; same title and order; 13-year gap) | 3.3 |
| Kingdom of Etruria 1801–1807 | separate | separate ✅ | R1, R2 |
| Duchy of Modena and Reggio 1452–1796 / 1814–1859 | 2 polities | **1 polity, 2 spans** if Francis IV counts as the legal Este heir (verify) | 3.3 |
| Duchy of Parma and Piacenza 1545–1802 / 1814–1859 | 2 polities | **stays 2**: in 1814 it went to Marie Louise, not the Bourbon-Parma heir (verify) | 3.3 (1) fails |
| Kingdom of Spain (Bourbon) 1700–1808 + (First Bourbon Restoration) 1813–1873 | 2 polities | **1 polity, 2 spans** (Ferdinand VII returned; prior order reinstated). ⚠️ The 1813–1873 entry appears to include the 1868–1870 provisional government and Amadeo of Savoy's reign (≈1870–1873), which would need their own handling | 3.3, R2 |
| Kingdom of Spain (Second Bourbon Restoration) 1874–1931 | separate | stays separate (new constitution of 1876) | R1 |
| Kingdom of Spain 1975– | separate | stays separate (new constitutional order) | R1 |
| Kingdom of France (Bourbon Restoration) 1815–1830 | separate | stays separate (Charter of 1814 = new constitutional form) | R1 |
| Kingdom of Greece 1832–1924 | 1 polity across Otto (Wittelsbach) → George I (Glücksburg) | stays 1 *if* the 1863 change counts as constitutional (election by the National Assembly) | 3.2 |
| Kingdom of Greece (Restored) 1935–1973 | separate | merge candidate (same house and title, 11-year gap); depends on whether the prior constitution was reinstated (verify) | 3.3 |
| Kingdom of England (Wessex) / Kingdom of England, 1066 | split | stays split (conquest) | R2 |
| Qi 齐（诸侯国）−1046 to −221 | 1 polity | ✅ **split at 386 BCE**: the Tian clan usurped the Jiang house (田氏代齐). Jiang Qi and Tian Qi become 2 polities in one lineage | R2 |
| Kingdom of Mysore 1399–1831 | — | ⚠️ Under I2 this would end in **1799** (subsidiary status), like Hyderabad in 1798 | I2 |
| Tahirid Dynasty 821–873 | included | included (nominal vassalage only) | I1 |

## 4. Relations between polities ✅

Stored in `relations.csv` as `from_id, to_id, type, start, end`. Relation types:

| Type | Meaning |
|---|---|
| `succeeded_by` | direct successor in the same core territory |
| `restoration_of` | restored regime that did not qualify for §3.3 continuation |
| `split_from` / `merged_into` | partition or union |
| `vassal_of` | nominal or real suzerainty that did not breach I1 (time-ranged) |
| `member_of` | member of a composite empire (HRE) |
| `claims_succession_of` | claimed legitimacy without territorial continuity (Shu Han → Han; HRE → Rome) |

## 5. Identifiers ✅

| Entity | Format | Notes |
|---|---|---|
| Polity | `P00001` | Opaque and never reused or renamed. Names can change; IDs never do. |
| Lineage | `L0001` | |
| Phase | `P00001-03` | polity ID + sequence number |
| Ruler row | `R000001` | One row per reign. ❓ Optional `person_id` later, to link one person across polities. |
| Vocabulary terms | readable slugs, e.g. `rel.islam.sunni`, `place.changan` | Slugs are stable because terms do not change name. |

## 6. Dates ✅

- **Era:** historical numbering. BCE years are negative, and there is **no year 0** (−1 = 1 BCE; the year after −1 is 1). Four current phase rows use year 0 and need fixing (Chera, Mahameghavahana, Satavahana, Indo-Scythian).
- **Duration across the era boundary:** subtract one extra year (−27 to 395 = 421 years).
- **Start / end:** the year of the founding event (proclamation, coronation, capture of the capital) and of the dissolution event. A successor may start in the same year its predecessor ends.
- **Precision:** `exact | circa | decade | century`. Non-exact dates display as "c.".
- **Ongoing:** an empty `end` means *present*. No modern polity is stored as ending in 2025 or 2026.
- **Time-ranged facts** (attributes, rulers, phases) follow the same rules, inclusive of both years.

### 6.1 Uncertain dates 🟡 (recorded S05; settle when building the validator and the website)
The stored year is always the best single estimate. Precision adds an **uncertainty window** around it:

| Precision | Display | Window (proposed) |
|---|---|---|
| exact (empty) | 1066 | the year itself |
| circa | c. 1066 | ± 10 years |
| decade | 1060s | the decade (1060–1069) |
| century | 11th century | the century (1001–1100) |

- **Legacy dates are unverified.** Many legacy years are approximate without being marked. Migrated rows carry no `source`, which marks them as unchecked; Stage 2 checks them and sets precision and certainty.
- **Duration rating:** computed from the stored years. When a window could push the duration across a band threshold (e.g. c. −150 to 350 sits on the 500-year S/A line), the validator warns (V16) and the grade is reviewed by hand. The grade is not changed automatically.
- **Query by Year:** a polity matches when the year falls between its stored start and end. If the year also falls inside an uncertainty window of the start or end, the result is shown with a "c." / uncertain marker rather than being hidden. Phases and rulers follow the same rule.

## 7. Attributes

Each time-varying fact is one row in `polity_attributes.csv`:
`polity_id, attribute, value_id, role, start, end, is_primary, certainty, source, note_en, note_zh`

- **`is_primary`:** one value per attribute per polity. It is what the overview table and filters show, preserving today's "one value per column" view. All other rows appear on the polity page timeline.
- **Migration rule:** in Step 1, each current single value becomes one row covering the whole polity, with `is_primary = true`. Detail is added later, wherever history warrants it.

| Attribute | Roles | Definition |
|---|---|---|
| `ethnic_group` | `ruling`, `majority` | Current values = `ruling` (the ruling elite's group) |
| `language` | `official`, `majority` | Official = court and administration |
| `religion` (incl. state ideology) | `official`, `ruling`, `majority` | e.g. Tang: Daoism `official` for given years; Mughal: Islam `ruling`, Hinduism `majority` |
| `capital` | `seat`, `secondary`, `symbolic` | Several may be active at once (Tang Chang'an + Luoyang). The current "most symbolic capital" = `is_primary` |
| `government_type` | — | Controlled vocabulary (draft list in Step 1): absolute monarchy, constitutional monarchy, elective monarchy, feudal monarchy, theocracy, khaganate/tribal confederation, oligarchic republic, parliamentary republic, presidential republic, one-party state, military regime, … |
| `area`, `population` | — | Numeric; at minimum the peak value per phase (feeds the ratings). *v1.1:* stored in `data/measures.csv` (one row per polity or phase), not in `polity_attributes.csv`; see `schema.md` §2.7 |

These fields stay polity-level and do not vary over time: `founder` (first span's founder), `region` (core region; optional secondary), `present_day_codes` (one or more ISO 3166 alpha-3 codes, replacing the single `Code`), and `evidence_tier`.

**Vocabularies** (`vocab/*.csv`: `id, en, zh, parent, …`) define every term once, in both languages. `parent` allows hierarchy (Sunni Islam → Islam), so a filter for "Islam" catches all branches. `places.csv` adds latitude and longitude, which give map pins for capitals.

## 8. Bilingual conventions ✅

- ✅ Every human-readable field is stored in **two columns** (`_en`, `_zh`), never as one `"English / 中文"` string. The website toggles EN/中文.
- **Names:** `name_en`, `name_zh`, plus an optional disambiguating `qualifier_en/_zh` (e.g. "state" / 诸侯国, "Ten Kingdoms" / 十国). The displayed label is name + qualifier, and the validator requires labels to be unique (this fixes `Song / 宋` vs `Song / 宋（诸侯国）`).
- **Name types** in `polity_names.csv`: `official`, `conventional` (the default display name), `historiographic` (e.g. "Third Republic"), `alternative`. Each is time-ranged where relevant.
- **Translation sources:** English uses the prevailing name in English-language scholarship. Chinese follows this order of precedence: (1) an established Chinese historiographic name (成吉思汗, 拜占庭帝国); (2) the domain conventions in Appendix A (Sanskrit-style for ancient South and Southeast Asia, simplified kanji for Japanese, PRC scholarly transliteration for Tibetan and Mongolian); (3) Xinhua transliteration conventions.
- Existing English-only text (3,590 phase notes) is translated in Step 3 or 4, with review.

## 9. Ratings

The full rubric is in [`rating-rubric.md`](rating-rubric.md). The v2 changes:

- **Dynamic ratings** ✅: all nine dimensions are graded **per phase**.
  - *Duration*, *Area* and *Population* grades are stored per phase like the others (v1.1). Duration = age at phase end (§9.1). Where a phase's peak area or population is recorded, its grade must match the existing thresholds (checked by the validator); where no value is recorded, the grade is estimated.
  - The six qualitative dimensions are graded S–D per phase, each with a one-line bilingual justification (this is the "fair description of each rating" feature).
- **Phase score** ✅ = the existing weighted formula (D×1 + A×2 + P×2 + E×3 + M×3 + C×3 + T×3 + G×2 + S×1, range 20–100), **computed from the stored grades, not typed**.

### 9.1 Duration in dynamic ratings ✅ Option B
Duration is awkward per phase, because it describes the polity's whole life, not a moment. Options tested on the current data:

| Option | Duration grade in each phase | Effect on current scores | Assessment |
|---|---|---|---|
| A. Polity-level | The whole polity's duration grade, the same in every phase | None: existing scores stay comparable | An early phase "knows" the polity's future longevity. But Duration's weight is 1 of 20, so this affects at most 4 of 100 points |
| **B. Age at phase end** (adopted) | Years from founding to the end of the phase | Changes 1,221 of 3,585 phase scores (mostly −1; up to −4); lowers Overall for 343 polities by 1–3 | Historically honest for a given year, but penalises young phases and breaks comparability with today's scores |
| C. Leave Duration out of phase scores | — | Numerically identical to A if D is added back for Overall | Only a presentational difference from A |

**Adopted: B.** A phase's Duration grade is based on the polity's age at the end of that phase.
- **Age** counts only years inside the polity's spans, so the gap in a restored polity is excluded.
- **Interaction with the envelope Overall (§9.2):** the best Duration grade across phases is always the final phase's, and the polity's age at its final phase equals its full duration. So **Overall keeps the full-lifetime Duration grade**: option B changes phase scores, never Overall.

### 9.2 Overall score ✅ Envelope
v0.1 proposed Overall = the highest phase score. Once phase scores are *computed*, that will generally come out **lower** than today's Overall. Today's grades judge each dimension at its best over the whole polity, and peak area, peak culture and peak governance often fall in different phases. Two definitions:

- **Envelope (adopted):** take each dimension's best grade across all phases, then apply the weighted formula. This reproduces the current methodology and matches the rubric, which scores area and population at their **peak** (高峰时期). Overall means "the polity's best achievements across its lifetime".
- **Peak phase:** the highest single phase score, meaning "the best single moment". Shown on the polity page as a second figure, *peak phase score*.

Note: the current Overall equals the peak phase score for 1,327 of 1,360 polities, because phase scores were typed to match. The other 33 differ by a few points (e.g. Sui: Overall 63, peak phase 56), and Nazi Germany's Overall differs between `polities.csv` (59) and `phases.csv` (56). In Stage 1, the current phase scores are kept as *legacy* values until per-phase grading in Stage 3 replaces them.

### 9.3 Traceability ✅ (adopted with v1.0)
Each rating row stores `rubric_version`, and if AI-assisted, the prompt version used. Prompt templates live in `docs/prompts/`. A small set of **anchor polities** with fixed grades (the rubric's own examples: Western Han, Tang, Qing, Byzantium, Mongol Empire…) is re-checked whenever the rubric or prompt changes, so grades stay calibrated across 20,000+ phase-dimension cells.

## 10. Sources and certainty ✅

- `certainty`: `certain | probable | disputed`. Disputed facts display with a marker.
- `source`: a short key into `sources.csv` (`id, citation, url`). Not required for migrated legacy data. Required for every new or changed fact from Step 2 onward.

## 11. Editing workflow ✅

**Adopted:** keep an Excel workbook as the editing surface, with one sheet per table and dropdowns driven by the vocabulary sheets, which prevents typos. A local Python script exports it to CSV, and both are committed: the CSVs are the canonical, readable record in git (clean diffs); the workbook is the convenient editor. GitHub Actions runs the validator on every push.


## 12. Open decisions

Decided in S02: puppet states excluded; R1–R3 and non-triggers; 25-year restoration limit; §3.4 test-case outcomes; evidence tiers (provisional); Xinhua as the transliteration fallback; workbook + CSV workflow with local Python scripts.
Decided in S03: member/vassal rule V1–V3 with filters; ecclesiastical electors included; I5 conflicts deferred to Stage 2; Duration option B; envelope Overall; `role` / `is_acting` / clipping in Appendix A; 万王之王 kept for both titles.

Decided in S07 (v1.2): ruler role `effective_ruler`; Kampaku = regent (Hideyoshi = effective leader); Iran's presidents = head of government; stand-in Vice/Delegate Presidents = President + acting; interim titles kept as titles.

Decided in S05 (v1.1): area and population stored in `measures.csv`; all nine grades stored per phase, with the quantitative ones checked against the numbers.

Decided in S04: Zhongshan added; Qi split at 386 BCE; rubric duration examples replaced (rubric v1.1); `gov.party` renamed "One-party state" with "Communist state" as its child type. **Standards frozen at v1.0.**

No blocking decisions remain. Optional future extensions: `person_id` for rulers (§5), a state-structure attribute (Appendix B).

---

## Appendix A — Ruler standards

Source: the ruler-list master prompt (preserved verbatim in [`prompts/ruler-list-v1.md`](prompts/ruler-list-v1.md)). Its rules carry over unchanged unless noted. Only the storage format changes for v2. AI output can keep the prompt's 5-column `English / 中文` TSV format, and the import script splits and links it.

### A.1 Storage (`data/rulers.csv`) ✅
`ruler_id, polity_id, role, title_id, name_en, name_zh, start, end, start_precision, end_precision, is_acting, certainty, source, note_en, note_zh`

- `role` (new): `monarch | head_of_state | head_of_government | party_leader | governor_general | regent | rival_claimant | effective_ruler`. *v1.2:* `effective_ruler` (Effective leader / 实际领导人) is the person who actually held power while the nominal sovereign or formal office lay elsewhere: shōguns, the Oda/Tokugawa heads and Hideyoshi, Goryeo's military rulers (武臣), the Druk Desi and Tibetan Desi, and paramount leaders without the top formal office (Deng Xiaoping). This replaces the "(rival)" suffix in names and lets the site group rows by role.
- `title_id` points to `vocab/titles.csv` (`id, en, zh, gender, rank_note`). Titles are gendered entries (King / Queen are separate IDs), so a gender column isn't needed and the female-ruler flag can be generated.
- `is_acting` (new): records acting or interim status **without** changing the title. This matches the prompt's rule (no "acting" label on the title) while keeping the information.
- Optional later: `person_id`, to link one person across polities (e.g. a monarch of several realms).

### A.2 Row rules ✅
- One row = one continuous tenure of one person in one role. Non-consecutive tenures and different titles over time get separate rows.
- Year-only integers with historical numbering: BCE negative, no year 0 (§6).
- Don't infer or fill gaps. Omit rulers whose start and end are both unknown. Include partially dated rulers, with `start_precision` / `end_precision` set.

### A.3 Roles included, by government type ✅
The roles follow the polity's `government_type` **in force at the time** (a v2 addition: government type can change within a polity).

| Government type | Roles |
|---|---|
| Absolute monarchy (ancient/medieval) | Monarch; powerful de facto regents who were the effective ruler; rival claimants if listed in sources |
| Presidential republic | President |
| Executive presidential / semi-presidential (PM constitutionally subordinate) | President only |
| Parliamentary republic | Head of state + head of government |
| Constitutional monarchy | Monarch + head of government |
| Commonwealth realm | Monarch + Governor-General + Prime Minister |
| Communist / one-party state | Party leader (shown first when start years overlap) + head of state + head of government |
| Dual rule (shogunate type) *(v1.2)* | Effective leader + nominal monarch |
| Any type *(v1.2)* | Effective leader, when power lay outside the formal offices (e.g. Deng Xiaoping) |

All types: include acting or interim leaders only if listed in a reliable source **and** in office ≥ 1 month. Omit interregna with no named ruler. Omit sub-rulers, vassals and regional governors unless they are the polity's primary ruler.

### A.4 Titles ✅
- Use the most accurate, specific title for the role and period. The Chinese title must match the English in meaning.
- Gender-correct titles for monarchs. Gender-neutral offices are never gendered (总理, never 女总理). Regent forms: Queen Regent / 摄政女王, King Regent / 摄政国王, Regent / 摄政.
- **Title preservation rule:** where Anglophone historiography keeps a culture-specific title untranslated, use the transliteration, and the standard PRC scholarly transliteration in Chinese. When in doubt, follow the English Wikipedia infobox. The prompt's list (Pharaoh / 法老, Basileus / 巴西琉斯, Lugal / 卢伽尔 vs Ensi / 恩西, Chanyu / 单于, Khagan / 可汗 vs Khan / 汗, Chakravartin / 转轮王, Deva Raja / 神王, Padishah / 帕迪沙, Shahanshah / 万王之王, Amir al-Mu'minin / 信士的长官, Negus Nagast / Negus, Mansa / 曼萨, Asantehene / 阿散蒂赫内, Oba / 奥巴, Huey Tlatoani / 大特拉托阿尼 vs Tlatoani / 特拉托阿尼, Sapa Inca / 萨帕印卡, Maharaja / 摩诃罗阇) seeds `vocab/titles.csv`. Distinct ranks stay distinct IDs.
- ✅ Shahanshah and Negus Nagast both keep 万王之王 for now (different IDs, same Chinese label). Revisit if it causes confusion on the site.

### A.5 Names ✅
- English: the most common historiographical name, without titles. Remove administrative prefixes unless they are inseparable from the historiographical name.
- Chinese: simplified, PRC convention, following the precedence in §8: established historical names (成吉思汗, 努尔哈赤); Japanese kanji converted to simplified (後→后, 國→国); PRC scholarly transliteration for Tibetan and Mongolian; Sanskrit-style for ancient Indian names (-varman → 跋摩, -deva → 提婆, -gupta → 笈多); otherwise Xinhua transliteration.

### A.6 Sources ✅
English Wikipedia and Britannica (and other reputable references) are primary. Chinese Wikipedia is used for Chinese names and titles and to cross-check dates; English Wikipedia wins when they conflict. Prefer a source's chronology or list section over its prose. Recorded as `source` keys (`enwiki`, `zhwiki`, `britannica`, …) per §10.

### A.7 Relation to polity spans ✅
The polity's spans are the verified period of sovereignty. Ruler rows are **clipped** to the spans (e.g. Victoria for the Commonwealth of Australia: 1901–1901). The validator flags any row outside the spans. The 39 current out-of-span rows are reviewed in Stage 1.

### A.8 Display order ✅
Group by role (title), with groups ordered by their first holder's start year, then chronological within each group. In v2 this is a **display rule** applied by the site, not a storage requirement.

### A.9 Flags ✅
The prompt's FLAGS section maps to v2 fields and reports: female rulers (generated from title gender), date discrepancies and uncertainties (`certainty` + `note`), omissions (session report), and polity-type and title-convention notes (`government_type` and the title vocabulary).

---

## Appendix B — Government types (`vocab/government_types.csv`) ✅

`government_type` is a time-ranged attribute (§7): one row per period, with `is_primary` on the most characteristic one. The ruler roles to record follow the type in force (A.3). Types marked **new** had no role rule in the ruler prompt; their roles were agreed in S04. The `parent` column lets a general type contain specific ones: a filter for "one-party state" also returns communist states.

| ID | English | 中文 | Definition | Ruler roles |
|---|---|---|---|---|
| `gov.mon.absolute` | Absolute monarchy | 君主专制 | Hereditary monarch with unchecked supreme authority | Monarch (+ effective regents, rival claimants) |
| `gov.mon.feudal` | Feudal monarchy | 封建君主制 | Monarch whose authority runs through hereditary vassal lords | Monarch |
| `gov.mon.elective` | Elective monarchy | 选举君主制 | Monarch chosen by a body of electors (HRE, Poland–Lithuania) | Monarch |
| `gov.mon.constitutional` | Constitutional monarchy | 君主立宪制 | Monarch bound by a constitution, with a separate head of government | Monarch + head of government |
| `gov.mon.realm` | Commonwealth realm | 英联邦王国 | Shares the British monarch; represented locally by a Governor-General | Monarch + Governor-General + Prime Minister |
| `gov.mon.dual` | Dual rule (shogunate type) **new** | 二元统治（幕府型） | A nominal sovereign alongside an effective military ruler (Kamakura shogunate) | Effective leader (`effective_ruler`) + nominal monarch |
| `gov.theocracy` | Theocracy | 神权政体 | Supreme authority held by a religious office (Papal States, Ganden Phodrang) | Religious head (Pope, Dalai Lama…) (+ effective regents) |
| `gov.confed.tribal` | Tribal confederation / khaganate | 部落联盟 / 汗国 | Nomadic or tribal peoples united under a supreme ruler (Xiongnu, Göktürks) | Supreme ruler (Chanyu, Khagan…) |
| `gov.rep.oligarchic` | Oligarchic republic | 寡头共和制 | Rule by elected magistrates drawn from a narrow elite (Roman Republic, Venice, Genoa) | Chief magistrate(s) (Consuls, Doge…) **new** |
| `gov.rep.classical_democracy` | Classical democracy **new** | 古典民主制 | Citizen assembly as the sovereign body (Athens) | Leading magistrates as listed in sources |
| `gov.rep.parliamentary` | Parliamentary republic | 议会共和制 | Head of government responsible to parliament; separate head of state | Head of state + head of government |
| `gov.rep.presidential` | Presidential republic | 总统共和制 | President is both head of state and head of government | President |
| `gov.rep.semi_presidential` | Semi-presidential republic | 半总统共和制 | Executive president with a constitutionally subordinate PM (France, Fifth Republic) | President only |
| `gov.rep.directorial` | Directorial republic **new** | 委员会制共和国 | A collective executive council (Switzerland) | Presiding officer (e.g. President of the Confederation) |
| `gov.party` | One-party state **new** | 一党制国家 | A single legal ruling party holds a monopoly on power. Used directly for non-communist cases (e.g. fascist or nationalist regimes) | Party leader + head of state + head of government |
| `gov.party.communist` | Communist state (parent: `gov.party`) | 共产主义国家 | A one-party state ruled by a communist party | Party leader + head of state + head of government |
| `gov.military` | Military regime **new** | 军政府 | Armed forces govern directly | Junta chief (+ head of state if separate) |
| `gov.theo_republic` | Theocratic republic **new** | 神权共和制 | A republic in which a religious leader holds supreme authority (Islamic Republic of Iran) | Supreme leader + president |
| `gov.provisional` | Provisional government **new** | 临时政府 | Interim authority pending a constitutional settlement | Head of the provisional government |

Notes:
- **State structure** (unitary / federal / confederal) is a separate attribute from government type, added later if useful.
- The list is a seed and will grow as Stage 1 maps existing polities to types. A new type needs its definition and role rule added here first.
