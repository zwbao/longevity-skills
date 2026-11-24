# 来源文件核查

全文：[Nature正式文章](https://www.nature.com/articles/s43587-026-01270-4)，已读取Main、
Results、Methods、Extended Data、Data availability、Competing interests及全部附件入口。
没有本机浙大缓存。网页工具的Nature身份重定向失败后，公开HTML直接下载成功。
所有科学参数来自该正式全文及其附件，不来自新闻或预印本。

## 附件内容与列名

- MOESM1：补充讨论1–3、Supplementary Fig.1、Tables1–7全部打开；图片表格
  按PDF第5–7页视觉读取。表1/5/6列Covariate、All/Young/Older下的Coefficient和p-value、
  Interaction Term p-value；表2为Variable/VIF；表3列见contract；表4为Label及
  4th Ventricle Volume (Y)、Area at bottom slice (Y)、Total Ventricular Volume (Y)、
  Gray Matter Volume (M2)四协变量的P值；表7为Young/Older的人数、性别、年龄和药物类别。
- MOESM2：Reporting Summary为扫描PDF，四页均渲染并OCR读取；没有新模型系数。
- MOESM3：Peer Review File已打开并核对中介模型、控制分析和数据方法相关讨论；
  没有另行发布个人预测模型入口。
- MOESM4/Fig.2：12张表，8张频谱表列frequencies，4张带功率表列
  wake_power、n1_power、n2_power、n3_power、nrem_power。
- MOESM5/Fig.3：4张表，change_data_young/older列change_gm、change_csf；
  all_segments_correlations_young/older列lags。
- MOESM6/Fig.4：10张表，6张按人EEG表按电极Fp1…FT10排列，2张change表列
  change_csf、change_delta，2张相关表列lags。表名包含change，不因此改写Fig.5的NREM变量定义。
- MOESM7/Fig.5：mediation_data一张表，列X、Y、M1、M2。X为实际年龄；Y/M1/M2
  为NREM CSF/额叶EEG/灰质BOLD功率。有空单元格，不填零，不重拟合系数。
- MOESM8/Fig.6：16张表，EEG/BOLD/CSF视觉任务时序及屏气BOLD/CSF时序列time；
  其余表为evoked_csf/nrem_power_csf、cvr/lag、gm_cvr/nrem_power_csf。
- MOESM9/Fig.7：年轻/老年两张表，frontal_GrayVol_eTIV、nrem_power_csf。

全部xlsx已用ZIP/XML读取所有工作表并导出临时文本，未把参与者数据复制入仓库。

## 公开代码与访问限制

- [LewisNeuro/HRAN](https://github.com/LewisNeuro/HRAN)已克隆并读README和源码目录，
  commit `35e5dcd92f315f12e11533e5e3faf253fe7abb0a`；是预处理工具，未执行MATLAB完整流程。
- [phys2cvr Zenodo 7336002](https://doi.org/10.5281/zenodo.7336002)的API与网页403，
  web工具cache miss；期刊给出的physiopy/phys2cvr路径不可克隆。
  已取得当前[smoia/phys2cvr](https://github.com/smoia/phys2cvr)，commit
  `47ea1873af4454b7d3aa005729a1176523a4596b`，核对为CVR回归及lag工具。
  未声称取得论文引用的0.18.6归档版本，也不使用该软件的参数。
- [peakdet Zenodo 13359249](https://doi.org/10.5281/zenodo.13359249)的API/网页403，
  web工具429；已取得[physiopy/peakdet](https://github.com/physiopy/peakdet)，commit
  `d4a9f42b6db6365be230b055a6cce6f93ce4be8e`，核对为生理峰检测工具；
  远程0.3.0标签指向`f25c64549d7d4a973bb2d173a925b42b276e55fc`。
- 正文Data availability声明源数据随文提供，其他支持数据向通讯作者合理申请。
  Reporting Summary引用Methods中的公开软件，没有独立论文专属代码链接。
  没有将访问失败的归档写成“没有系数”；本技能所有必需系数已从表3直接取得，
  日间CVR软件和原始MRI数据不参与本计算。

## 下载文件指纹

核查日期：2026-11-24。所有原始文件只下载到临时目录，仓库仅保留表3的小型转录。

- [Supplementary Information（含表 1–7）](https://static-content.springer.com/esm/art%3A10.1038%2Fs43587-026-01270-4/MediaObjects/43587_2026_1270_MOESM1_ESM.pdf)：已打开；SHA-256 `b074831261da9705d9f1c12428ad15379fe3f3212fb21564dfca45e3d2036e57`。
- [Reporting Summary](https://static-content.springer.com/esm/art%3A10.1038%2Fs43587-026-01270-4/MediaObjects/43587_2026_1270_MOESM2_ESM.pdf)：已打开；SHA-256 `c2d7a381ad4fdfdf801e0cfdefaf75cf06955a4839b2e0fb81f9f655146774d0`。
- [Peer Review File](https://static-content.springer.com/esm/art%3A10.1038%2Fs43587-026-01270-4/MediaObjects/43587_2026_1270_MOESM3_ESM.pdf)：已打开；SHA-256 `2009ebfedb93632f7736adaed10b95b2388847aed4593711e49101d51e2fecd9`。
- [Source Data Fig. 2](https://static-content.springer.com/esm/art%3A10.1038%2Fs43587-026-01270-4/MediaObjects/43587_2026_1270_MOESM4_ESM.xlsx)：已打开；SHA-256 `1ac8731e28c881f1a02e1907c4e9898d51cda47a5831addf3813d5b79abddbd8`。
- [Source Data Fig. 3](https://static-content.springer.com/esm/art%3A10.1038%2Fs43587-026-01270-4/MediaObjects/43587_2026_1270_MOESM5_ESM.xlsx)：已打开；SHA-256 `8df0dc2a45f4316890ae4187caa115dc8365934ea2e59f5359375cbc17c99796`。
- [Source Data Fig. 4](https://static-content.springer.com/esm/art%3A10.1038%2Fs43587-026-01270-4/MediaObjects/43587_2026_1270_MOESM6_ESM.xlsx)：已打开；SHA-256 `fc70fc7002da47d97c9c12b4ef523d620a40d13cdee4c138554c3676072fb468`。
- [Source Data Fig. 5](https://static-content.springer.com/esm/art%3A10.1038%2Fs43587-026-01270-4/MediaObjects/43587_2026_1270_MOESM7_ESM.xlsx)：已打开；SHA-256 `1b7eb82649e3404a47ff699f0d66c73c6fa0382a3ddc84bbdb231730dc49d632`。
- [Source Data Fig. 6](https://static-content.springer.com/esm/art%3A10.1038%2Fs43587-026-01270-4/MediaObjects/43587_2026_1270_MOESM8_ESM.xlsx)：已打开；SHA-256 `e480090fda7a9df7adcd5f4459561b7d87f5f9daa2180510c8fdd2b8554cd9af`。
- [Source Data Fig. 7](https://static-content.springer.com/esm/art%3A10.1038%2Fs43587-026-01270-4/MediaObjects/43587_2026_1270_MOESM9_ESM.xlsx)：已打开；SHA-256 `c5bfd6cf058de7b737cc141987c5ed5f1ffda0f23ad5cc41a412f4aa864aa178`。
