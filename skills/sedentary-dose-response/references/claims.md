# 证据与实现核对

研究：Patterson 等，European Journal of Epidemiology 33:811–829，2018，doi:10.1007/s10654-018-0380-1。Europe PMC/ PubMed出版类型包含Meta-Analysis和Systematic Review；本技能`evidence=review`。这是成人前瞻性队列的系统综述和剂量反应荟萃分析，不是随机干预试验、临床个体风险预测模型或原始队列开发/验证研究。

全部样本组：34项研究、1,331,468名独立参与者；57项暴露—结局分析，不将重复进入不同结局的队列相加。地域为北美17项、欧洲9项、澳大利亚4项、亚洲4项；31项自报暴露、3项客观测量。3项全男性、5项全女性（后者来自4个队列）。平均随访8.9年，范围2–31年。没有独立的模型推导集或个人风险外部验证集。另用2012年Health Survey for England的17岁以上调查参与者演示电视的群体归因分数；该模拟不进入个人查表。

正文表2的结局样本（病例数/基线人数，不是互不重叠的人群）：全因死亡110,395/1,138,042，心血管死亡24,042/667,524，癌症死亡35,241/684,673，新发2型糖尿病17,552/400,292。对照是各队列的较低暴露组；个人表的参照由附表7–8归一化首行决定，不当作未患病对照组人数。

物种：人（human / Homo sapiens），论文没有作者进行的动物实验。纳入规则为一般人群中不以已确诊疾病入组的成人；个别队列按既往病史调整而不是全部排除，不能把所有参与者称为完全健康。

利益冲突：正文Conflict of interest声明作者提交ICMJE表格，过去三年无可能对本研究有利益的机构财务关系，无其他可能影响研究的关系或活动；同时该段写“no support from any organisation for the submitted work”。Funding/Acknowledgements另列British Heart Foundation、MRC、Cancer Research UK、ESRC、NIHR、Wellcome Trust等支持，资助方未参与设计、实施和报告。保留这两个声明的区别，不概括为“无资助”，未见本文相关专利/企业受雇披露。

|论文声称什么|补充材料实际有什么|代码实际算什么|同名或相近项目|
|---|---|---|---|
|久坐/电视与结局的关系经体力活动调整后部分仍存在|附表7–8为PA调整后非线性模型的已印出时长输出|个人时长查印刷RR和CI；年龄性别不再次校正|不同于后续加速度计久坐荟萃分析，不混用参数|
|全因/心血管死亡在较高时长段关联更强|附表5有四个切点及整段每小时RR/CI|每暴露、每结局分别判断，等于阈值归低段|不是公共卫生指南或连续久坐休息规则|
|电视与癌症死亡的线性关联|摘要写PA调整后1.03 (1.02–1.04)，正文及表2为1.02 (1.01–1.03)；附表6 Summary Estimate上限另写1.02|不使用这些线性数重建曲线，使用附表8；记录摘要/正文/附表差异|不是所有癌症发病风险|
|总久坐与癌症死亡未达统计显著|正文表2调整后线性p=0.268；附表7仍印非线性RR/CI|仍可查表但报告保留未达显著的解释|非无风险证明|
|电视与糖尿病接近线性，但存在形状偏离|正文非线性p=0.066，附表8完整非线性输出|保留附表8，不强制线性，也不把4小时当确定糖尿病切点|不是糖尿病诊断器|
|计算英国电视暴露的群体归因分数|方法依赖HSE暴露比例、调查权重、因果假设及模拟|不实现PAF；没有把群体百分比当个人绝对概率|不是个人健康寿命预测|

正文称某些异质性为0%的概括与表2中相应PA调整结果并非全部一致；实现不使用异质性指标作为个人输出。附表2/3的原始剂量赋值精度与附表7/8显示精度可能不同（例如6.44与6.43、13.75与13.74）；查表以附表7/8印出的最终输出时长为准，不自行修正。

## 正文表1的研究组索引

下表按结局保留作者、队列、事件及原表基线人数/随访年数；同一研究可多次出现。人数栏保留原文排版（例如`47,53`、`22,2497`），不拿这些排版值参与计算。`b`为正文表1的随访脚注。参考文献编号与正文一致。

|作者|国家/队列|暴露（事件）|原表n/随访年|
|---|---|---|---|

### All-cause mortality

|作者|国家/队列|暴露（事件）|原表n/随访年|
|---|---|---|---|
| Chau et al. [40] | Norway/HUNT3 | Total sitting (640),TV viewing (684) | 42,077/3.3 |
| Kim et al. [45] | USA/Multiethnic Cohort Study (MEC) | Total sitting (19,143),TV viewing (19,143) | 134,596/13.7 |
| Pulsford et al. [66] | UK/Whitehall 2 | Total sitting (450),TV viewing (324) | 5132/15.7 |
| Ensrud et al. [42] | USA/Osteoporotic Fractures in Men Study (MrOS) | Total sitting—accelerometer measured (409) | 2918/4.5 |
| Fox et al. [51] | UK/OPAL | Total sitting—accelerometer measured (32) | 208/4.2 |
| Inoue et al. [55] | Japan/Japan Public Health Center-based prospective study group | Total sitting (4564) | 83,034/8.7 |
| Katzmarzyk et al. [56] | Canada/Canada Fitness Survey | Total sitting (1832) | 17,013/12.0 |
| Matthews et al. [60] | USA/Southern Community Cohort Study | Total Sitting (5007) | 64,304/6.4 |
| Matthews et al. [62] | USA/NIH-AARP Diet and Health Study | Total sitting (12,201) | 154,614/6.8 |
| Pavey et al. [63] | Australia/Australian Longitudinal Study on Women’s Health | Total sitting (1364) | 47,53/6.0 |
| Petersen et al. [64] | Denmark/Danish Health Examination Survey | Total sitting (1074) | 71,363/5.4 |
| Schmid et al. [67] | USA/National Health and Nutrition Examination Survey | Total sitting—accelerometer measured (112) | 1677/2.9 |
| Seguin et al. [68] | USA/Women’s Health Initiative (WHI) Observational Study (OS) and Extension Study (ES). | Total sitting (13,316) | 92,234/12.2 |
| van der Ploeg et al. [71] | Australia/45 and up cohort | Total sitting (4405) | 22,2497/2.8 |
| Basterra-Gortari et al. [39] | Spain/The SUN Cohort | TV viewing (97) | 13,284/8.2 |
| Dunstan et al. [49] | Australia/The Australian Diabetes, Obesity and Lifestyle Study (AusDiab) | TV viewing (284) | 8800/6.6 |
| Keadle et al. [57] | USA/NIH-AARP Diet and Health Study | TV viewing (36,590) | 221,426/14.1 |
| Matthews et al. [61] | USA/NIH-AARP Diet and Health Study | TV viewing (17,044) | 240,819/8.5 |
| Muennig et al. [46] | USA/General Socal Survey | TV viewing (2048) | 9344/b |
| Suzuki et al. [70] | Japan/Japan Collaborative cohort study | TV viewing (9880) | 110,792/b |
| Wijndaele et al. [48] | UK/EPIC-Norfolk | TV viewing (1270) | 13,197/9.5 |

### 
CVD mortality


|作者|国家/队列|暴露（事件）|原表n/随访年|
|---|---|---|---|
| Kim et al. [45] | USA/Multiethnic Cohort Study (MEC) | Total sitting (6535),TV viewing (6535) | 134,596/13.7 |
| Ensrud et al. [42] | USA/Osteoporotic Fractures in Men Study (MrOS) | Total sitting– accelerometer measured (138) | 2918/4.5 |
| Katzmarzyk et al. [56] | Canada/Canada Fitness Survey | Total sitting (759) | 17,013/12.0 |
| Matthews et al. [60] | USA/Southern Community Cohort Study | Total Sitting (1376) | 64,304/6.4 |
| Matthews et al. [62] | USA/NIH-AARP Diet and Health Study | Total sitting (3339) | 154,614/6.8 |
| Seguin et al. [68] | USA/Women’s Health Initiative (WHI) Observational Study (OS) and Extension Study (ES). | Total sitting (3878) | 92,234/12.2 |
| Dunstan et al. [49] | Australia/The Australian Diabetes, Obesity and Lifestyle Study (AusDiab) | TV viewing (87) | 8800/6.6 |
| Ikehara et al. [54] | Japan/The Japan Collaborative Cohort Study | TV viewing (5835) | 85,899/19.2 |
| Matthews et al. [61] | USA/NIH-AARP Diet and Health Study | TV viewing (4684) | 240,819/8.5 |
| Warren et al. [47] | USA/ACLS Cohort | TV viewing (377) | 7744/b |
| Wijndaele et al. [48] | UK/EPIC-Norfolk | TV viewing (373) | 13,197/9.5 |

### 
Cancer mortality


|作者|国家/队列|暴露（事件）|原表n/随访年|
|---|---|---|---|
| Kim et al. [45] | USA/Multiethnic Cohort Study (MEC) | Total sitting (6697),TV viewing (6697) | 134,596/13.7 |
| Ensrud et al. [42] | USA/Osteoporotic Fractures in Men Study (MrOS) | Total sitting– accelerometer measured (129) | 2918/4.5 |
| Katzmarzyk et al. [56] | Canada/Canada Fitness Survey | Total sitting (547) | 17,013/12.0 |
| Matthews et al. [60] | USA/Southern Community Cohort Study | Total Sitting (1227) | 64,304/6.4 |
| Matthews et al. [62] | USA/NIH-AARP Diet and Health Study | Total sitting (4507) | 154,614/6.8 |
| Seguin et al. [68] | USA/Women’s Health Initiative (WHI) Observational Study (OS) and Extension Study (ES). | Total sitting (4759) | 92,234/12.2 |
| Dunstan et al. [49] | Australia/The Australian Diabetes, Obesity and Lifestyle Study (AusDiab) | TV viewing (125) | 8800/6.6 |
| Keadle et al. [57] | USA/NIH-AARP Diet and Health Study | TV viewing (15,161) | 221,426/14.1 |
| Matthews et al. [61] | USA/NIH-AARP Diet and Health Study | TV viewing (7652) | 240,819/8.5 |
| Suzuki et al. [70] | Japan/Japan Collaborative cohort study | TV viewing (3787) | 110,792/b |
| Wijndaele et al. [48] | UK/EPIC-Norfolk | TV viewing (570) | 13,197/9.5 |

### 
Incident type 2 diabetes


|作者|国家/队列|暴露（事件）|原表n/随访年|
|---|---|---|---|
| Ding et al. [41] | Australia/45 and up | Total sitting (829) | 54,997/3.4 |
| Gibbs et at [43] | USA/The Coronary Artery Risk Development in Young Adults (CARDIA) Study | Total sitting (201) | 1869/5 |
| Manini et al. [59] | USA/Women’s Health Initiative (WHI) Observational Study (OS) | Total sitting (7426) | 88,250/11.1 |
| Petersen et al. [65] | Denmark/DANHES | Total sitting (1790) | 72,608/4.9 |
| Anjana et al. [38] | India/Chennai urban rural epidemiology study (CURES-142) | TV viewing (385) | 1376/10 |
| Ford et al. [50] | Germany/EPIC–Potsdam | TV viewing (927) | 23,855/7.8 |
| Hu et al. [52] | USA/The health professional follow-up study (HPFS) | TV viewing (767) | 31,379/8.0 |
| Hu et al. [53] | USA/Nurses’ Health Study | TV viewing (1515) | 68,497/5.3 |
| Joseph et al. [44] | USA/Multi-ethnic study of atherosclerosis (MESA) | TV viewing (655) | 5829/11.1 |
| Krishnan et al. [58] | USA/The Black Women’s Health Study (BWHS) | TV viewing (2928) | 45,668/4.0 |
| Smith et al. [69] | UK/English Longitudinal Study of Aging—ELSA | TV viewing (129) | 5964/2.0 |

aWhere a range is presented this was age range of included participantsbInformation not available
