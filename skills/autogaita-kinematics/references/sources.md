# 来源及附件核查（2026-11-24）

正式文章：[PNAS](https://www.pnas.org/doi/10.1073/pnas.2534093123)，[PMC13535145](https://pmc.ncbi.nlm.nih.gov/articles/PMC13535145/)，[PubMed](https://pubmed.ncbi.nlm.nih.gov/42636367/)。已读正文 Methods、Results、Discussion、图注和声明。

本机没有用户指定的全文缓存。PNAS 的 41 个附件直链返回 403，PMC 直链返回 HTML 验证页；浏览器 CDP 连接超时。随后成功使用 [Europe PMC supplementaryFiles](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13535145/supplementaryFiles) 取得完整 ZIP（22,293,386 字节），ZIP CRC 检查通过。包含 SI Appendix、S1–S39、Movie S1 和正文图像。没有把缓存或整篇原文复制进仓库。

SI Appendix 共17页，已读扩展方法及全部图注、附件说明；另渲染第6页核查推蹬公式的分母，避免 PDF 文本抽取误读。Movie S1 可解码，时长291.67秒；以30秒间隔抽帧查看工作流、配置与结果显示，没有把视频中的鼠示范当成人体数值验证。

代码：[AutoGaitA v1.3.1](https://github.com/mahan-hosseini/AutoGaitA/tree/v1.3.1)，提交 f3ba2dbc05da350fccf198d32a8ba9d0feff9342；已克隆并读取角度、梯度、归一化、绘图单位、测试与示例目录。正式论文引用的 [Zenodo 15373063](https://zenodo.org/records/15373063) 正是该版本，页面列出的归档名为 mahan-hosseini/AutoGaitA-v1.3.1.zip；采用对应 Git 标签检查源码，未另重复下载其241.4 MB压缩包。当前主分支也检查过（784a2e2a175042fffc180bf59717fc8e6cc73c92），方法基准固定在论文引用版本。

额外开放材料：[MoVi-Toolbox](https://github.com/saeed1262/MoVi-Toolbox) 及其 [BioMotionLab 数据说明页](https://www.biomotionlab.ca/movi/) 已打开，提供原始行为分段与坐标读取工具；这是外部三维行为演示，不是年龄组人体步行原始数据。没有下载完整 MoVi 视频/坐标集合，也没有用其替代本论文人体算例。

## 表格逐份核对

所有39个 XLSX 均打开工作簿和工作表 XML、读取单元格。下表按实际工作表标题记录。PCA Info 的列为 PC 1…，行含 Explained Var. (%) 和 Features；PCA Features 列为 PC n Features / PC n Value；Statistics 列为特征名、Tukey's q、p value、CI、reject、sig. level；S27 列为 Group、ID、PC 1…；S39 为两组 ID、Age、Height (m)、Sex。未找到完整人体逐帧坐标及相应印刷的角度/速度/跨步距离结果，也未找到完整推蹬回归截距与时间项。

| 文件 | 实际工作表 | 行数 | SHA-256 |
|---|---|---:|---|
| pnas.2534093123.sd01.xlsx | S1 - Figure 2m - PCA Info | 553 | `47d1d3c3a9caac7f487d4ae49f4bedd5f7aaf5b8388247f3769352a32bc47d0d` |
| pnas.2534093123.sd02.xlsx | S2 - Figure 2m - PCA Features | 21 | `89615de92e4e68437e322637866f577b107a781874af9a301cceba0de63de6f3` |
| pnas.2534093123.sd03.xlsx | S3 - Figure 3a - PCA Info | 728 | `56dc2e6c799a3f66d62afde4f555b915f7afc39a213ef4d4149bf4ab4c51930f` |
| pnas.2534093123.sd04.xlsx | S4 - Figure 3a - PCA Features | 21 | `cd98a3df0a68d2a7852bfde6a0d18079414c79a8480c1c43e6d3a0022e4b9831` |
| pnas.2534093123.sd05.xlsx | S5 - Figure 3b - PCA Info | 803 | `fe4b3ebd1654e1b72c35394f14dba6cc4a18f55708eb13629130389dc2a4147a` |
| pnas.2534093123.sd06.xlsx | S6 - Figure 3b - PCA Features | 21 | `398d8008f8ac27b664542a9a252e39081e350882239bf7a6ed4bc505b5e230ea` |
| pnas.2534093123.sd07.xlsx | S7 - Figure 3c - PCA Info | 553 | `b42ca39c9776a2cef7a856ce289a1bb0209f716ebc47230b83310472ec6608d8` |
| pnas.2534093123.sd08.xlsx | S8 - Figure 3c - PCA Features | 21 | `e0d0fbe3e060975452b56267e31447ea77a7b6be34a15fc5792819b75e241a8d` |
| pnas.2534093123.sd09.xlsx | S9 - Figure 3d - Statistics | 51 | `45d089ec0ea8c85835ce4efdf9b89c05b29a0812d56047e814d7cff6d36daeea` |
| pnas.2534093123.sd10.xlsx | S10 - Figure 3e - Statistics | 51 | `4c0e2d6560fbed0481cf78d2f782195ec368dd4404e4d3c48c792f20305c2cb0` |
| pnas.2534093123.sd11.xlsx | S11 - Figure 3f - Statistics | 51 | `bcf135f61fc9df334f39be86034249b81ac4482a7dbe4030dbc9ebf940be14ed` |
| pnas.2534093123.sd12.xlsx | S12 - Figure 4d - Statistics  | 101 | `0a9bcc90fe4875b1a83b368ee865317d664df755dc1ea4f345d3d6eddb78bcf6` |
| pnas.2534093123.sd13.xlsx | S13 - Figure 4e - Statistics  | 101 | `d11b8d433d5cb9b4ea352e2863f275cd397cf10a4b31a12d58f9e7ce22306a14` |
| pnas.2534093123.sd14.xlsx | S14 - Figure 4f - Statistics | 101 | `bb82690326b385bcae7ea753ca86ee90006d96c0765a0dab25e37b8915858b77` |
| pnas.2534093123.sd15.xlsx | S15 - Figure 4g - Statistics | 101 | `213da54d8a35ce0e8c00893f324812b2a07569b9c7349b5044821516ff481bbf` |
| pnas.2534093123.sd16.xlsx | S16 - Figure 4h - PCA Info | 1778 | `2bc0c34345f51d0e57da4f5c94beb753e311ecfa988577eeaa6b90e1c64ff553` |
| pnas.2534093123.sd17.xlsx | S17 - Figure 4h - PCA Features | 21 | `f321cd8714e274cd63f3d99e0513cf0f6fafd7a7e593495fa0daae859a577947` |
| pnas.2534093123.sd18.xlsx | S18 - Figure 4i - Statistics | 401 | `547965bcd5613ba1f989218f575d9da7fc8be95dac250c6f94293e2e4e1fa884` |
| pnas.2534093123.sd19.xlsx | S19 - Figure 4j - Statistics | 101 | `48a24c3f07389d5a9aac1b7d98a54d4364698fab4aea1a2fb5f4ccb438c4f0c8` |
| pnas.2534093123.sd20.xlsx | S20 - Figure 4k - Statistics | 401 | `fddf3cef10541369499a26b8945900cd48a3219116b6203d874cce4c3718b044` |
| pnas.2534093123.sd21.xlsx | S21 - Figure 4l - PCA Info | 1778 | `02921b0acc95161e75cec5b8e041557818e2eaaa33e31e8d1374314ed8f707c9` |
| pnas.2534093123.sd22.xlsx | S22 - Figure 4l - PCA Features | 21 | `085590435c86afbd0e9fed9fb21d6d78b2543ab3ea031ae124a594bafdb5129a` |
| pnas.2534093123.sd23.xlsx | S23 - Figure S1 - PCA Info | 2053 | `e02f3361a3f2a85d3af8b304a2e98f495637454b149c6ff887cebeb5e5e73a9f` |
| pnas.2534093123.sd24.xlsx | S24 - Figure S1 - PCA Features | 21 | `782e515cf9a31e66db41cc884c37d36fb564ff8a6a05419654b1fef90151691f` |
| pnas.2534093123.sd25.xlsx | S25 - Figure S4b,c - PCA Info | 728 | `99aedd020053791bd1ec2fefd632ed0918f4e83d23e3f145522e57bc424a2d5f` |
| pnas.2534093123.sd26.xlsx | S26 - Figure S4b,c - PCA Feats | 21 | `599837280ce84fa7b599ed214642af895858a403c12642a80287347d27e805d1` |
| pnas.2534093123.sd27.xlsx | S27 - Figure S4b,c - PCA IDs | 13 | `c4a311df83124fb419d9916fae8bf27c73affc6ae8438530d384a63ba2f50c8c` |
| pnas.2534093123.sd28.xlsx | S28 - Figure S4g - Statistics | 51 | `6dee0a1bd890d6637898ccdffd91c12c0cab02979e602cc053e3f3d61c9d7bf5` |
| pnas.2534093123.sd29.xlsx | S29 - Figure S4h - Statistics | 51 | `06b3a4caa88d22d5b2854585afcaf4ea4febc0263d288a2e27edfa1fdb0985e9` |
| pnas.2534093123.sd30.xlsx | S30 - Figure S5 - PCA Info | 553 | `4d94e73e3b875e39abc6553f9ca2f1313f64f410d4e0367a9015ab345e591bb5` |
| pnas.2534093123.sd31.xlsx | S31 - Figure S5 - PCA Features | 21 | `3473d01321c8d9fa537c43e89e211274289c2c94360aec0f605ec2397158689e` |
| pnas.2534093123.sd32.xlsx | S32 - Figure S6m - Statistics | 101 | `9afb34603ec746f073901b74e7c138612930b6c3a18305ad4e55bb0cb7741ad7` |
| pnas.2534093123.sd33.xlsx | S33 - Figure S6n - Stats Knee | 101 | `dc304f7273aeeb89768e856d61120e4594d12a17e650ad840d2f7f07cf072ef0` |
| pnas.2534093123.sd34.xlsx | S34 - Figure S6n - Stats Hip | 101 | `35cb6b212f4e1f85c71a843b48587b7b613dbe91a80bf165a2a7707a197abab0` |
| pnas.2534093123.sd35.xlsx | S35 - Figure S6o - PCA Info | 1778 | `6be18aa1093d7778fedbe9945a9e0d4020f19aa95e5549777141d1000726f4eb` |
| pnas.2534093123.sd36.xlsx | S36 - Figure S6o - PCA Features | 21 | `9067631631ac381ec7e8c2c7b162c812985d213d8626cd4193c59be3bcef09a8` |
| pnas.2534093123.sd37.xlsx | S37 - Figure S8b - Statistics | 101 | `56cc13b12563dc0f99774b3d048153629277b5af0fd6f56f2528edf67ec8aa19` |
| pnas.2534093123.sd38.xlsx | S38 - Figure S8c - Statistics | 101 | `2c47ab02cb579fd4db54bf58b67504a71ceb32244a74383dcd9400f0ee00951a` |
| pnas.2534093123.sd39.xlsx | S39 - Human Dataset | 30 | `4acb579dc78bd17806ddc5a6e421c82c718610181adbab33a0e8b0c79472baa6` |

PCA 载荷并不包含新个人映射所需的全部训练中心化与缩放参数。本技能没有借这些表生成个人 PCA 分数。表格仅供证据核对，运行时不加载。
