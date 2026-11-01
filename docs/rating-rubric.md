# Rating Rubric · 评分标准

**Version:** rubric **v1.1** · 2026-10-31. v1.0 = transcription of `Dimensions.pdf` (Chinese original; English translation added). v1.1 = duration examples replaced with cases checked against the dataset (S04).
**Scope:** applies to the whole history of civilisation, from the Sumerian city-states to the present, so every grade is judged on a global scale. For modern polities, judge from a historian's perspective: only the regime's achievements and their influence on later history, especially in technology and culture.
适用范围：标准适用于整个人类文明史（苏美尔城邦—现代），评分时应妥善考虑全局。对于现代政权，请从历史学的角度仅考虑该政权的成就对后世的影响，尤其是科技和文化层面。

## Scoring

| Grade | S | A | B | C | D |
|---|---|---|---|---|---|
| Points | 5 | 4 | 3 | 2 | 1 |

| Dimension | Code | Weight |
|---|---|---|
| Duration 存续时间 | D | 1 |
| Area 领土面积 | A | 2 |
| Population 人口规模 | P | 2 |
| Economy 经济 | E | 3 |
| Military 军事 | M | 3 |
| Culture 文化 | C | 3 |
| Technology 科技 | T | 3 |
| Governance 制度与治理 | G | 2 |
| Social welfare 社会民生 | S | 1 |

**Score** = Σ (points × weight), range **20–100**.
v2: computed per phase. Proposed: Overall = each dimension's best grade across phases (the "envelope"), with the peak phase score shown separately (see `standards.md` §9).

---

## Quantitative dimensions (computed automatically)

### 1. Duration · 存续时间 — polity-level
| | Threshold | Examples 示例 |
|---|---|---|
| S | ≥ 500 years 年 | Byzantium, Egyptian dynasties, Eastern Zhou → Spring and Autumn / Warring States system 拜占庭、古埃及王朝、东周→春秋战国体系 |
| A | 200–499 | Western Han, Tang, Qing 西汉、唐、清 |
| B | 100–199 | Northern Song, Northern Wei, Eastern Jin 北宋、北魏、东晋 |
| C | 50–99 | Yuan, Mongol Empire, Western Jin 元、蒙古帝国、西晋 |
| D | < 50 | Sui, Southern Ming, Qin; Later Jin; most Five Dynasties and Ten Kingdoms regimes 隋、南明、秦、后金、五代十国多数政权 |

> v1.1: examples checked against `polities.csv` durations — Western Han 211, Northern Song 167, Northern Wei 149, Eastern Jin 103, Yuan 97, Mongol Empire 65, Western Jin 50, Southern Ming 39, Sui 38, Qin 14. Remember to update `Dimensions.pdf` and any rating prompt to match.

### 2. Area · 领土面积 — peak controlled area 高峰时期的控制面积 (km²)
| | Threshold | Examples 示例 |
|---|---|---|
| S | ≥ 10,000,000 | super-empires: Mongol, Qing, British Empire 超级帝国级，如蒙古、清、英帝国 |
| A | 3,000,000–9,999,999 | classic unified civilisations: Han, Tang, Russian Empire 典型大一统文明，如汉、唐、俄罗斯帝国 |
| B | 1,000,000–2,999,999 | regional empires: Empire of Japan, Byzantium, Timurid Empire 区域性大帝国，如日本帝国、拜占庭、帖木儿帝国 |
| C | 100,000–999,999 | mid-sized states: Joseon, Yamato Japan, Lý Vietnam 中等政权，如朝鲜王朝、大和日本、越南李朝 |
| D | < 100,000 | small local regimes: Wuyue, Chu, city-states 地方小政权，如吴越、楚、城邦国家 |

### 3. Population · 人口规模 — peak 高峰时期
| | Threshold | Examples 示例 |
|---|---|---|
| S | ≥ 100,000,000 | Ming, Qing, modern great powers 明、清、近代大国 |
| A | 30,000,000–99,999,999 | Han, Tang, pre-WWII Empire of Japan 汉、唐、日本帝国二战前 |
| B | 10,000,000–29,999,999 | Byzantium, Joseon, Nara/Heian Japan 拜占庭、朝鲜王朝、奈良/平安日本 |
| C | 3,000,000–9,999,999 | Qin, Xiongnu, a single Warring State, Kamakura shogunate 秦、匈奴、战国单国、镰仓幕府 |
| D | < 3,000,000 | most ancient breakaway regimes, tribal confederations 多数古代割据、部落联盟 |

---

## Qualitative dimensions (graded per phase in v2)

### 4. Economy · 经济
| | Level | Standard 标准 |
|---|---|---|
| S | Builder of a cross-civilisational economic system 跨文明经济体系构建者 | Extremely high productivity, leading in agriculture, crafts and urbanisation; dominates cross-civilisational trade and currency settlement, forming an intercontinental economic order. 生产力极高，农业、手工业与城市化全面领先；主导跨文明贸易与货币结算，形成洲际经济秩序。 |
| A | Unified high-productivity commercial empire 大一统高生产力–商业帝国 | Domestic productivity far above neighbouring civilisations; large agricultural surplus; thriving crafts and markets; sustains a unified economy over the long term and radiates it to neighbours. 国内生产力远超周边文明；农业剩余巨大，手工业与市场体系繁荣；能长期维系大一统经济格局并辐射周边。 |
| B | Institutional innovator or regionally prosperous economy 制度创新或区域性繁荣经济体 | Innovates in fiscal, land, monetary or market institutions, or creates a highly prosperous regional economy, but at a scale insufficient to support a super-empire. 在财政、土地、货币或市场制度上有创新，或在局部区域形成高度繁荣的经济格局，但规模不足以支撑超级帝国。 |
| C | Specialised / locally prosperous economy 专业化/局部繁荣经济体 | Relies on a single resource or local market (tea, salt, silk, rice); maintains some surplus and regional influence, but overall strength is limited and poorly integrated. 依赖单一资源或局部市场（如茶、盐、丝绸、稻米）；能维持一定的商品剩余与区域影响，但总体国力有限，缺乏整合性。 |
| D | Subsistence economy 生存型经济体 | Mainly natural (non-market) economy; low productivity, very little surplus, weak markets and money circulation; sustains only basic survival. 以自然经济为主，生产力低下，商品剩余极少，市场与货币流通薄弱，仅维持基本生存。 |

### 5. Military · 军事
| | Level | Standard 标准 |
|---|---|---|
| S | Cross-civilisational strategic deterrence 跨文明战略威慑 | Creates a military order or deterrence system on an intercontinental scale, shaping the security of several civilisations. 能在跨大洲范围内形成军事秩序或威慑体系，影响多个文明的安全格局。 |
| A | Supra-regional expeditions and power projection 超区域远征与战略投射 | Stable long-range expedition and supply capability; projects and holds power over thousands of kilometres; achieves continental hegemony. 具备稳定跨区域远征与补给能力，能在数千公里范围投射力量并维持战果，在大洲范围内实现称霸。 |
| B | Regional hegemony 区域霸权 | Defeats and absorbs the main rivals in its core region; establishes regional dominance and military pressure on neighbours. 能在核心区域击败并整合主要竞争对手，建立区域主导权，对周边国家形成军事压制。 |
| C | Effective defence, limited counter-attack 有效防御与有限反击 | Defends effectively using geography, fortifications or mobile warfare; wins local campaigns but lacks sustained expansion capacity. 能依托地理、城防或机动作战进行有效防御，并在局部取得战役性胜利，但缺乏持续扩张能力。 |
| D | Tribal or fragmented forces 部落或割据武力 | Relies on tribal or small-scale warlord conflict; lacks a mature strategic system and large-scale operational capacity. 依赖部落或小规模军阀冲突，缺乏成熟的战略体系与大规模作战能力。 |

### 6. Culture · 文化
| | Level | Standard 标准 |
|---|---|---|
| S | Exporter of a civilisational paradigm 文明范式输出 | Exports a complete civilisational system (script, religion, philosophy, institutions), forming a cross-civilisational cultural sphere. 输出完整文明体系（文字、宗教、哲学、制度），形成跨文明的文化圈。 |
| A | Radiating value system 价值体系辐射 | Original (or deeply reworked) culture profoundly shapes the values, religion, law or literature of neighbouring states and peoples. 能够以原创型文化（或深度改造型文化）对周边国家/民族的价值观、宗教、法律、文学产生深远影响。 |
| B | Distinctive cultural identity 特色文化标识 | Has unique, widely known cultural symbols or art forms, but without broad diffusion. 拥有独特且广为人知的文化符号或艺术形式，但缺乏普遍性扩散。 |
| C | Autonomous script and institutions 文字与制度自主性 | Has its own writing system or institutional innovation, but its influence stays internal. 具备独立的文字系统或制度创新，但影响局限在内部。 |
| D | Oral or local culture 口头或地方性文化 | Sustained mainly by oral tradition or local folk custom; lacks wide transmission. 主要依靠口述传统或局部民俗维系，缺乏广域传播力。 |

### 7. Technology · 科技
| | Level | Standard 标准 |
|---|---|---|
| S | Industrial-revolution-level breakthrough 工业革命型突破 | Breakthroughs cause a qualitative leap in productivity and change the course of civilisation. 技术突破引发生产力质变，改变文明发展方向（产业革命级）。 |
| A | Monopoly of core technology 核心技术垄断 | Masters and monopolises key, irreplaceable technologies, keeping a long-term military/economic edge. 掌握并垄断关键技术，具备不可替代性，长期保持军事/经济优势。 |
| B | Original invention and improvement 技术原创与改进 | Original breakthroughs in metallurgy, agronomy, engineering, medicine etc. that drive social development. 在冶金、农学、工程、医学等方面有原创性突破，推动社会发展。 |
| C | Adoption and adaptation 技术引进与改造 | Effectively absorbs foreign technology and adapts it to local conditions. 能有效吸收外来技术，并在本土条件下进行适配和改造。 |
| D | Dependence and backwardness 技术依赖与落后 | Wholly dependent on external inputs; lacks independent research and innovation. 完全依赖外部输入，缺乏自主研发与创新能力。 |

### 8. Governance · 制度与治理
Core criteria: bureaucracy, rule of law, stability of power, integrative capacity. 评估核心：官僚制度、法制化、权力稳定、统治整合力。

| | Level | Standard 标准 |
|---|---|---|
| S | Model good governance (institutional exemplar) 模式化的良治（制度化典范） | Professional bureaucracy, clear legal procedure, institutionalised succession; efficiently integrates large populations and territories; institutions serve as a model abroad. 官僚体系专业、法律程序明确、权力更替有制度，能高效整合广域人口与领土，制度有对外示范价值。 |
| A | Complete but imperfect (mature governance) 完备但不完美（成熟治理） | Bureaucracy and law largely complete, strong execution with occasional political turbulence; maintains most territory and fiscal order long-term. 官僚与法律基本完备，执行力高但偶有政治波动；能长期维持大部分领土与财政秩序。 |
| B | Institutions reliant on personal rule (semi-institutionalised) 有制度但依赖人治（半制度化） | Formal bodies and laws exist but gaps are filled by strongmen or ad hoc arrangements; localities keep considerable autonomy; moderate efficiency. 存在正式机构/法律，但靠强人或临时机制补缺，地方仍有较大自主权，治理效率中等。 |
| C | Authority-based rule (weak institutions) 基于权威的统治（弱制度） | Power held by individuals, armies or local forces; weak bureaucracy and law; struggles to govern distant or diverse societies. 权力靠个人、军力或地方势力维系；官僚与法制薄弱，难以有效管理远方或多元社会。 |
| D | No effective governance (institutional collapse) 无有效治理（制度崩溃） | Bureaucracy exists in name only, law ineffective, frequent internal strife; state cannot provide basic public order. 官僚名存实亡、法律失效、频繁内乱，国家机构无法提供基本公共秩序。 |

### 9. Social welfare · 社会民生
Core criteria: food and livelihood security, basic education and skills, public services and social mobility. 评估核心：粮食与生活保障、基本教育/技能传播、公共服务与社会流动。

| | Level | Standard 标准 |
|---|---|---|
| S | Broad high welfare (stability for all) 广泛高福祉（全民稳定） | Stable food supply with long-term surplus and reserves; literacy and vocational training widely available; systematic public services (medicine, water management, granaries, roads, disaster relief); open paths of social mobility. 粮食稳定，长期余粮与储备；识字/写作与职业训练广泛可得；系统性公共服务（医疗、治水、仓储、道路、赈灾）完善；社会上升通道通畅。 |
| A | Good living security (broadly available) 较高生活保障（普及性良好） | Most people have stable food and housing; literacy or formal training common among the mainstream population; public works and relief effective though coverage incomplete; mobility generally possible. 大多数人口有稳定食物与住所；识字或正规训练在主流群体中普及；公共工程与赈灾机制有效但覆盖略有不足；社会流动一般可实现。 |
| B | Partial improvement (limited inclusiveness) 局部改善（有限普惠） | Good welfare in towns and rich areas, unstable in rural or remote areas; education exists with limited reach; basic public works poorly maintained; restricted mobility. 城镇或富庶区福利良好，农村或偏远地区不稳定；教育/训练存在但覆盖有限；有基本公共工程但维护与覆盖不足；上升渠道受限。 |
| C | Basic survival (fragile system) 基本生存（脆弱体系） | Frequent famine or regional shortages; literacy and training scarce; weak public services and low relief capacity; rigid social strata. 常见粮荒或地区性短缺；识字/训练稀缺；公共服务薄弱，灾害时救助能力低；社会阶层固化，普通人很难上升。 |
| D | Widespread poverty (survival crisis) 广泛贫困（生存危机） | Chronic famine; public infrastructure almost absent; no education or training; no effective relief; social upheaval or high mass mortality. 长期饥荒、公共基础设施几乎不存在、教育与训练缺失、无有效赈灾或救济，社会动荡或大规模死亡率高。 |
