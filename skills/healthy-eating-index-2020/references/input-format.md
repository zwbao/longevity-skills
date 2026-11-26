# 饮食表输入口径

13项必须来自同一记录期间和同一总能量口径；年龄另以`--age`给出。所有食物密度比均先由规范的食物当量分析求得。没有现成的分析数据时，不用照片、菜名或任意克数猜换算。

| item | 中文名称 | 数值的定义 | unit |
|---|---|---|---|
| total_fruits_density_ratio | 总水果 | 实际摄入密度 ÷ (1 cup equiv. per 1,000 kcal) | 1 |
| whole_fruits_density_ratio | 完整水果 | 实际摄入密度 ÷ (1 cup equiv. per 1,000 kcal) | 1 |
| total_vegetables_density_ratio | 总蔬菜 | 实际摄入密度 ÷ (1 cup equiv. per 1,000 kcal) | 1 |
| greens_beans_density_ratio | 深绿色蔬菜和豆类 | 实际摄入密度 ÷ (1 cup equiv. per 1,000 kcal) | 1 |
| whole_grains_density_ratio | 全谷物 | 实际摄入密度 ÷ (1 oz equiv. per 1,000 kcal) | 1 |
| dairy_density_ratio | 乳制品 | 实际摄入密度 ÷ (1 cup equiv. per 1,000 kcal) | 1 |
| total_protein_density_ratio | 总蛋白质食物 | 实际摄入密度 ÷ (1 oz equiv. per 1,000 kcal) | 1 |
| seafood_plant_density_ratio | 海鲜和植物蛋白质食物 | 实际摄入密度 ÷ (1 oz equiv. per 1,000 kcal) | 1 |
| fatty_acids_ratio | 不饱和与饱和脂肪酸比 | (PUFA+MUFA)/SFA摄入质量比，SFA>0 | 1 |
| refined_grains_density_ratio | 精制谷物 | 实际摄入密度 ÷ (1 oz equiv. per 1,000 kcal) | 1 |
| sodium_density_ratio | 钠 | 实际摄入密度 ÷ (1 gram per 1,000 kcal) | 1 |
| added_sugars_energy_pct | 添加糖供能比例 | 占全部能量的百分数 | % |
| saturated_fats_energy_pct | 饱和脂肪供能比例 | 占全部能量的百分数 | % |

同一个字段用英文名称或中文名称也可匹配，但须显式填写单位。血液化验中的钠、血脂不能作为本表输入。杯当量和盎司当量必须来自食品当量分析，不接受通用克数或容量换算。

两项百分比若用单位`1`，数字必须为供能分数（例如0.065对应6.5%），程序精确乘100；否则填`%`。密度比和脂肪酸比值仅接受`1`，不自动换算全天值。

以下仅为图3满分端点的算术示范，不是一份推荐菜单，不得填作个人测量。保存为CSV可以演示报告格式：

```csv
item,value,unit
total_fruits_density_ratio,0.8,1
whole_fruits_density_ratio,0.4,1
total_vegetables_density_ratio,1.1,1
greens_beans_density_ratio,0.2,1
whole_grains_density_ratio,1.5,1
dairy_density_ratio,1.3,1
total_protein_density_ratio,2.5,1
seafood_plant_density_ratio,0.8,1
fatty_acids_ratio,2.5,1
refined_grains_density_ratio,1.8,1
sodium_density_ratio,1.1,1
added_sugars_energy_pct,6.5,%
saturated_fats_energy_pct,8,%
```

真实使用时每行换成个人记录值，零摄入和缺失要区分；缺失不得填零。此示范合计100分，只验证评分表端点。单日分数不能当成长期习惯或充足摄入证明。

目标表使用相同三列，可仅列部分输入；未列的项目保持当前值。目标不是工具推荐，若食物子组超过总组，须连同相关总组提供一致的数据。
