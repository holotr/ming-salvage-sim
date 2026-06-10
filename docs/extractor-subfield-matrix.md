# Extractor 全子字段测试矩阵

> 把 4 档房 prompt 契约里**每个子字段 / 枚举值**列成可独立验证的测试点。
> 目标：每个点至少被一个带 `expect_values` 的 case 覆盖。约 **138 个点**。

## 写 `expect_values` 的铁律（从 simulation.py 落库链反推）

`extractor_field_coverage.py` 读的是 `db.get_turn_extraction(turn).extractor_output`，
= `_localized_extraction(merged)`，其中 `merged` 已过 `_sanitize_module_output`（枚举规范化）。

- **键**：写中文（runner 的 `_VALUE_KEY_ALIASES` + prompt 的 `ITEM_FIELD_LABELS` 双向兜底，中英皆可命中）。
- **枚举值**：必须断言**规范化后的英文**，不是 prompt 里的中文：
  - 方向 `收`→`income`、`支`→`expense`
  - 计税公式 `按税基`→`per_basis`
  - 计税依据 `人口`→`population`、`在册田亩/田亩`→`registered_land`
  - 结案/撤销 原因 `resolved`/`failed`（英文）
  - 密令状态 `done`/`failed`
  - 崇祯结局 `abdicate`/`suicide`/`null`
  - 人物归属 `new_power` = power_id（`ming`/`houjin`/`bandits`/`mongol`…）
  - 军队归属 `owner_power` = power_id 或势力中文名（落库看 _clean）
- **数值**：照写（容差 0.01）。增量带符号。
- **自由文本**（原因/叙述/阶段/状态/结果/推演备注）：**不要断言精确文本**（模型每次措辞不同，必抖 FAIL）。
  只用 `expect_fields` 验顶层命中，或在 cheat 里 `须输出…` 锁结构后只断言**结构性键**（如位号/状态枚举），不断言长文本。
- **难命中的点**：cheat 里写 `须输出 <字段>：[{…}]` 显式喂结构，让值校验确定化（沿用现有 c066* / c068* 套路）。
- **dict 型字段**（国势变化/派系变化/阶级变化/地区变化/军队变化/势力变化/四方动向）：
  `expect_values` 写成 `{实体id: {子字段: 值}}`；**list 型**（钱粮收支/财政制度变化/新立/裁撤/局势*/新建军队/人物变化/后宫册封/密令*）写成 `[{子字段: 值}]`。

---

## 一、internal 档房（8 顶层字段）

### 国势变化（dict，2 点）
| 点 | 断言 | case |
|---|---|---|
| 民心+ | `{"民心": +n}` | NEW c200 |
| 皇威+ | `{"皇威": +n}` | NEW c201 |

### 钱粮收支（list，7 点）
| 点 | 断言 | case |
|---|---|---|
| 账户=内库 + 正增量 | `账户:内库,增量:+` | c001 ✅ |
| 账户=国库 + 正增量 | `账户:国库,增量:+` | c002 ✅ |
| 出账负增量(国库) | `账户:国库,增量:-` | c003 ✅ |
| 用途=补饷+目标编号 | `用途:补饷,目标编号:army_id` | c004 ✅ |
| 小数换算(两→万两) | `增量:0.46` | c064 ✅ |
| 分类 | `分类:<值>` | NEW c202 |
| 用途=其它(互拨出账) | `用途:其它` | NEW c203 |
| 目标类型=army | `目标类型:army` | NEW c204（并入c004补强） |

### 财政制度变化（list，5 口径全覆盖）
| 点 | 断言 | case |
|---|---|---|
| 口径=设为原始值 | `口径:设为原始值,数值:55` | c066 ✅ |
| 口径=增减原始值 | `口径:增减原始值,数值:5` | c066b ✅ |
| 口径=月额设为 | `口径:月额设为,数值:30` | c066c ✅ |
| 口径=月额增减(负) | `口径:月额增减,数值:-10` | c066d ✅ |
| 口径=月额增减(正) | `口径:月额增减,数值:2` | c066f ✅ |
| 口径=月额按比例增减 | `口径:月额按比例增减,数值:-30` | c066e ✅ |

### 新立月度收支（list，9 点）
| 点 | 断言 | case |
|---|---|---|
| 固定月收(账户/方向income/初值) | `账户,方向:income,初值` | c008 ✅ |
| 固定月支(方向expense/初值) | `方向:expense,初值` | c009 ✅ |
| 按税基-人口 | `计税公式:per_basis,计税依据:population` | c068a ✅ |
| 按税基-在册田亩 | `计税公式:per_basis,计税依据:registered_land` | c068b ✅ |
| 按税基-官民田 | `计税依据:guan_min_tian?` | NEW c205（验依据枚举） |
| 按税基-皇庄 | `计税依据:huang_zhuang?` | NEW c206 |
| 按税基-藩王庄田 | `计税依据:wang_tian?` | NEW c207 |
| 按税基-隐田 | `计税依据:hidden_land?` | NEW c208 |
| 税率单位(毫/亩/年) | `税率单位` | 随 c068b 验 |

### 裁撤月度收支（list，2 点）
| 点 | 断言 | case |
|---|---|---|
| 键(矿税整项删) | `键:矿税_base` | c010 ✅ |
| 键(织造整项删) | `键:织造_base` | c068c ✅ |

### 派系变化（dict，2 点）
| 点 | 断言 | case |
|---|---|---|
| satisfaction± | `{派系:{满意:±}}` | NEW c209 |
| leverage± | `{派系:{影响力:±}}` | NEW c210 |

### 阶级变化（dict，3 点）
| 点 | 断言 | case |
|---|---|---|
| 键=<阶级>@<region> | `key 形如 农民@shaanxi` | NEW c211 |
| satisfaction± | `{...:{满意:±}}` | NEW c211 |
| leverage± | `{...:{影响力:±}}` | NEW c212 |

### 地区变化（dict，23 子字段——重头戏）
每点一个 case，断言 `{region_id: {子字段: ±值}}`：
民心 / 动乱 / 粮食年产 / 存粮 / 士绅阻力 / 军事压力 / 腐败度 / 官民田 / 藩王庄田 / 皇庄 /
田赋亩率 / 辽饷亩率 / 盐税基数 / 商税基数 / 人口 / 田亩(registered_land) / 隐田 / 税收 /
天灾 / 人祸 / 状态(文本不强断) / 控制(power_id) / 「全国」特例(商税基数)
→ NEW c220–c242（全国特例已有 c106 ✅）

---

## 二、issues 档房（4 顶层字段）

### 局势推进（list，5档+专款）
| 点 | 断言 | case |
|---|---|---|
| verygood 大幅正 | 进度增量 +20~+50 | NEW c250（断言增量符号/区间） |
| good 中等正 | +8~+20 | NEW c251 |
| normal 轻正 | +1~+7 | NEW c252 |
| bad 轻负 | -1~-7 | NEW c253 |
| verybad 大幅负 | -20~-50 | NEW c254 |
| 专款支取 | `专款支取:n` | NEW c255 |
| 局势编号 | `局势编号:N` | c024 部分 ✅ |

> 进度增量是区间，runner 只能精确比对——断言策略：cheat 锁定 `进度增量: <具体数>`，断言该数。

### 新立局势-decree（list，14 字段）
| 点 | 断言 | case |
|---|---|---|
| 类型=initiative | `类型:initiative` | NEW c260 |
| 题材=工程 | `题材:工程`+解决效果建筑create | NEW c261 |
| 题材=政治 | `题材:政治`+部门create | NEW c262 |
| 题材=科技 | `题材:科技`+科技create | NEW c263 |
| 题材=军事/民生/经济/文化/其他 | `题材:<枚举>` | NEW c264-268（合并验枚举） |
| 可撤销=decree | `可撤销:decree` | NEW c269 |
| 可撤销=never | `可撤销:never` | NEW c270 |
| 可撤销=by_progress | `可撤销:by_progress` | c020 ✅(值校验补) |
| 当前进度/预计月数 | 数值 | NEW c271 |
| 承办人 | 文本不强断/验存在 | — |
| 解决效果.建筑create | `动作:create,类别` | c261 |
| 解决效果.部门create | `动作:create` | c262 |
| 解决效果.科技create | `动作:create` | c263 |

### 新立局势-event_pool（2 点）
| 点 | 断言 | case |
|---|---|---|
| 来源类型=event_pool+编号 | `来源类型:event_pool,编号:<id>` | NEW c272（需盘面有候选） |

### 撤销局势（list，3 点）
| 点 | 断言 | case |
|---|---|---|
| 局势编号 | `局势编号:702` | c026 ✅(补值) |
| 已付代价 | 结构存在 | NEW c273 |

### 结案局势（list，2 点）
| 点 | 断言 | case |
|---|---|---|
| 原因=resolved | `局势编号,原因:resolved` | c025 ✅(补值) |
| 原因=failed | `原因:failed` | c083 ✅ |

---

## 三、military 档房（5 顶层字段）

### 军队变化（dict，12 动作）
| 点 | 断言 | case |
|---|---|---|
| 扩编 manpower+/maint+ | `{army:{人数:+,月维护费:+}}` | NEW c280 |
| 裁撤 manpower-/maint- | `{army:{人数:-}}` | NEW c281 |
| 改番号 name | `{army:{番号:<新名>}}` | NEW c282 |
| 改编制 troop_type | `{army:{兵种:<值>}}` | NEW c283 |
| 改主帅 commander | `{army:{统帅:<姓名>}}` | NEW c284 |
| 调度 station | `{army:{驻地:<地>}}` | NEW c285 |
| 倒戈 owner_power | `{army:{归属势力:houjin}}` | NEW c286 |
| 士气 morale± | `{army:{士气:±}}` | NEW c287 |
| 忠诚 loyalty± | `{army:{忠诚:±}}` | NEW c287 |
| 训练 training± | `{army:{训练:±}}` | NEW c288 |
| 装备 equipment± | `{army:{装备:±}}` | NEW c288 |

### 新建军队（list，owner 三类 + 属性）
| 点 | 断言 | case |
|---|---|---|
| 官军 owner=大明 | `归属势力:大明` | c031 ✅(补值) |
| 叛军 owner=流寇 | `归属势力:流寇` | c032 ✅(补值) |
| 外族 owner=后金 | `归属势力:后金` | c089 ✅(补值) |
| 外族 owner=蒙古 | `归属势力:蒙古` | c090 ✅(补值) |
| 属性(manpower/morale…) | 数值 | NEW c289 |

### 军备变化（KV，4 点）
| 点 | 断言 | case |
|---|---|---|
| 赶制正增量 | `{红夷大炮:+4}` | c092b ✅(补值) |
| 缴获/进贡正 | `{鸟铳:+n}` | NEW c290 |
| 损毁负增量 | `{火铳:-n}` | NEW c291 |

### 势力变化（dict，3 点）
| 点 | 断言 | case |
|---|---|---|
| 威望± | `{houjin:{威望:±}}` | c033 ✅(补值) |
| 实力± | `{houjin:{实力:±}}` | c033 |
| 经济± | `{houjin:{经济:±}}` | c033 |

### 四方动向（KV，7 态度枚举）
| 点 | 断言 | case |
|---|---|---|
| 敌对/摇摆/倾明/潜伏/臣服后金/中立/友好 | `{后金:<态度>}` | NEW c292-294（覆盖主要枚举） |

---

## 四、personnel_secret 档房（5 顶层字段）

### 人物变化（list，多动作）
| 点 | 断言 | case |
|---|---|---|
| 任官 新官职 | `{姓名,新官职:<官名>}` | NEW c300 |
| 罢黜 status | `{状态:罢黜}` | NEW c301 |
| 下狱 | `{状态:下狱}` | NEW c302 |
| 流放 | `{状态:流放}` | NEW c303 |
| 致仕 | `{状态:致仕}` | NEW c304 |
| 身故 | `{状态:身故}` | NEW c305 |
| 降敌 new_power=houjin | `{new_power:houjin}` | c030/c096 ✅(补值) |
| 归正 new_power=ming | `{new_power:ming}` | c039 ✅ |
| 派系 | `{派系:<枚举>}` | NEW c306 |
| 新官署类别 | `{新官署类别:内阁}` | NEW c307 |
| 当前所在 | `{当前所在:陕西}` | NEW c308 |

### 后宫册封（list，位号枚举+准许）
| 点 | 断言 | case |
|---|---|---|
| 位号=贵妃+准许true | `位号:贵妃,准许:true` | NEW c310 |
| 位号其他明制(妃/嫔/才人…) | `位号:<枚举>` | NEW c311 |
| 准许false(非明制) | `准许:false` | NEW c312 |
| 官署类别=后宫 | `官署类别:后宫` | c310 |

### 密令进度（list，2 点）
| 点 | 断言 | case |
|---|---|---|
| 密令编号 | `密令编号:N` | NEW c313（需盘面 active 密令） |

### 密令结案（list，2 枚举）
| 点 | 断言 | case |
|---|---|---|
| 状态=done | `状态:done` | NEW c314（需 pending_review 密令） |
| 状态=failed | `状态:failed` | c043/c105 ✅(补值) |

### 崇祯结局（1 字段，3 枚举）
| 点 | 断言 | case |
|---|---|---|
| abdicate | `expect_emperor_fate:abdicate` | c100 ✅ |
| suicide | `expect_emperor_fate:suicide` | c099 ✅ |
| null(负样本) | `expect_emperor_fate:null` | NEW c315 |

---

## 覆盖统计

- 已有带值校验：~25 点（标 ✅）
- 需新增/补强：~110 点（标 NEW / 补值）
- 新增 case 编号段：c200–c315（避开现有 c001–c107）
