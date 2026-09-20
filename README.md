# OGE 杭州七类土地利用/覆盖分类课堂项目

本项目用于开放地球引擎（OGE）课堂实操。学生只需浏览器和 OGE 账号：上传研究区边界与训练标签后，将课堂代码复制到 OGE 开发中心运行，即可在 OGE 云端读取六景固定 Sentinel-2 影像、构建特征、训练随机森林，并提交杭州全域分类批处理任务。

## 本地训练与 OGE 云端训练的区别

课堂不需要安装本地 Python 环境，也不需要下载 Sentinel-2 影像或运行本地随机森林程序。

`hangzhou_landcover_oge_classroom.py` 会调用 OGE 数据和云端算子，在 OGE 服务器上依次完成：

1. 按六个已核验的 OGE `coverageID` 读取 2025 年 Sentinel-2 L2A 影像；
2. 多景中值合成并选择光谱波段；
3. 计算 NDVI 和 NDWI；
4. 读取上传的七类训练标签；
5. 在云端训练随机森林；
6. 对杭州全域逐像元分类；
7. 将七类结果提交为 20 米 GeoTIFF 批处理任务。

此前用于制作正式成果的本地程序不属于课堂运行流程。课堂版默认使用 30 棵树，以缩短等待时间，因此结果与使用更多树木训练的正式成果可能存在少量细节差异。

## 仓库文件

| 文件 | 用途 | 是否必须 |
|---|---|---|
| `hangzhou_landcover_oge_classroom.py` | OGE 云端训练、分类与显示代码 | 是 |
| `HZ_boundary.geojson` | 杭州市研究区边界，用于裁剪分类结果 | 是 |
| `HZ2025_reference_train_20m.tif` | 20 米分辨率七类训练标签 | 是 |
| `README.md` | 学生操作说明 | 是 |

如需讲授精度评价，还需另行提供并上传 `HZ2025_reference_validation_20m.tif`。基础课堂不需要该文件。

## 数据来源与制作过程

这两个课堂输入文件不是两个可以由 OGE 自动联网读取的远程地址：

- `HZ_boundary.geojson`：当前文件实际来自 GADM 4.1 的中国二级行政区数据，从 `gadm41_CHN_2.json.zip` 中提取 `GID_2 = CHN.31.1_1`（Hangzhou），整理为单要素 WGS84 GeoJSON。它不是 OGE 平台数据。GADM 允许学术及其他非商业用途，但未经许可不允许再分发或商业使用；公开课程材料需要另行处理该许可问题。
- `HZ2025_reference_train_20m.tif`：不是直接下载的训练样本成品。它由本地脚本从 Esri / Impact Observatory / Microsoft Sentinel-2 Land Cover 2025 参考产品中派生：先转换为 20 米网格，再筛选 3×3 邻域内类别一致的像元，最后按七类各抽取 1000 个训练像元。它是自动生成的参考标签，不是实地调查真值。

GitHub 只负责分发文件。学生必须把这两个文件上传到自己的 OGE `myData`，才能由课堂代码读取。公开的 GitHub 文件链接不能直接替代 `myData/文件名`；`Feature.loadFeatureFromUpload` 和 `service.getCoverage` 读取的是 OGE 已登记且当前账号有权限的资源。

## 分类体系

| 编码 | 类别 | 地图颜色 |
|---:|---|---|
| 1 | 水体 | 蓝色 |
| 2 | 林地 | 深绿色 |
| 3 | 湿地/淹水植被 | 青绿色 |
| 4 | 耕地 | 黄色 |
| 5 | 建成区 | 红色 |
| 6 | 裸地 | 灰色 |
| 7 | 灌木草地 | 黄绿色 |

编码 `0` 仅用于研究区外或无数据区域，不属于土地覆盖类别。

## 学生操作步骤

### 1. 下载课堂材料

在本仓库页面点击 **Code → Download ZIP**，解压后确认存在以下三个文件：

- `hangzhou_landcover_oge_classroom.py`
- `HZ_boundary.geojson`
- `HZ2025_reference_train_20m.tif`

### 2. 登录 OGE

打开 [开放地球引擎](https://www.openge.org.cn/)并登录个人账号。

### 3. 上传杭州市边界

进入 **个人中心 → 我的数据 → 上传数据 → 矢量数据**，上传：

```text
HZ_boundary.geojson
```

数据名称保持为 `HZ_boundary`，不要自行改名。

### 4. 上传训练标签

进入 **个人中心 → 我的数据 → 上传数据 → 栅格数据**，上传：

```text
HZ2025_reference_train_20m.tif
```

数据名称保持为 `HZ2025_reference_train_20m`，不要自行改名。

课堂代码按以下资源路径读取数据：

```python
myData/HZ_boundary.geojson
myData/HZ2025_reference_train_20m.tif
```

如果修改了上传名称，必须同步修改代码中的路径。

### 5. 在开发中心运行代码

1. 打开 OGE **开发中心**；
2. 新建或清空 Python 代码模板；
3. 打开 `hangzhou_landcover_oge_classroom.py`，复制全部代码；
4. 粘贴到 OGE 编辑器；
5. 点击 **运行**；
6. 在导出窗口中填写 `EPSG:32650`、分辨率 `20`、格式 `TIF`；
7. 提交任务，在左侧 **任务面板** 等待状态由“运行中”变为完成。

代码直接写入下列六个 OGE `coverageID`，不会再次按日期、云量动态检索：

```text
T50RQU_20251128T023939
T50RPT_20251128T023939
T50RQT_20251128T023939
T51RTP_20250916T024141
T50RPU_20251121T024919
T50RPT_20251121T024919
```

这些编号来自 OGE 数据中心的 `S2_MSIL2A` 产品，并已在 OGE 开发中心逐景验证。不要替换成 Earth Search 的 `S2A_...` 或 `S2B_...` 场景编号，OGE 会返回“未查询到元数据”。

### 6. 查看分类结果

全市 20 米分类需要批处理。任务完成后下载 GeoTIFF；如需在 OGE 可视化区域查看，可将该 GeoTIFF 上传到个人 `myData`，再用 `service.getCoverage("myData/上传后的文件名.tif")` 和 `getMap()` 加载。直接让完整训练与分类链在同步地图请求中执行，容易触发约 5 分钟的网页请求超时。

## 课堂参数

代码开头包含以下参数：

```python
NUM_TREES = 30
EXPORT_RESULT = True
SHOW_RESULT_ON_MAP = False
EVALUATE_RESULT = False
```

- `NUM_TREES = 30`：课堂演示使用 30 棵树，减少云端计算时间；正式计算可改为 `100`。
- `EXPORT_RESULT = True`：提交杭州全市分类批处理任务。
- `SHOW_RESULT_ON_MAP = False`：不在同一次同步请求中渲染全市结果，避免网页超时。
- `EVALUATE_RESULT = False`：不读取验证标签，不计算参考一致性。

如需计算参考一致性，需先上传验证标签，再将 `EVALUATE_RESULT` 改为 `True`。`SHOW_RESULT_ON_MAP` 只建议在较小研究区或已有分类栅格的情况下启用。

## 常见问题

### 提示找不到 `myData` 数据

检查两个输入文件是否已经上传到当前登录的 OGE 账号，并确认上传名称与代码路径一致。每位学生的 `myData` 相互独立，教师账号中的个人数据不会自动出现在学生账号中。

### 使用 GitHub 在线链接时提示无权限

GitHub 上“可以下载”不等于 OGE 服务器“可以作为平台数据资源读取”。不要把 GitHub `blob` 或 `raw` 地址直接填入 `Feature.loadFeatureFromUpload`、`service.getCoverage`。请先下载文件，再上传到当前学生账号的 OGE `myData`；或者由教师将数据发布为 OGE 共享资源并提供具有访问权限的资源 ID。

### 提示“未查询到元数据”或集合为空

先确认代码中的 `productID="S2_MSIL2A"` 和六个 `coverageID` 没有被改动。Earth Search 的完整场景名与 OGE `coverageID` 不是同一种编号，不能互换。若未来 OGE 数据目录发生变化，可在 **数据中心 → 高级检索** 中选择 `S2_MSIL2A`、输入杭州空间范围和上述日期，打开产品详情并复制平台显示的完整 `coverageID`；课堂 PPT 已逐步截图演示该过程。

### 运行时间较长

影像读取、合成、随机森林训练和全域分类都在 OGE 云端执行，运行速度受平台任务队列和云端资源影响。不要在任务运行期间重复点击运行。任务面板显示“运行中”表示平台已经接受任务，并非代码仍在本地运行。

### 是否还要运行本地训练程序

不需要。本仓库的课堂代码会在 OGE 云端重新训练随机森林。本地程序只用于此前制作正式成果，不参与课堂操作。

### 为什么课堂结果与正式成果不完全相同

课堂版使用 30 棵树，正式成果可能使用更多树，并可能采用不同的数据预处理或计算环境。两者分类体系和总体流程一致，局部像元结果可能不同。

## 数据与精度说明

训练标签来自公开土地覆盖参考产品的空间抽样，用于课程演示，不属于独立实地调查真值。如果使用同源验证标签计算指标，应表述为“参考一致性”，不宜称为独立实测精度。

## 运行环境

本代码依赖 OGE 平台的 `oge` 接口、数据目录和云端算子，不能直接作为普通本地 Python 脚本运行。
