# 输入

CSV 表头 `marker,value,unit`。每行一个指标，单位与别名以 skill.json 为准。所有 0/1 标志均需明确回答，不能以 0 代替未知。两类运动时长分别记录一周累计整数分钟，不重复计数；睡眠是平均每晚小时数。

| key | 说明 |
|---|---|
| mepa_score | 已完成成人16项MEPA总分（整数）；不是MEDAS或儿童问卷 |
| moderate_min_week / vigorous_min_week | 一周中等/剧烈活动累计分钟；无活动也需明确填0 |
| smoking_status | 0从不吸烟；1戒烟≥5年；2戒烟1至<5年；3戒烟<1年；4当前吸烟 |
| inhaled_nicotine | 当前吸入式尼古丁产品，包括电子烟：0否/1是 |
| indoor_smoke | 家中有主动在室内吸烟者：0否/1是 |
| sleep_h | 平均每晚睡眠小时 |
| bmi_kg_m2 | BMI，kg/m² |
| bmi_asian_scale | 0使用通用成人尺度；1使用论文亚洲/太平洋祖源尺度；明确选择，不根据语言推断 |
| non_hdl_mg_dl | 非HDL胆固醇；不是LDL或总胆固醇；可由同次总胆固醇减HDL后提供 |
| lipid_treated | 该血脂是否为药物治疗后水平 |
| diabetes | 医生确诊糖尿病史；不得从本次化验值推断 |
| fasting_glucose_mg_dl / hba1c_pct | 无糖尿病史至少一个；有糖尿病史必须有HbA1c；若均提供须核实一致性 |
| sbp_mmhg / dbp_mmhg | 规范测量的平均收缩压/舒张压 |
| bp_treated | 该血压是否为降压药治疗后水平 |
| sleep_apnea_penalty | 可选，医生已决定因未充分治疗的睡眠呼吸暂停应用扣分：0/1 |
| prediabetes_penalty | 可选，医生已决定对接受糖尿病前期治疗且血糖已正常者应用扣分：0/1 |

年龄通过 `--age` 输入。药物类别、数量和剂量不作为情景输入。所有临床测量须能代表同一评估时期。没有MEPA总分时列为待补问卷；本实现不自动解释附录Table C酒精条目中的逻辑措辞，不据此建议饮酒。

`--targets` 只接受有当前值的饮食分、运动时长、睡眠时长、BMI、非HDL、血糖、HbA1c、血压。所有目标及逐项变化的中间情景都须通过同样检查。使用联合情景时，两项血糖不能制造互相矛盾的分档。
