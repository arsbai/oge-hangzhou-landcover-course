"""OGE 课堂示例：杭州 2025 年七类土地利用/覆盖分类。"""

import oge

# 使用前请将以下两个文件上传到个人 OGE 资源 myData：
# 1. HZ_boundary.geojson
# 2. HZ2025_reference_train_20m.tif
#
# 类别编码：
# 1 水体；2 林地；3 湿地/淹水植被；4 耕地；
# 5 建成区；6 裸地；7 灌木草地。

oge.initialize()
service = oge.Service.initialize()

BBOX = [118.3333, 29.1965, 120.9271, 30.5557]
NUM_TREES = 30          # 课堂演示；正式计算可改为 100
EXPORT_RESULT = False   # True：提交结果导出
EVALUATE_RESULT = False # True：读取验证标签并计算参考一致性

# 1. 读取研究区与训练标签
boundary = service.getProcess("Feature.loadFeatureFromUpload").execute(
    "myData/HZ_boundary.geojson",
    "EPSG:4326",
)
labels = service.getCoverage("myData/HZ2025_reference_train_20m.tif")

# 2. 检索并合成 2025 年秋季 Sentinel-2 L2A 影像
images = service.getCoverageCollection(
    productID="S2_MSIL2A",
    datetime="2025-09-01 00:00:00,2025-11-30 23:59:59",
    bbox=BBOX,
    cloudCoverMin=0,
    cloudCoverMax=5,
)
image = service.getProcess("CoverageCollection.mosaic").execute(images, "median")
image = service.getProcess("Coverage.selectBands").execute(
    image,
    ["B02", "B03", "B04", "B08", "B11", "B12"],
)
image = service.getProcess("Coverage.reproject").execute(image, 32650, 20)

# 3. 计算 NDVI、NDWI，并加入分类特征
ndvi = service.getProcess("Coverage.NDVI").execute(image, "B04", "B08")
ndvi = service.getProcess("Coverage.rename").execute(ndvi, ["NDVI"])
ndwi = service.getProcess("Coverage.NDWI").execute(image, "B03", "B08")
ndwi = service.getProcess("Coverage.rename").execute(ndwi, ["NDWI"])
features = service.getProcess("Coverage.addBands").execute(
    image, ndvi, ["NDVI"], False
)
features = service.getProcess("Coverage.addBands").execute(
    features, ndwi, ["NDWI"], False
)

# 4. 训练随机森林并进行逐像元分类
model = service.getProcess("Coverage.randomForestClassifierModel").execute(
    featuresCoverage=features,
    labelCoverage=labels,
    checkpointInterval=10,
    featureSubsetStrategy="sqrt",
    maxBins=32,
    maxDepth=10,
    minInfoGain=0.0,
    minInstancesPerNode=2,
    minWeightFractionPerNode=0.0,
    numTrees=NUM_TREES,
    seed=20250914,
    subsamplingRate=0.8,
)
prediction = service.getProcess("Coverage.modelClassify").execute(features, model)

# 5. 将模型输出的 0—6 编码转换为 1—7，0 留给区外/无数据
classes = service.getProcess("Coverage.remap").execute(
    prediction,
    [0, 1, 2, 3, 4, 5, 6],
    [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    0,
)
result = service.getProcess("Coverage.clipRasterByMaskLayerByGDAL").execute(
    classes,
    boundary,
    "True", "", "False", "", "", "False", "False", "", "False", "0", "",
)
result = service.getProcess("Coverage.toUint8").execute(result)

# 6. 设置类别颜色并显示结果
colors = [
    "#0064c8", # 水体
    "#006400", # 林地
    "#009688", # 湿地/淹水植被
    "#ffda5e", # 耕地
    "#fa0000", # 建成区
    "#b4b4b4", # 裸地
    "#bbcc33", # 灌木草地
]
result.styles({"min": 1, "max": 7, "palette": colors}).getMap(
    "杭州2025_随机森林七类_20m"
)
boundary.styles(["#FFFFFF"]).getMap("杭州市研究区边界")
oge.mapclient.centerMap(119.60, 29.90, 9)

# 7. 可选：读取验证标签并计算参考一致性
if EVALUATE_RESULT:
    validation = service.getCoverage(
        "myData/HZ2025_reference_validation_20m.tif"
    )
    metrics = service.getProcess(
        "Coverage.multiclassClassificationEvaluator"
    ).execute(
        validation,
        prediction,
        ["accuracy", "f1", "weightedPrecision", "weightedRecall"],
    )
    metrics.log("Spatial_holdout_reference_agreement")

# 8. 可选：导出单波段类别栅格
if EXPORT_RESULT:
    result.export("Hangzhou_2025_RF_classes_20m")
