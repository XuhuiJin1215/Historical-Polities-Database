# Historical Polities v2 — Schema Specification

**Status:** **v1.1** (v1.0 frozen S05 + amendment S07: ruler role `effective_ruler`). Later changes by amendment, as for the standards.
**Implements:** [`standards.md`](standards.md) v1.0. Where this spec and the standards disagree, the standards win, unless the difference is listed in §9 as a proposed amendment.
**Legend:** ✅ follows from the standards or was confirmed by Xuhui (S05) · 🟡 proposed, to be settled at the stage named.

This document defines every table in `data/` and `vocab/`: file name, columns, types, keys, and validation rules. It also maps each legacy column to its v2 home (§8), so the Stage 1 migration can be checked for losslessness.

---

## 1. Conventions (all tables)

| Topic | Rule |
|---|---|
| Format | CSV, UTF-8 **without** BOM, LF line endings, comma separator, RFC 4180 quoting, one header row. |
| Editing | The Excel workbook is the editor (one sheet per table, same name and columns). `export.py` writes the CSVs; the CSVs are canonical in git. ✅ |
| Helper columns | Workbook columns whose name starts with `_` (e.g. `_polity_label` next to `polity_id`) are for the editor's convenience and are **not exported**. ✅ |
| Row order | Each CSV is written sorted by its primary key, so diffs stay small. |
| Text | Unicode NFC. Trimmed; no double spaces; non-breaking hyphens (U+2011) and non-breaking spaces replaced by ASCII equivalents. |
| Empty | An empty cell means "none / not applicable". In `end` columns it means **present** (§6 of the standards). |
| Years | Integers, historical numbering, BCE negative, **no 0**. Ranges are inclusive. |
| Precision | `start_precision` / `end_precision` ∈ `exact, circa, decade, century`. **Empty = exact** ✅. Legacy dates are *not verified*: a migrated row has an empty `source`, which marks it as unchecked until Stage 2 reviews it. How uncertain years feed duration grades and Query by Year: standards §6.1. |
| Booleans | `true` / `false` (lowercase). |
| Lists | Only `present_day_codes` holds a list, separated by `;` with no spaces (`CHN;MNG`). Every other multi-valued fact is a separate row. |
| Bilingual | Every human-readable field is a pair `<field>_en`, `<field>_zh`. ✅ |
| Provenance | `certainty` ∈ `certain, probable, disputed` (empty = certain); `source` = a key in `data/sources.csv`, or a `;`-separated list of keys. Empty allowed for migrated legacy data only (from Stage 2, required on new or changed facts). ✅ |

### 1.1 Identifiers ✅
| Entity | Format | Assignment |
|---|---|---|
| Polity | `P00001` | See [ID plan](../../notes/id-assignment-plan.md). Never reused, never renumbered. |
| Lineage | `L0001` | Next free number. |
| Phase | `P00001-01` | Polity ID + 2-digit sequence. A new phase takes the next free sequence number; existing phases are never renumbered, even if a phase is inserted between them. Display order comes from `start`, not from the number. ✅ |
| Ruler row | `R000001` | Next free number. |
| Vocabulary term | prefixed slug: `reg.`, `eth.`, `lang.`, `rel.`, `place.`, `gov.`, `title.` | Lowercase ASCII from the English term, `_` for spaces. A slug may *look* hierarchical (`gov.party.communist`) but the `parent` column is authoritative. On a collision, append a short distinguishing word chosen in review (never a bare `_2`). |

---

## 2. Polity tables (`data/`)

### 2.1 `polities.csv` — one row per polity
| Column | Type | Req. | Notes |
|---|---|---|---|
| `polity_id` | id | ✔ | PK |
| `name_en`, `name_zh` | text | ✔ | Conventional (display) name, without qualifier |
| `qualifier_en`, `qualifier_zh` | text | | Disambiguator, e.g. `state` / `诸侯国`, `Ten Kingdoms` / `十国`. Label = `name (qualifier)` in EN, `name（qualifier）` in ZH |
| `lineage_id` | → `lineages` | | A polity belongs to at most one lineage ✅ |
| `region_id` | → `vocab/regions` | ✔ | Core region |
| `region2_id` | → `vocab/regions` | | Optional secondary region |
| `present_day_codes` | list of ISO 3166-1 alpha-3 | ✔ | → `vocab/countries` |
| `founder_en`, `founder_zh` | text | | Founder of the first span ✅ |
| `evidence_tier` | enum `A, B, C` | ✔ | Legacy data migrates as `A`; Stage 2 assigns B/C where needed ✅ |
| `note_en`, `note_zh` | text | | |

Start and end are **not** stored here: they are derived from `spans.csv` (first start, last end). The overview table's single-value columns (religion, capital, …) come from the `is_primary` rows of `polity_attributes.csv`.

**Rules:** label unique per language across all polities; `present_day_codes` all exist in `vocab/countries`.

### 2.2 `spans.csv` — continuous periods of existence ✅ (§1, §3.3)
| Column | Type | Req. | Notes |
|---|---|---|---|
| `polity_id` | → `polities` | ✔ | PK part 1 |
| `span_no` | int ≥ 1 | ✔ | PK part 2, chronological |
| `start`, `end` | year | ✔ / | `end` empty = present (last span only) |
| `start_precision`, `end_precision` | enum | | |
| `certainty`, `source`, `note_en`, `note_zh` | | | |

**Rules:** every polity has ≥ 1 span; spans of one polity don't overlap and are in order; gaps between spans ≤ 25 years (§3.3); only the last span may have an empty `end`.

### 2.3 `polity_names.csv` — names other than the display name ✅ (§8)
| Column | Type | Req. | Notes |
|---|---|---|---|
| `polity_id` | → `polities` | ✔ | |
| `name_type` | enum `official, historiographic, alternative, conventional` | ✔ | `conventional` here = a *former* conventional name (time-ranged); the current one lives in `polities.csv` |
| `name_en`, `name_zh` | text | ✔ (one of) | A name may exist in one language only |
| `start`, `end` | year | | Empty = whole polity |
| `source`, `note_en`, `note_zh` | | | |

PK: (`polity_id`, `name_type`, `name_en`, `name_zh`, `start`). Empty in Stage 1; populated in Stage 2.

### 2.4 `lineages.csv` ✅ (§1)
`lineage_id` (PK), `name_en`, `name_zh`, `note_en`, `note_zh`. Members are the polities with this `lineage_id`, ordered by start. A lineage carries no ratings. Empty in Stage 1.

### 2.5 `relations.csv` ✅ (§4)
| Column | Type | Req. | Notes |
|---|---|---|---|
| `from_id`, `to_id` | → `polities` | ✔ | `from_id ≠ to_id` |
| `type` | enum `succeeded_by, restoration_of, split_from, merged_into, vassal_of, member_of, claims_succession_of` | ✔ | |
| `start`, `end` | year | | Required for `vassal_of`, `member_of` |
| `certainty`, `source`, `note_en`, `note_zh` | | | |

PK: (`from_id`, `to_id`, `type`, `start`). Empty in Stage 1.

### 2.6 `polity_attributes.csv` — time-varying categorical facts ✅ (§7)
| Column | Type | Req. | Notes |
|---|---|---|---|
| `polity_id` | → `polities` | ✔ | |
| `attribute` | enum `ethnic_group, language, religion, capital, government_type` | ✔ | |
| `value_id` | → the matching vocabulary | ✔ | `ethnic_group` → `vocab/ethnic_groups`, `language` → `vocab/languages`, `religion` → `vocab/religions`, `capital` → `vocab/places`, `government_type` → `vocab/government_types` |
| `role` | enum, allowed set depends on attribute (§7) | | `ethnic_group`: ruling, majority · `language`: official, majority · `religion`: official, ruling, majority · `capital`: seat, secondary, symbolic · `government_type`: — (empty) |
| `start`, `end` | year | | Empty both = whole polity |
| `is_primary` | bool | ✔ | Exactly one `true` per (polity, attribute) for every attribute the polity has |
| `certainty`, `source`, `note_en`, `note_zh` | | | |

PK: (`polity_id`, `attribute`, `value_id`, `role`, `start`). Rows must fall inside the polity's spans.
**Stage 1 migration:** each legacy single value → one row, empty `start`/`end`, `is_primary = true`, roles: ethnic `ruling`, language `official`, religion `official`, capital `symbolic` ✅. `government_type` is new: filled in Stage 1 only where obvious, otherwise in Stage 3.

### 2.7 `measures.csv` — area and population ✅ (standards v1.1)
Kept out of `polity_attributes` because they are numbers, not vocabulary terms, and each value belongs to exactly one phase (it feeds that phase's grade).

| Column | Type | Req. | Notes |
|---|---|---|---|
| `scope_id` | polity ID or phase ID | ✔ | PK. A **polity** ID = whole-polity peak (all legacy values); a **phase** ID = that phase's peak (Stage 3) |
| `area_kkm2` | decimal ≥ 0 | | Peak controlled area, thousand km² (legacy unit) |
| `area_year` | year | | Year of the peak, if known |
| `population_m` | decimal ≥ 0 | | Peak population, millions (legacy unit) |
| `population_year` | year | | |
| `certainty`, `source`, `note_en`, `note_zh` | | | |

**Link to grades:** where a phase has a value here, its stored Area/Population grade in `ratings.csv` must match the rubric threshold for that value (V15). A phase without a value keeps a manually estimated grade.

### 2.8 `phases.csv` ✅ (§1, §9)
| Column | Type | Req. | Notes |
|---|---|---|---|
| `phase_id` | id | ✔ | PK |
| `polity_id` | → `polities` | ✔ | Must equal the prefix of `phase_id` |
| `name_en`, `name_zh` | text | ✔ EN | ZH filled in Stage 3 |
| `start`, `end` | year | ✔ / | |
| `note_en`, `note_zh` | text | | Legacy notes → `note_en` |
| `legacy_score` | int 20–100 | | Legacy typed phase score; read-only, dropped once Stage 3 grades the phase |

**Rules:** a polity's phases tile its spans exactly: no overlaps, no gaps, first start = first span start, last end = last span end, and no phase crosses a gap between spans.

### 2.9 `ratings.csv` — grades for all nine dimensions ✅ (wide: one row per graded scope)
All nine dimensions are stored per phase, because Duration, Area and Population also change from phase to phase. The three quantitative grades are checked against the numbers wherever the numbers exist (V15), so a grade and its number can never disagree.

| Column | Type | Req. | Notes |
|---|---|---|---|
| `scope_id` | polity ID or phase ID | ✔ | PK. Polity ID = legacy whole-polity grades (Stage 1); phase ID = per-phase grades (Stage 3) |
| `dur`, `area`, `pop` | grade `S, A, B, C, D` | ✔ | Duration, Area, Population. `dur` = the polity's age at the end of the phase (option B; for a polity row, its full duration). `area`/`pop` = the phase's peak |
| `econ`, `mil`, `cult`, `tech`, `gov`, `soc` | grade `S, A, B, C, D` | ✔ | Economics, Military, Culture, Technology, Governance, Social |
| `dur_why_en`, `dur_why_zh`, … `soc_why_en`, `soc_why_zh` | text | | One-line justification per dimension (18 columns). Optional for `dur`, which is mechanical |
| `method` | enum `legacy, manual, ai_assisted` | ✔ | |
| `rubric_version` | text | ✔ | e.g. `1.1`; legacy rows: `legacy` ✅ §9.3 |
| `prompt_version` | text | | Required when `method = ai_assisted` (file in `docs/prompts/`) |
| `rated_on` | date `YYYY-MM-DD` | | |
| `note_en`, `note_zh` | | | |

**Scores (computed by `build.py`, never stored):**
- *Phase score* = dur×1 + area×2 + pop×2 + econ×3 + mil×3 + cult×3 + tech×3 + gov×2 + soc×1 (S=5 … D=1), range 20–100.
- *Overall* = envelope: each dimension's best grade across the polity's phase rows, then the formula. While a polity has no phase rows, its polity row is used. ✅ §9.2
- *Peak phase score* = highest phase score.

### 2.10 `rulers.csv` ✅ (Appendix A.1)
| Column | Type | Req. | Notes |
|---|---|---|---|
| `ruler_id` | id | ✔ | PK |
| `polity_id` | → `polities` | ✔ | |
| `role` | enum `monarch, head_of_state, head_of_government, party_leader, governor_general, regent, rival_claimant, effective_ruler` | ✔ | `effective_ruler` added in v1.1 (standards v1.2) |
| `title_id` | → `vocab/titles` | ✔ | |
| `name_en`, `name_zh` | text | ✔ | |
| `start`, `end` | year | ✔ (one of) | A.2: omit rows with both unknown |
| `start_precision`, `end_precision` | enum | | |
| `is_acting` | bool | ✔ | Default `false` |
| `certainty`, `source`, `note_en`, `note_zh` | | | |

**Rules:** within the polity's spans (A.7, validator flags); `start ≤ end`; title gender consistent with role (gendered titles only for monarchs and regents, A.4).

### 2.11 `sources.csv` ✅ (§10)
`source_id` (PK, short key: `enwiki`, `zhwiki`, `britannica`, …), `citation`, `url`, `accessed` (date), `note`. Seeded with the A.6 keys.

### 2.12 `retired_ids.csv` ✅
`id` (PK, a polity or lineage ID that no longer exists), `replaced_by` (the surviving ID, or empty), `reason_en`, `reason_zh`, `session` (e.g. `S12`). Keeps IDs from ever being reused and lets old links redirect. Empty in Stage 1.

---

## 3. Vocabularies (`vocab/`)

All vocabularies share: `id` (PK), `en`, `zh`, `parent` (→ same table, acyclic, optional), `note_en`, `note_zh`. Extra columns:

| File | Extra columns | Seeded from (Stage 1) |
|---|---|---|
| `regions.csv` | `sort` | Legacy `Region` (24 values) |
| `countries.csv` | `iso3` = `id` (no prefix), `is_current` | Legacy `Code` (199 values) + ISO list |
| `ethnic_groups.csv` | — | Legacy `Ethnic Group` (333) |
| `languages.csv` | — | Legacy `Language` (352) |
| `religions.csv` | — | Legacy `Religion` (106); `parent` e.g. `rel.catholicism` → `rel.christianity` |
| `places.csv` | `modern_en`, `modern_zh`, `country` (→ countries), `lat`, `lon` | Legacy `Capital` + `Present Day Location` (≈946 pairs); coordinates in Stage 3 |
| `government_types.csv` | `roles` (`;`-list of ruler roles), `definition_en`, `definition_zh` | Appendix B (19 types) ✅ |
| `titles.csv` | `gender` (`m, f, n`), `rank_note` | Legacy ruler titles (436 EN/ZH pairs) + A.4 list ✅ |
| `enums.csv` | `field`, `value`, `en`, `zh`, `sort` (PK = `field`+`value`; no `id`/`parent`) | Bilingual labels for every enum in this spec (roles, relation types, name types, precision, certainty, tiers, method, gender), so the site never hard-codes them |

Each distinct legacy `"English / 中文"` pair becomes one term. Spelling variants that clearly mean the same thing are merged in the vocabulary step, and the merge is logged in the session report.

---

## 4. Validation (`validate.py`, run locally and by GitHub Actions)

Errors block; warnings are reported.

| # | Check | Level |
|---|---|---|
| V1 | Headers exactly as specified; required columns non-empty | error |
| V2 | Primary keys unique; ID formats valid | error |
| V3 | Every foreign key resolves (incl. vocab `parent`, `present_day_codes`) | error |
| V4 | Enum values valid; attribute roles allowed for the attribute | error |
| V5 | Years are integers ≠ 0; `start ≤ end`; empty `end` only where allowed | error |
| V6 | Spans ordered, non-overlapping, gaps ≤ 25 years | error |
| V7 | Phases tile spans exactly | error |
| V8 | Exactly one `is_primary` per (polity, attribute) | error |
| V9 | Labels unique per language | error |
| V10 | Ruler, attribute, name and relation dates inside the polity's spans | warning (A.7) |
| V11 | No retired ID used anywhere | error |
| V12 | Vocabulary terms unused by any row | warning |
| V13 | `ai_assisted` rating without `prompt_version` | error |
| V14 | Missing `_zh` where `_en` is filled (phase notes exempt until Stage 3) | warning |
| V15 | `dur` matches the age at phase end; `area`/`pop` match the thresholds wherever `measures.csv` has a value for that scope | error |
| V16 | Borderline duration: a non-exact start or end whose uncertainty window (standards §6.1) could move the Duration grade across a band | warning |

---

## 5. Build outputs (summary; detailed with `build.py`)
`build.py` reads every table above and writes `site/data/index.json` (overview rows: label, years, region, primary attributes, Overall, peak phase score) and `site/data/polity/P00001.json` (everything about one polity). Computed values (start/end, durations, scores) exist only in these outputs.

## 6. AI ruler import
AI output may keep the master prompt's 5-column `Polity / Title / Name / Start / End` TSV with `"English / 中文"` cells (Appendix A). `import_rulers.py` splits the pairs, resolves polity and title IDs (stopping on anything unmatched), maps acting titles to `is_acting`, and appends new `R` IDs.

## 7. Workbook layout
Sheet order: polities, spans, phases, measures, ratings, polity_attributes, rulers, polity_names, relations, lineages, sources, retired_ids, then the `vocab_*` sheets. Dropdowns (data validation) on every enum and foreign-key column point at the vocabulary sheets. Helper columns (`_…`) can show labels via lookup formulas.

## 8. Legacy → v2 mapping (losslessness checklist)

| Legacy file · column | v2 location |
|---|---|
| polities · Political Entities | `polities.name_*` + `qualifier_*` (split at ` / `, then at the bracketed qualifier) |
| polities · Start, End | `spans` (span 1); End `2026` → empty (205 rows); `2024` (Ba'athist Syria) stays |
| polities · Ethnic Group, Language, Religion, Capital | `polity_attributes` rows → vocab terms |
| polities · Present Day Location | `vocab/places.modern_*` of the capital |
| polities · Founder | `polities.founder_*` |
| polities · Code | `polities.present_day_codes` (and `places.country`) |
| polities · Region | `polities.region_id` |
| polities · Duration (year) | dropped: computed |
| polities · Area, Population (numbers) | `measures` (polity row) |
| polities · Duration/Area/Population grades | `ratings` (polity row); checked against the numbers (V15). Mahameghavahana's Duration S → A (499 years, §6) |
| polities · Economics … Social | `ratings` (polity row, `method = legacy`, `rubric_version = legacy`) |
| polities · Overall; D…S numeric helper columns; spacer columns | dropped: computed / redundant |
| phases · Polity | `phases.polity_id` |
| phases · Start Year, End Year, Region, Overall Score | dropped: denormalised copies (4 rows disagree on years, 5 on Overall) |
| phases · Phase Name, Phase Start, Phase End, Notes | `phases.name_en`, `start`, `end`, `note_en` |
| phases · Phase Score | `phases.legacy_score` |
| rulers · Polity | `rulers.polity_id` |
| rulers · Title | `rulers.title_id` (+ `is_acting` for "Acting …" titles) |
| rulers · Name | `rulers.name_*`; "(anti-king)" / "（对立王）" → `role = rival_claimant` |
| rulers · Start, End | `rulers.start`, `end` |
| workbook · Query sheet | dropped: replaced by the site's Query by Year |

---

## 9. Decisions (S05)

| # | Decision | Status |
|---|---|---|
| 1 | Area and population in `measures.csv` (standards amended to v1.1) | ✅ |
| 2 | Ratings stored wide, **all nine dimensions** per phase; D/A/P checked against the numbers (V15) | ✅ (changed from the proposal, which stored only six) |
| 3 | Phase IDs never renumbered | ✅ |
| 4 | Empty precision = exact; empty certainty = certain. Legacy dates stay flagged as unverified (empty `source`) until Stage 2 | ✅ |
| 5 | Legacy polities default to evidence tier A | ✅ |
| 6 | `retired_ids.csv` for merged and removed polities | ✅ |
| 7 | `_`-prefixed helper columns, not exported | ✅ |
