# Extractor 全字段覆盖测试报告

- 跑 case：**67**　PASS **64** / FAIL **3** / ERROR **0**
- 顶层字段总数：**22**
- 耗时：2054s

## 一、字段遗漏校验

✅ 全部顶层字段都有 case 覆盖（每个字段至少被一个 case 的 expect_fields 引用）。

✅ 所有被期望的字段在实测中均至少命中过一次。

## 二、字段覆盖矩阵

| 顶层字段 | 期望次数 | 实测命中次数 | 命中 case |
|---|---|---|---|
| ✅ 国势变化 | 4 | 31 | c032_xinjianjun_panjun、c050_combo_chaojia_bushang、c051_combo_zhenzai_jieji、c052_combo_qingdang、c054_combo_gongcheng_xinli_caiche、c055_combo_xianluo_jundui… |
| ✅ 钱粮收支 | 8 | 14 | c032_xinjianjun_panjun、c050_combo_chaojia_bushang、c051_combo_zhenzai_jieji、c052_combo_qingdang、c056_combo_shili_sifang、c058_combo_jiean_diguoxiuzheng… |
| ✅ 财政制度变化 | 7 | 7 | c066_zhidu_shewei、c066b_zhidu_zengjian_yuan、c066c_zhidu_yuee_shewei、c066d_zhidu_yuee_zengjian、c066e_zhidu_yuee_bili、c066f_zhidu_zhizao_zeng… |
| ✅ 新立月度收支 | 4 | 5 | c057_combo_xinli_keji_bumen、c067_xinli_qishui、c068_xinli_jintie、c068a_xinli_dingfu、c068b_xinli_mushui |
| ✅ 裁撤月度收支 | 2 | 3 | c054_combo_gongcheng_xinli_caiche、c068c_caiche_zhizao、c069_caiche_yanke |
| ✅ 派系变化 | 2 | 34 | c043_miling_jiean、c050_combo_chaojia_bushang、c052_combo_qingdang、c054_combo_gongcheng_xinli_caiche、c055_combo_xianluo_jundui、c056_combo_shili_sifang… |
| ✅ 阶级变化 | 4 | 38 | c032_xinjianjun_panjun、c043_miling_jiean、c050_combo_chaojia_bushang、c051_combo_zhenzai_jieji、c052_combo_qingdang、c053_combo_xinjun_renshi… |
| ✅ 地区变化 | 10 | 22 | c032_xinjianjun_panjun、c051_combo_zhenzai_jieji、c053_combo_xinjun_renshi、c055_combo_xianluo_jundui、c056_combo_shili_sifang、c060_combo_caiche_jiazheng… |
| ✅ 局势推进 | 1 | 67 | c032_xinjianjun_panjun、c043_miling_jiean、c050_combo_chaojia_bushang、c051_combo_zhenzai_jieji、c052_combo_qingdang、c053_combo_xinjun_renshi… |
| ✅ 新立局势 | 5 | 10 | c054_combo_gongcheng_xinli_caiche、c055_combo_xianluo_jundui、c057_combo_xinli_keji_bumen、c078_xinli_zhaofu、c079_xinli_an、c080_xinli_bingzhi… |
| ✅ 撤销局势 | 1 | 1 | c085_chexiao_2 |
| ✅ 结案局势 | 3 | 3 | c058_combo_jiean_diguoxiuzheng、c083_jiean_failed、c084_jiean_diguo |
| ✅ 军队变化 | 5 | 17 | c032_xinjianjun_panjun、c050_combo_chaojia_bushang、c051_combo_zhenzai_jieji、c052_combo_qingdang、c055_combo_xianluo_jundui、c056_combo_shili_sifang… |
| ✅ 新建军队 | 5 | 5 | c032_xinjianjun_panjun、c053_combo_xinjun_renshi、c089_xinjianjun_houjin、c090_xinjianjun_menggu、c107_combo_xinjun_junbei |
| ✅ 军备变化 | 4 | 4 | c092a_junbei_ganzhi、c092b_junbei_huojiao、c092c_junbei_aomen、c107_combo_xinjun_junbei |
| ✅ 势力变化 | 2 | 15 | c032_xinjianjun_panjun、c050_combo_chaojia_bushang、c051_combo_zhenzai_jieji、c052_combo_qingdang、c055_combo_xianluo_jundui、c056_combo_shili_sifang… |
| ✅ 四方动向 | 3 | 20 | c032_xinjianjun_panjun、c050_combo_chaojia_bushang、c051_combo_zhenzai_jieji、c052_combo_qingdang、c055_combo_xianluo_jundui、c056_combo_shili_sifang… |
| ✅ 人物变化 | 8 | 12 | c032_xinjianjun_panjun、c050_combo_chaojia_bushang、c052_combo_qingdang、c053_combo_xinjun_renshi、c058_combo_jiean_diguoxiuzheng、c061_chaojia_huanguan… |
| ✅ 后宫册封 | 2 | 2 | c059_combo_hougong_renshi、c097_hougong_feijun |
| ✅ 密令进度 | 1 | 1 | c104_miling_fuzuoyong2 |
| ✅ 密令结案 | 2 | 2 | c043_miling_jiean、c105_miling_jiean2 |
| ✅ 崇祯结局 | 2 | 2 | c099_jieju_suicide、c100_jieju_abdicate |

## 三、逐 case 明细

| case | 状态 | 期望 | 实测命中 | 缺失 | 多余 | 备注 |
|---|---|---|---|---|---|---|
| c032_xinjianjun_panjun | ✅ | 新建军队 | 人物变化、军队变化、势力变化、四方动向、国势变化、地区变化、局势推进、新建军队、钱粮收支、阶级变化 | — | 人物变化、军队变化、势力变化、四方动向、国势变化、地区变化、局势推进、钱粮收支、阶级变化 |  |
| c043_miling_jiean | ✅ | 密令结案 | 密令结案、局势推进、派系变化、阶级变化 | — | 局势推进、派系变化、阶级变化 |  |
| c050_combo_chaojia_bushang | ✅ | 钱粮收支、军队变化 | 人物变化、军队变化、势力变化、四方动向、国势变化、局势推进、派系变化、钱粮收支、阶级变化 | — | 人物变化、势力变化、四方动向、国势变化、局势推进、派系变化、阶级变化 |  |
| c051_combo_zhenzai_jieji | ✅ | 钱粮收支、地区变化、阶级变化 | 军队变化、势力变化、四方动向、国势变化、地区变化、局势推进、钱粮收支、阶级变化 | — | 军队变化、势力变化、四方动向、国势变化、局势推进 |  |
| c052_combo_qingdang | ✅ | 钱粮收支、人物变化、派系变化 | 人物变化、军队变化、势力变化、四方动向、国势变化、局势推进、派系变化、钱粮收支、阶级变化 | — | 军队变化、势力变化、四方动向、国势变化、局势推进、阶级变化 |  |
| c053_combo_xinjun_renshi | ✅ | 人物变化、新建军队 | 人物变化、地区变化、局势推进、新建军队、阶级变化 | — | 地区变化、局势推进、阶级变化 |  |
| c054_combo_gongcheng_xinli_caiche | ✅ | 新立局势、裁撤月度收支 | 国势变化、局势推进、新立局势、派系变化、裁撤月度收支 | — | 国势变化、局势推进、派系变化 |  |
| c055_combo_xianluo_jundui | ✅ | 地区变化、军队变化 | 军队变化、势力变化、四方动向、国势变化、地区变化、局势推进、新立局势、派系变化、阶级变化 | — | 势力变化、四方动向、国势变化、局势推进、新立局势、派系变化、阶级变化 |  |
| c056_combo_shili_sifang | ✅ | 势力变化、四方动向、国势变化 | 军队变化、势力变化、四方动向、国势变化、地区变化、局势推进、派系变化、钱粮收支、阶级变化 | — | 军队变化、地区变化、局势推进、派系变化、钱粮收支、阶级变化 |  |
| c057_combo_xinli_keji_bumen | ✅ | 新立局势 | 国势变化、局势推进、新立局势、新立月度收支、派系变化 | — | 国势变化、局势推进、新立月度收支、派系变化 |  |
| c058_combo_jiean_diguoxiuzheng | ✅ | 结案局势 | 人物变化、势力变化、四方动向、国势变化、局势推进、派系变化、结案局势、钱粮收支、阶级变化 | — | 人物变化、势力变化、四方动向、国势变化、局势推进、派系变化、钱粮收支、阶级变化 |  |
| c059_combo_hougong_renshi | ❌ | 后宫册封、人物变化 | 后宫册封、局势推进 | 人物变化 | 局势推进 |  |
| c060_combo_caiche_jiazheng | ✅ | 地区变化 | 军队变化、势力变化、四方动向、国势变化、地区变化、局势推进、派系变化、阶级变化 | — | 军队变化、势力变化、四方动向、国势变化、局势推进、派系变化、阶级变化 |  |
| c061_chaojia_huanguan | ✅ | 钱粮收支 | 人物变化、国势变化、局势推进、派系变化、钱粮收支 | — | 人物变化、国势变化、局势推进、派系变化 |  |
| c062_bushang_xuanda | ✅ | 钱粮收支 | 军队变化、局势推进、钱粮收支 | — | 军队变化、局势推进 |  |
| c063_bushang_jizhen | ✅ | 钱粮收支 | 军队变化、四方动向、局势推进、钱粮收支 | — | 军队变化、四方动向、局势推进 |  |
| c064_jinwei_xiaoe | ✅ | 钱粮收支 | 局势推进、钱粮收支、阶级变化 | — | 局势推进、阶级变化 | 小额换算：四千六百两=0.46万两 |
| c065_jiazheng_yanshui | ✅ | 地区变化 | 地区变化、局势推进 | — | 局势推进 |  |
| c066_zhidu_shewei | ✅ | 财政制度变化 | 局势推进、派系变化、财政制度变化、阶级变化 | — | 局势推进、派系变化、阶级变化 | 口径=设为原始值：数值即新值 |
| c066b_zhidu_zengjian_yuan | ✅ | 财政制度变化 | 局势推进、派系变化、财政制度变化、阶级变化 | — | 局势推进、派系变化、阶级变化 | 口径=增减原始值：数值为增量 |
| c066c_zhidu_yuee_shewei | ✅ | 财政制度变化 | 局势推进、财政制度变化 | — | 局势推进 | 口径=月额设为：数值=新总额万两 |
| c066d_zhidu_yuee_zengjian | ✅ | 财政制度变化 | 局势推进、财政制度变化、阶级变化 | — | 局势推进、阶级变化 | 口径=月额增减：数值为月额增量带符号 |
| c066e_zhidu_yuee_bili | ✅ | 财政制度变化 | 局势推进、派系变化、财政制度变化、阶级变化 | — | 局势推进、派系变化、阶级变化 | 口径=月额按比例增减：数值=百分比，削为负 |
| c066f_zhidu_zhizao_zeng | ✅ | 财政制度变化 | 局势推进、财政制度变化 | — | 局势推进 | 增额方向：月额增减正数 |
| c067_xinli_qishui | ✅ | 新立月度收支 | 局势推进、新立月度收支、阶级变化 | — | 局势推进、阶级变化 |  |
| c068_xinli_jintie | ✅ | 新立月度收支 | 军队变化、势力变化、四方动向、局势推进、新立月度收支 | — | 军队变化、势力变化、四方动向、局势推进 |  |
| c068a_xinli_dingfu | ✅ | 新立月度收支 | 局势推进、新立月度收支 | — | 局势推进 | 动态人头税：formula=per_basis,basis=population（键由LLM自拟dingfu_base不 |
| c068b_xinli_mushui | ✅ | 新立月度收支 | 国势变化、地区变化、局势推进、新立月度收支、派系变化、阶级变化 | — | 国势变化、地区变化、局势推进、派系变化、阶级变化 | 动态田亩税：basis=registered_land（落英文） |
| c068c_caiche_zhizao | ✅ | 裁撤月度收支 | 国势变化、局势推进、派系变化、裁撤月度收支 | — | 国势变化、局势推进、派系变化 | 裁撤的是支出/收入固定科目，与c010矿税(收入)互补，此为内库收入项永罢 |
| c069_caiche_yanke | ✅ | 地区变化 | 国势变化、地区变化、局势推进、派系变化、裁撤月度收支、阶级变化 | — | 国势变化、局势推进、派系变化、裁撤月度收支、阶级变化 |  |
| c070_minxin_zheng | ✅ | 国势变化、地区变化 | 国势变化、地区变化、局势推进、钱粮收支、阶级变化 | — | 局势推进、钱粮收支、阶级变化 |  |
| c071_minxin_fu | ❌ | 国势变化 | 军队变化、势力变化、四方动向、局势推进 | 国势变化 | 军队变化、势力变化、四方动向、局势推进 |  |
| c072_paixi_donglin | ✅ | 派系变化、人物变化 | 人物变化、国势变化、局势推进、派系变化 | — | 国势变化、局势推进 |  |
| c073_jieji_junhu | ✅ | 阶级变化 | 军队变化、四方动向、国势变化、地区变化、局势推进、派系变化、钱粮收支、阶级变化 | — | 军队变化、四方动向、国势变化、地区变化、局势推进、派系变化、钱粮收支 |  |
| c074_jieji_shangren | ✅ | 阶级变化 | 国势变化、局势推进、阶级变化 | — | 国势变化、局势推进 |  |
| c075_diqu_fengshou | ✅ | 地区变化 | 国势变化、地区变化、局势推进、阶级变化 | — | 国势变化、局势推进、阶级变化 |  |
| c076_diqu_shoufu | ✅ | 地区变化 | 势力变化、四方动向、国势变化、地区变化、局势推进、派系变化、钱粮收支、阶级变化 | — | 势力变化、四方动向、国势变化、局势推进、派系变化、钱粮收支、阶级变化 |  |
| c077_diqu_fubai | ✅ | 地区变化 | 国势变化、地区变化、局势推进、派系变化、阶级变化 | — | 国势变化、局势推进、派系变化、阶级变化 |  |
| c078_xinli_zhaofu | ✅ | 新立局势 | 局势推进、新立局势 | — | 局势推进 |  |
| c079_xinli_an | ✅ | 新立局势 | 人物变化、国势变化、局势推进、新立局势、派系变化 | — | 人物变化、国势变化、局势推进、派系变化 |  |
| c080_xinli_bingzhi | ✅ | 新立局势 | 局势推进、新立局势、派系变化、阶级变化 | — | 局势推进、派系变化、阶级变化 | 军务章程类改革(非军队实体变化)走新立局势；原 cheat 未明示立issue致LLM当一锤子事 FAIL |
| c081_tuijin_zhonggongcheng | ✅ | 局势推进 | 局势推进、派系变化、阶级变化 | — | 派系变化、阶级变化 |  |
| c083_jiean_failed | ✅ | 结案局势 | 势力变化、四方动向、国势变化、地区变化、局势推进、结案局势、阶级变化 | — | 势力变化、四方动向、国势变化、地区变化、局势推进、阶级变化 | 失败结案：须预置 active issue 方有编号可结案；原缺 sql 致无 issue 可结故 FAIL |
| c084_jiean_diguo | ✅ | 结案局势 | 国势变化、局势推进、派系变化、结案局势、阶级变化 | — | 国势变化、局势推进、派系变化、阶级变化 |  |
| c085_chexiao_2 | ✅ | 撤销局势 | 局势推进、撤销局势 | — | 局势推进 |  |
| c086_jundui_gaibianzhi | ✅ | 军队变化 | 军队变化、四方动向、局势推进、阶级变化 | — | 四方动向、局势推进、阶级变化 |  |
| c087_jundui_caiche | ✅ | 军队变化 | 军队变化、局势推进、阶级变化 | — | 局势推进、阶级变化 |  |
| c088_jundui_chexiao | ✅ | 军队变化 | 军队变化、局势推进 | — | 局势推进 |  |
| c089_xinjianjun_houjin | ✅ | 新建军队 | 局势推进、新建军队、新立局势、派系变化 | — | 局势推进、新立局势、派系变化 |  |
| c090_xinjianjun_menggu | ✅ | 新建军队 | 局势推进、新建军队、新立局势 | — | 局势推进、新立局势 |  |
| c091_shili_zhuangda | ✅ | 势力变化、四方动向 | 势力变化、四方动向、国势变化、地区变化、局势推进、新立局势、阶级变化 | — | 国势变化、地区变化、局势推进、新立局势、阶级变化 |  |
| c092_sifang_chaoxian | ✅ | 四方动向 | 四方动向、地区变化、局势推进、新立局势、派系变化 | — | 地区变化、局势推进、新立局势、派系变化 |  |
| c092a_junbei_ganzhi | ✅ | 军备变化 | 军备变化、局势推进 | — | 局势推进 |  |
| c092b_junbei_huojiao | ✅ | 军备变化 | 军备变化、局势推进 | — | 局势推进 |  |
| c092c_junbei_aomen | ✅ | 军备变化 | 军备变化、局势推进 | — | 局势推进 |  |
| c093_renshi_diaoren | ✅ | 人物变化 | 人物变化、军队变化、地区变化、局势推进、派系变化、阶级变化 | — | 军队变化、地区变化、局势推进、派系变化、阶级变化 |  |
| c094_zhuangtai_zhishi | ✅ | 人物变化 | 人物变化、局势推进、派系变化 | — | 局势推进、派系变化 |  |
| c095_zhuangtai_shengu | ✅ | 人物变化 | 人物变化、军队变化、四方动向、国势变化、地区变化、局势推进、派系变化、阶级变化 | — | 军队变化、四方动向、国势变化、地区变化、局势推进、派系变化、阶级变化 |  |
| c096_yizhu_jiangdi | ❌ | 人物变化 | 势力变化、四方动向、国势变化、局势推进 | 人物变化 | 势力变化、四方动向、国势变化、局势推进 |  |
| c097_hougong_feijun | ✅ | 后宫册封 | 后宫册封、局势推进 | — | 局势推进 |  |
| c099_jieju_suicide | ✅ | 崇祯结局 | 势力变化、四方动向、国势变化、地区变化、局势推进、崇祯结局 | — | 势力变化、四方动向、国势变化、地区变化、局势推进 |  |
| c100_jieju_abdicate | ✅ | 崇祯结局 | 国势变化、局势推进、崇祯结局、派系变化、阶级变化 | — | 国势变化、局势推进、派系变化、阶级变化 |  |
| c103c_neg_zhidu_vs_xianjin | ✅ | 财政制度变化 | 局势推进、派系变化、财政制度变化、阶级变化 | — | 局势推进、派系变化、阶级变化 | 区分『改月度额度』(财政制度变化)与『一次性现金』(钱粮收支)：削禄米是改额度，不产生本月现金流，钱粮收支不得抽 |
| c104_miling_fuzuoyong2 | ✅ | 密令进度 | 国势变化、密令进度、局势推进、派系变化、阶级变化 | — | 国势变化、局势推进、派系变化、阶级变化 |  |
| c105_miling_jiean2 | ✅ | 密令结案 | 密令结案、局势推进、派系变化 | — | 局势推进、派系变化 |  |
| c106_combo_full_neizheng | ✅ | 钱粮收支、地区变化、阶级变化、国势变化 | 国势变化、地区变化、局势推进、派系变化、钱粮收支、阶级变化 | — | 局势推进、派系变化 | 全国不分省加征商税→地区变化『全国』key 摊派；禁止再建新立科目(双账)或写财政制度变化 |
| c107_combo_xinjun_junbei | ✅ | 新建军队、军备变化 | 人物变化、军备变化、地区变化、局势推进、新建军队、阶级变化 | — | 人物变化、地区变化、局势推进、阶级变化 |  |
