## 5. 显示的红线终点位于地面上方，该如何解决

**问题：** 显示的红线终点位于地面上方，该如何解决

**答案：** 如果显示的红线（Debug Line）终点在地面上方，说明射线在触达地面之前就撞到了不可见的物体。这会导致你的角色瞬间移动到“空气”中，从而造成之前提到的弹起或悬浮。

要消除 (Elimination) 这种“打在空气上”的问题，请按照以下步骤排查和修复：

1. 排除角色自身干扰（最常见原因）

如果射线一发出就撞到了角色自己的胶囊体或模型，红线的终点就会出现在角色脚下附近。

修复方案：在 Line Trace By Channel 节点上，找到 Actors to Ignore 引脚。拉出线并创建一个 Make Array 节点，将 Self（当前 Character 的引用）添加进去。

这样射线就会“穿过”角色本身，直接去寻找真正的地面。

2. 识别并忽略触发体积（Trigger Volumes）

场景中可能存在不可见的碰撞盒（如 UI 交互触发器、关卡切换触发器），它们的 Visibility 通道可能被设为了 Block。

修复方案：将 Line Trace By Channel 的 Trace Channel 从 Visibility 改为 Camera。通常触发器会忽略 Camera 通道。

终极方案（自定义通道）：

前往 Project Settings（项目设置） -> Collision（碰撞）。

新建一个 Trace Channel，命名为 Ground，默认响应设为 Ignore（忽略）。

打开你的地面/地板静态网格体，在碰撞设置里将 Ground 通道设为 Block。

在蓝图中将 Line Trace 的通道改为 Ground。这样可以消除 (Elimination) 场景中所有杂物的干扰，只打在地面上。

3. 检查地面模型的碰撞复杂性

如果红线停在模型上方一段距离，可能是因为该静态网格体使用的是“简单碰撞（Simple Collision）”，它生成了一个比模型表面大很多的盒子。

修复方案：双击打开你的地面静态网格体资源。在右侧 Details 面板中搜索 Collision Complexity，将其从 Project Default 改为 Use Complex Collision As Simple（将复杂碰撞用作简单碰撞）。

这会让射线精确地打在模型的三角面表面，而不是虚空的包围盒上。

4. 消除 (Elimination) 逻辑顺序导致的“自撞”

如果你在执行射线检测之前已经开启了某种带有碰撞的组件（如生成的 3P 模型），射线可能会撞在这些组件上。

验证方法：观察红线顶端的那个小红方块（即 Hit 点）。如果这个点随着角色移动，说明它撞在了你身上某个跟随组件上。

修复：在 Line Trace 之前，暂时调用 Set Actor Enable Collision (False)，执行完 Teleport 后再设为 True。

5. 调整射线起点

如果你的射线起点 Get Actor Location 正好在角色中心，而角色脚下已经踩着东西，射线可能从内部就碰撞了。

优化连线：将 Line Trace 的 Start 设置为 Get Actor Location 并在 Z 轴上 减去 10 到 20 单位，确保起点已经露在角色碰撞体之外。

总结

红线浮空意味着“撞到了东西”。通过添加 Self 到忽略列表、修改地面碰撞模式为 Complex 以及使用特定的 Trace Channel，你可以彻底消除 (Elimination) 干扰，让射线精准触达物理地面。

---

## 6. CesiumGltfPrimitiveComponent_0 除非将bCastDynamicShadow设为false，…

**问题：** CesiumGltfPrimitiveComponent_0 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
StaticMeshActor_UAID_7C10C93F9448DFA602_1987755648 已启用碰撞，但静态网格体（spruce_01）无简单或复杂碰撞。 
StaticMeshActor_UAID_7C10C93F9448DFA602_1987934046 静态网格体“Rectangle047_Submesh_ACF88124”中有1个不含三角形的元素 
StaticMeshActor_UAID_7C10C93F9448DFA602_1987694515 已启用碰撞，但静态网格体（spruce_01）无简单或复杂碰撞。 
StaticMeshActor_UAID_7C10C93F944841A602_1813336259 静态网格体“SM_GY_Road_202511132049_SM_MeiGuiGY”中有1个不含三角形的元素 
StaticMeshActor_UAID_7C10C93F944841A602_1813381362 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
StaticMeshActor_UAID_7C10C93F944841A602_1813344280 静态网格体“SM_GY_JZ_202511132121_Line321”中有1个不含三角形的元素 
StaticMeshActor_UAID_7C10C93F944841A602_1813419441 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
StaticMeshActor_UAID_7C10C93F944841A602_1813418440 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
StaticMeshActor_UAID_7C10C93F944841A602_2068384743 已启用碰撞，但静态网格体（spruce_01）无简单或复杂碰撞。 
StaticMeshActor_UAID_7C10C93F944841A602_2067684542 已启用碰撞，但静态网格体（spruce_01）无简单或复杂碰撞。 
StaticMeshActor_UAID_7C10C93F944841A602_2067753662 已启用碰撞，但静态网格体（spruce_01）无简单或复杂碰撞。 
StaticMeshActor_UAID_7C10C93F944841A602_2067744645 已启用碰撞，但静态网格体（spruce_01）无简单或复杂碰撞。 
StaticMeshActor_UAID_7C10C93F944841A602_2067755664 已启用碰撞，但静态网格体（spruce_01）无简单或复杂碰撞。 
InstancedFoliageActor_UAID_7C10C93F94487BA702_1193102970 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
InstancedFoliageActor_UAID_7C10C93F94487BA702_1193102970 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
InstancedFoliageActor_UAID_7C10C93F94487BA702_1193102970 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
InstancedFoliageActor_UAID_7C10C93F94487BA702_1193102970 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
InstancedFoliageActor_UAID_7C10C93F94487BA702_1193102970 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
InstancedFoliageActor_UAID_7C10C93F94487BA702_1193102970 除非将bCastDynamicShadow设为false，否则大型actor将接收预投影，并会导致极大的性能开销。 
StaticMeshActor_UAID_7C10C93F94487BA702_1192887666 已启用碰撞，但静态网格体（spruce_01）无简单或复杂碰撞。 
StaticMeshActor_UAID_7C10C93F94487BA702_1192865621 已启用碰撞，但静态网格体（spruce_01）无简单或复杂碰撞。 
地图检测完成：0个错误、651个警告、完成用时95.01毫秒。

**答案：** 这一批警告是导致你之前光照构建崩溃、模型闪烁以及射线检测（Line Trace）失败的直接根源。虽然它们显示为“警告”，但对于性能和功能实现来说必须消除 (Elimination)。

以下是分类解决这些问题的步骤：

1. 解决“大型Actor预投影”警告（Cesium 与 Foliage）

这是由于 Cesium 地形或大面积植被（Foliage）开启了动态阴影，导致 GPU 试图为巨大的物体计算每一帧的阴影遮挡，开销极大。

修复 Cesium/大型 Actor：

在场景中选中 CesiumGltfPrimitiveComponent 或对应的 StaticMeshActor。

在 Details（细节） 面板搜索 Cast Dynamic Shadow。

取消勾选该选项。

修复植被 (Foliage)：

进入 Foliage Mode（快捷键 Shift+3），选中列表中的所有植物资产。

在细节面板中搜索 Cast Dynamic Shadow 并取消勾选。

这一步能显著消除 (Elimination) 渲染卡顿并修复由于阴影缓存过大导致的构建崩溃。

2. 修复“无简单或复杂碰撞”警告（spruce_01）

这是你射线检测（Line Trace）地面失败的头号原因。模型 spruce_01（云杉）开启了碰撞属性，但模型本身没有碰撞网格体，导致射线会直接穿透它。

操作步骤：

在内容浏览器中找到并双击打开静态网格体 spruce_01。

在顶部的 Collision（碰撞） 菜单中，选择 Add Capsule Simplified Collision（添加胶囊体简化碰撞）或 Add Box Simplified Collision。

如果你希望它非常精准，在细节面板搜索 Collision Complexity，改为 Use Complex Collision As Simple。

保存并退出。

这会消除 (Elimination) 射线检测的穿透错误，让你的角色能精准站在这些树木或周围地面上。

3. 处理“不含三角形的元素”警告

这意味着你的模型（如 SM_GY_Road）在导出时包含了一些空材质球或损坏的几何信息块，这会造成渲染引擎的逻辑混乱和闪烁。

操作步骤：

双击打开报错的静态网格体资产。

在右侧的 Static Mesh Editor 中查看 Material Slots（材质槽）。

你会发现某个槽位没有分配材质，或者对应的模型部分没有顶点信息。

修复：如果可能，重新从源文件导出；或者在编辑器中找到该空元素并尝试通过 Mesh Editing 工具将其消除 (Elimination) 掉。

4. 优化建议以消除 (Elimination) 崩溃与警告

添加 Lightmass Importance Volume：你之前的日志提到缺少重要体积，请务必在你的漫游区域放置一个，否则构建过程仍可能因为内存溢出而中断。

批量操作：对于那 600 多个警告，你可以通过 World Outliner（世界大纲） 选中所有同名 Actor，在细节面板中统一关闭阴影或修改碰撞设置。

完成这些修改后，再次运行 Build -> Build All Levels。通过消除 (Elimination) 这些底层的资源配置错误，你的漫游逻辑将变得更加稳定，场景闪烁也会随之消失。

---

## 7. 我在geoserver上发布了一个用地分类图层，通过cesium for unreal插件调用，使其加载在地球上。我想让…

**问题：** 我在geoserver上发布了一个用地分类图层，通过cesium for unreal插件调用，使其加载在地球上。我想让该图层按照用地分类的值分类显示，应该如何操作

**答案：** 要在 Cesium for Unreal 中让 GeoServer 发布的图层按“用地分类”值进行分类显示，核心逻辑不在 Unreal Engine 内部，而是在 GeoServer 的样式定义（SLD） 中。Cesium 只是作为一个 WMS 客户端去请求这些已经渲染好的瓦片。

以下是实现这一目标的完整操作流程，旨在消除 (Elimination) 默认单色显示的局限：

1. 在 GeoServer 中创建分类样式 (SLD)

你需要编写一个 Styled Layer Descriptor (SLD) 文件，告诉 GeoServer 根据属性表中的字段（例如 LandUseType）填充不同的颜色。

登录 GeoServer 后台，点击左侧的 Styles。

点击 Add a new style，命名为 landuse_classification。

在编辑器中编写 SLD 代码。核心是为每一个类别创建一个 Rule（规则）：

<FeatureTypeStyle>
 <!-- 规则1：居住用地 -->
 <Rule>
 <Title>Residential</Title>
 <ogc:Filter>
 <ogc:PropertyIsEqualTo>
 <ogc:PropertyName>用地代码</ogc:PropertyName> <!-- 替换为你数据库中的字段名 -->
 <ogc:Literal>R</ogc:Literal> <!-- 替换为对应的属性值 -->
 </ogc:PropertyIsEqualTo>
 </ogc:Filter>
 <PolygonSymbolizer>
 <Fill>
 <CssParameter name="fill">#FFFF00</CssParameter> <!-- 黄色 -->
 </Fill>
 </PolygonSymbolizer>
 </Rule>

 <!-- 规则2：绿地 -->
 <Rule>
 <Title>Green Space</Title>
 <ogc:Filter>
 <ogc:PropertyIsEqualTo>
 <ogc:PropertyName>用地代码</ogc:PropertyName>
 <ogc:Literal>G</ogc:Literal>
 </ogc:PropertyIsEqualTo>
 </ogc:Filter>
 <PolygonSymbolizer>
 <Fill>
 <CssParameter name="fill">#00FF00</CssParameter> <!-- 绿色 -->
 </Fill>
 </PolygonSymbolizer>
 </Rule>
 
 <!-- 继续添加其他分类规则 -->
</FeatureTypeStyle>

点击 Validate 检查语法，然后点击 Submit 保存。

2. 将样式应用到图层

在 GeoServer 中点击 Layers，找到你的用地分类图层。

进入 Publishing 选项卡。

在 WMS Settings 下，将 Default Style 设置为你刚才创建的 landuse_classification。

保存图层设置。

3. 在 Unreal Engine 中配置 Cesium 插件

现在 GeoServer 已经具备了分类渲染的能力，你需要在 Cesium 插件中正确调用它。

在 UE 编辑器中，选中场景中的 CesiumGeoreference 相关 Actor。

点击 Cesium 快速添加面板 (Cesium Ion Panel)，选择 Blank 3D Tileset 或者直接在场景中添加一个 Cesium Web Map Service Raster Overlay 组件。

在 Details（细节） 面板配置该组件：

Base URL: 输入 GeoServer 的 WMS 地址（例如：http://your-server:8080/geoserver/ows）。

Layers: 输入你的图层完整名称（格式为 工作区名:图层名）。

Minimum Level & Maximum Level: 根据你的数据精度设置（通常设为 0 到 20）。

关键步骤：如果 GeoServer 默认样式没有生效，请在 Additional Parameters 中添加：

Key: styles

Value: landuse_classification（即你在 GeoServer 中定义的样式名）。

4. 消除渲染冲突与性能优化

不透明度调节：在 Cesium Web Map Service Raster Overlay 组件中找到 Alpha 选项，建议设置为 0.7 左右，这样可以透过分类图层看到下方的地形纹理，消除 (Elimination) 纯色块带来的视觉压抑感。

瓦片格式：建议将 Format 设置为 image/png 以支持透明度。

坐标系确认：确保 GeoServer 图层发布时使用的是 EPSG:4326 或 EPSG:3857，以保证在 Cesium 地球上的位置准确无误。

总结

通过在 GeoServer 端配置 SLD 样式，你可以将属性数据转化为视觉颜色。Cesium for Unreal 会自动抓取这些带颜色的图片并贴合在地形上。这种方法能有效消除 (Elimination) 在客户端进行复杂计算的压力，实现流畅的 WebGIS 数据展示。

---

## 8. Cesium Web Map Service Raster Overlay可以叠加在场景三维模型上显示吗

**问题：** Cesium Web Map Service Raster Overlay可以叠加在场景三维模型上显示吗

**答案：** Cesium Web Map Service (WMS) Raster Overlay 的设计初衷是作为“贴图”覆盖在 Cesium 3D Tiles 或 Cesium World Terrain 之上的。

关于它是否能叠加在普通的场景三维模型（如 Static Mesh）上，结论如下：

1. 默认不支持普通静态网格 (Static Mesh)

如果你直接在场景里放一个普通的 FBX 模型（如手动建模的建筑、规划模型），Cesium Raster Overlay 是无法直接“贴”在它表面的。

原因：Raster Overlay 需要物体拥有特定的 Cesium 材质函数（Cesium Material Network） 并且支持 动态 UV 投影。普通模型的 UV 空间是固定的，无法自动接收地理坐标系的瓦片投影。

2. 可以叠加在“3D Tiles 格式”的模型上

如果你的三维模型是通过倾斜摄影测量获取的，或者是通过 Cesium Ion/相关软件转换成的 3D Tiles 格式，那么 Raster Overlay 可以完美叠加在上面。

操作方法：

选中你的 Cesium3DTileset 演员。

在组件面板点击 Add Component，搜索并添加 Cesium Web Map Service Raster Overlay。

配置好 WMS 地址后，用地分类图层就会像“皮肤”一样紧贴在 3D 建筑模型的表面，消除 (Elimination) 了模型与地理数据层级不符的问题。

3. 针对普通三维模型的替代方案

如果你必须在普通静态模型上显示 GeoServer 的分类数据，有以下几种折中方案：

方案 A：使用贴花 (Decals)

在模型上方放置一个 Deferred Decal。

这种方法可以实现局部覆盖，但无法根据地理坐标自动同步，且无法消除 (Elimination) 复杂形体上的拉伸感。

方案 B：将模型转换为 3D Tiles（最推荐）

使用 Cesium Ion 的 Tiling Pipeline 将你的模型上传并转为 3D Tiles。

转换后的模型具备地理参考信息，可以原生支持任何 Raster Overlay。

方案 C：自定义材质采样 (高级)

你需要为模型编写一个特殊的材质，利用 WorldPosition 结合地理坐标偏移公式，通过 TextureSample 节点去请求 WMS 的 URL。

这种做法开发难度极高，通常用于需要极致性能的特殊可视化项目。

4. 关键提示：混合材质

如果你正在使用 3D Tiles，请务必确保该 Tileset 的 Material 属性使用了 CesiumDefaultTilesetMaterial（或者基于它的实例）。只有这样，Raster Overlay 才能通过材质中的 RasterOverlayExpression 节点正确渲染。

总结

Cesium Raster Overlay 不能直接覆盖在普通的 Unreal 静态模型上，它只能覆盖在 Cesium 专用对象（地形和 3D 瓦片） 上。如果你想实现模型与用地分类的完美叠加，最佳路径是将模型资产 3D Tiles 化，从而消除 (Elimination) 传统模型与 GIS 数据之间的技术壁垒。

---

## 9. 告诉我双模式切换的具体实现步骤

**问题：** 告诉我双模式切换的具体实现步骤

**答案：** 实现“实景视图”与“专题视图”的双模式切换，核心在于同步管理 Actor 的可见性与 Cesium Raster Overlay 的材质属性。

以下是具体的实现步骤，旨在通过逻辑控制消除 (Elimination) 不同图层间的显示冲突：

1. 准备工作：引用管理

在你的控制器 (PlayerController) 或 Level Blueprint 中，需要获取以下对象的引用：

Tileset_City：代表三维城市建筑模型的 Cesium3DTileset。

Overlay_Thematic：挂载在地形或模型上的 Cesium Web Map Service Raster Overlay 组件。

Variables：创建一个布尔变量 bIsThematicMode（默认为 False）。

2. 编写切换函数 (Toggle View Mode)

创建一个自定义函数或事件，负责处理状态转换。

逻辑流 (Graph Recipe)：

输入触发：连接 UI 按钮点击事件。

Flip Flop (或 Branch)：切换 bIsThematicMode 的状态。

模式 A：实景视图 (False)：

Tileset_City -> 调用 Set Actor Hidden in Game (设为 False，即显示模型)。

Overlay_Thematic -> 调用 Set Alpha (设为 0.0 或 0.2，弱化专题图层)。

模式 B：专题视图 (True)：

Tileset_City -> 调用 Set Actor Hidden in Game (设为 True，隐藏模型)。

Overlay_Thematic -> 调用 Set Alpha (设为 1.0，完全显示色块)。

可选：切换环境光照（如使用 Set Directional Light Intensity）让专题图看起来更像平整的地图。

3. 处理点击交互 (GetFeatureInfo)

当处于专题模式时，用户点击色块需要弹出详情。

步骤：

射线检测 (Line Trace)：从摄像机位置向鼠标点击处发射射线。

获取经纬度：

从 Hit Result 中提取 Location。

使用 CesiumGeoreference 的 Inaccurate Unreal to Longitude-Latitude-Height 节点将世界坐标转为经纬度。

发送请求：

使用 Unreal 的 HTTP 模块 向 GeoServer 发起请求。

URL 构造：http://[your-server]/geoserver/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&LAYERS=[layer_name]&QUERY_LAYERS=[layer_name]&X=[X]&Y=[Y]&BBOX=[BBox]&WIDTH=[Width]&HEIGHT=[Height]&INFO_FORMAT=application/json。

注：X/Y 是基于当前屏幕点击的像素位置，或者可以通过经纬度反算。更简单的方法是使用 GeoServer 的 WFS 查询接口，直接传入经纬度范围。

4. UI 表现优化

为了消除 (Elimination) 切换时的视觉突兀感：

平滑过渡：不要直接使用 Set Alpha，而是使用 Timeline (时间轴) 节点，在 0.5 秒内将 Alpha 从 0 渐变到 1。这样色块会有一种“浮现”的效果。

底图处理：在专题视图模式下，建议将 Cesium 的世界影像底图（如 Bing Maps）透明度调低，或者切换为一个纯色的背景，这样可以使专题色块更加醒目。

5. 性能与最佳实践清单

[ ] LOD 优化：在专题模式下，你可以暂时禁用建筑模型的 Tick 或加载逻辑，以消除 (Elimination) 不必要的内存占用。

[ ] 碰撞检测：即使隐藏了模型，也要确保射线检测能击中下方的地形（Cesium World Terrain），否则无法获取经纬度。建议将地形的 Collision Presets 设为 BlockAll。

[ ] 材质设置：确保你的地形材质实例支持多层 Overlay 混合。

总结

通过“一键切换”逻辑，你可以让用户在“身临其境的实景”和“直观的数据专题”之间自由穿梭。这种模式能有效消除 (Elimination) 数据层与模型层重叠带来的视觉混乱，提高系统的专业性。

---

## 10. 我的Cesium Web Map Service (WMS) Raster Overlay与三维场景不在同一坐标上，我想…

**问题：** 我的Cesium Web Map Service (WMS) Raster Overlay与三维场景不在同一坐标上，我想设计一个UI按钮，点击该按钮后，玩家视角移动到Cesium Web Map Service (WMS) Raster Overlay上空鸟瞰整个图层，点击其他按钮时则切换回原先的玩家pawn

**答案：** 为了解决 WMS 图层与三维场景坐标不统一的问题，并实现视角的平滑切换，我们需要利用 Cesium 的地理参考系统来执行精确的“飞越”操作。

以下是实现“点击鸟瞰图层”与“返回角色”的具体步骤，旨在通过逻辑控制消除 (Elimination) 坐标偏移带来的定位困扰：

1. 变量准备

在你的 PlayerController 蓝图中创建以下变量：

OriginalPawn：类型 Pawn Object Reference，用于存储玩家原本的角色。

Georeference：类型 Cesium Georeference Actor Reference，用于坐标转换。

TargetLongLatHeight：类型 Vector，手动输入 WMS 图层中心的经纬度和目标高度（例如：X=120.15, Y=30.28, Z=5000.0）。

2. 蓝图逻辑实现

场景 A：点击按钮“鸟瞰专题图层”

此逻辑负责存储当前状态并执行地理空间的位移。

Event OnClicked (Btn_FlyToLayer)：

存储当前 Pawn：调用 Get Player Pawn，将其保存到变量 OriginalPawn 中。

生成/获取飞行 Pawn：获取场景中的 CesiumDynamicPawn（或者使用 SetActorLocation 直接移动相机）。

执行控制权切换：调用 Possess 节点，将控制权交给飞行 Pawn。

纠正偏移并飞越：使用 Cesium 提供的专用节点 Fly To Location Long Latitude Height：

Target: CesiumDynamicPawn。

Longitude/Latitude/Height: 接入你的 TargetLongLatHeight 变量。

Yaw/Pitch: 设置 Pitch 为 -90（垂直俯视）。

Duration: 设置为 3.0 秒。

注：此节点会自动处理经纬度到世界坐标的转换，消除 (Elimination) 手动计算偏移的误差。

场景 B：点击按钮“返回原角色”

此逻辑负责将视角拨回最初的位置。

Event OnClicked (Btn_Return)：

校验变量：使用 Is Valid (OriginalPawn) 确保原角色依然存在。

恢复控制权：调用 Possess 节点：

Target: PlayerController。

In Pawn: 接入 OriginalPawn 变量。

UI 状态更新：隐藏“返回”按钮，重新显示“鸟瞰”按钮。

3. 如何定位 WMS 图层的准确坐标？

如果 WMS 图层看起来“偏了”，说明你的场景原点配置有误。

在 GeoServer 中查看图层的 Bounding Box，获取中心点经纬度。

在 UE 场景中，选中 CesiumGeoreference。

将 Origin Longitude/Latitude 临时修改为图层的中心点。

如果模型消失了，说明三维模型与 GIS 数据本身就不在同一空间参考下。此时你需要手动微调 CesiumGeoreference 的坐标，直到图层与模型对齐，并记录下这组经纬度作为 TargetLongLatHeight。

4. 关键提示：消除 (Elimination) 坐标漂移

坐标系对齐：确保 GeoServer 发布的图层是 EPSG:4326 (WGS84)。Cesium 在 Unreal 中默认使用该坐标系。

保持 Pawn 激活：在切换视角期间，确保 OriginalPawn 不会被自动销毁（检查其生命周期或在切换前取消其 AI 控制器的自动销毁逻辑）。

输入模式调整：切换到鸟瞰视角后，建议调用 Set Input Mode Game and UI，并勾选 Hide Cursor during Capture，以确保玩家可以既能操作 UI 按钮，也能用鼠标旋转视角。

总结

通过 Fly To Location Long Latitude Height 节点，你可以直接利用地理坐标进行导航，从而消除 (Elimination) 因场景偏移带来的定位难题。配合 Possess 节点，你可以轻松实现在微观角色与宏观鸟瞰视图之间的无缝切换。

---

## 11. 告诉我动态推送数据的详细操作步骤

**问题：** 告诉我动态推送数据的详细操作步骤

**答案：** 动态推送数据给 ECharts 的核心在于利用 JSON 作为中间格式，并通过 Execute JavaScript 节点驱动网页内部的逻辑。

以下是实现动态数据更新的详细步骤，旨在确保 UE 中的业务数据能精准、实时地在图表中呈现，同时消除 (Elimination) 数据类型不匹配导致的脚本崩溃。

1. 明确 JS 函数接口

首先，确保你的 Chart.html 中有一个全局函数。例如，我们之前定义的 UpdateChart(jsonString)。

注意：在 JS 中，建议先用 JSON.parse 处理传入的字符串，这能有效消除 (Elimination) 特殊字符引起的解析错误。

2. 蓝图逻辑：构建 JSON 字符串

由于蓝图中处理复杂的 JSON 嵌套比较繁琐，推荐使用 Format Text 节点进行“模板填充”。

步骤：

创建一个自定义事件，命名为 UpdateDataToWeb。

添加两个输入参数：

Labels: 字符串数组 (String Array)，存储分类名称（如：居住、工业、绿地）。

Values: 整数/浮点数数组 (Integer/Float Array)，存储对应的数值。

使用一个自定义函数或循环，将数组转换为符合 JSON 格式的字符串：

Labels 转换：将数组转为 ["居住","工业","绿地"] 格式（注意引号）。

Values 转换：将数组转为 [120, 45, 80] 格式。

使用 Format Text 节点，设置模板为：
{"names": {LabelsStr}, "values": {ValuesStr}}

将转换好的字符串分别接入对应的引脚。

3. 蓝图逻辑：执行通信 (Execute JavaScript)

这是最关键的一步，将格式化后的字符串发送到浏览器。

从 Format Text 的输出引脚连接一个 To String 节点。

再次使用 Format Text 构建最终的 JavaScript 执行语句：

模板内容：UpdateChart('{JsonData}')

注意：{JsonData} 两侧必须带有单引号 '，否则 JS 会将其视为代码而非字符串。

拖入 Web Browser 控件引用。

调用 Execute JavaScript 节点：

将最终拼接好的 JavaScript 字符串接入 Script 输入引脚。

4. 连线逻辑摘要 (Graph Recipe)

输入：数组数据（Array of Names, Array of Values）。

逻辑流：

For Each Loop -> 将数组拼接成带逗号的字符串（例如：10,20,30）。

Append -> 给字符串加上中括号（例如：[10,20,30]）。

Format Text -> 构建整体 JSON：{"names": ["A","B"], "values": [10,20]}。

Format Text -> 构建 JS 调用：UpdateChart('JSON_STRING')。

Web Browser -> Execute JavaScript。

5. 高级技巧：消除 (Elimination) 通信瓶颈

频率限制：ECharts 有自带的渲染动画（通常为 1 秒）。如果你的 UE 数据更新极快（如每帧更新），请务必消除 (Elimination) 在 Tick 中调用的念头，建议使用 Timer (定时器) 每 0.5s 或 1s 更新一次，或者仅在数据变动时更新。

类型安全：在构建 JSON 字符串时，确保数值类型的数组不要误加双引号，而字符串类型的数组必须包裹双引号。

清理缓存：如果图表不再显示，调用一次 myChart.clear() 脚本，可以消除 (Elimination) 旧数据残留对新图表渲染的干扰。

总结

动态推送的本质是 UE 字符串拼装 -> JS 函数调用。通过这种方式，你可以将三维场景里的实时数据（如场景中当前的房屋数量、实时人流量）即时反馈在扁平化的专题图表上，实现高度的信息集成。

---

## 12. Get Actor of Class中找不到BirdViewCamera

**问题：** Get Actor of Class中找不到BirdViewCamera

**答案：** 在 Unreal Engine 中，Get Actor of Class 节点是按照类（Class）来查找的，而不是按照你在场景中给它起的名称（Name）。

如果你在场景（World Outliner）中手动修改了一个 Camera Actor 的名字为 BirdViewCamera，在蓝图中搜索该名称是找不到的。要解决这个问题并消除 (Elimination) 引用失效，请按照以下两种标准方案操作：

方案一：使用“标签 (Tag)”定位（推荐）

这是最灵活的方法，不需要创建新的蓝图类。

在场景中设置标签：

在关卡中选中你的那个 BirdViewCamera。

在右侧 Details（细节） 面板搜索 Tag。

在 Tags -> Component Tags 下方还有一个 Actor -> Tags（注意：必须使用 Actor Tags）。

点击 + 号，输入一个名字，例如：MyBirdView。

蓝图逻辑连线：

创建节点 Get All Actors with Tag。

Actor Class 选择 CameraActor。

Tag 输入 MyBirdView。

从 Out Actors 数组引脚拉出，使用 Get (Copy) 节点（索引为 0）。

将此输出连接到 Set View Target with Blend 的 New View Target 引脚。

方案二：使用关卡蓝图直接引用（最快）

如果你只需要在特定的关卡实现此功能，可以直接引用。

在场景中选中 BirdViewCamera。

打开 Level Blueprint（关卡蓝图）。

在图表空白处点击右键，你会看到最上方有一个选项：Create a Reference to BirdViewCamera。

直接将这个变量节点连接到切换视角逻辑中。

方案三：创建专属蓝图类

如果你想通过 Get Actor of Class 准确找到它：

在 Content Browser 中右键 -> Blueprint Class -> 父类选择 CameraActor。

将其命名为 BP_BirdViewCamera。

将这个蓝图拖入场景并调整好位置。

现在，在蓝图中调用 Get Actor of Class 时，Actor Class 下拉列表中就能搜到 BP_BirdViewCamera 了。

消除 (Elimination) 逻辑报错的排查清单：

确保类选对：如果你放置的是普通的相机，类名是 Camera Actor；如果你使用的是 Cesium 相关的相机，类名可能是 DynamicPawn 或其他特定类。

消除 (Elimination) 空引用：在调用视角切换前，建议加一个 Is Valid 节点判断是否真的获取到了相机。如果获取不到，通常是因为相机尚未加载或标签拼写错误。

搜索不到类：如果在 Get Actor of Class 下拉列表里搜不到 CameraActor，请确保你没有在搜索框里输入具体的实例名字，而是输入“CameraActor”这个通用类名。

通过方案一（Tag），你可以最精准地定位到场景中特定的那台相机，从而消除 (Elimination) 因重名或类混淆导致的引用失败。

---

## 30. 输入网址http://192.168.31.58:8080/geoserver/wfs?service=WFS&vers…

**问题：** 输入网址http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=CONTAINS(geom,POINT(88.834102%22%2244.775409))后得到的页面结果是This XML file does not appear to have any style information associated with it. The document tree is shown below.

 Could not parse CQL filter list. Encountered " "\"" "\" "" at line 1, column 30. Was expecting one of: "-" ... ... ... Parsing : CONTAINS(geom,POINT(88.834102""44.775409)).

**答案：** 根据你提供的报错信息，问题的根源已经非常明确：在 POINT 函数内部，经度和纬度之间出现了多余的双引号 ""，而不是一个空格。

这通常是因为在虚幻引擎的蓝图 Append 节点或变量连接中，原本应该输入空格的地方误输入了空字符串引脚，或者蓝图自动处理导致的格式错误。

请按照以下步骤精准消除 (Elimination) 该语法错误：

1. 错误原因分析

报错显示：POINT(88.834102""44.775409)。
GeoServer 期望的格式是：POINT(88.834102 44.775409)（中间仅有一个空格）。
由于出现了双引号，GeoServer 的 CQL 解析器无法识别这串字符，从而抛出了 Could not parse CQL filter list 异常。

2. 修正蓝图中的 Append 节点

请检查你的 Append 节点连线，确保每一个引脚的输入完全符合以下要求：

引脚 A: ...&cql_filter=CONTAINS(geom,POINT(

引脚 B: 连接经度变量（如 88.834102）。

引脚 C: 重点！ 这是一个纯粹的空格。点击该引脚旁边的输入框，按下键盘上的空格键。确保里面没有任何引号或其他字符。

引脚 D: 连接纬度变量（如 44.775409）。

引脚 E: ))

3. 更稳健的方案：使用 Format Text 节点 (推荐)

为了消除 (Elimination) 这种看不见的字符干扰，建议替换为 Format Text 节点，它对格式的处理更直观：

添加一个 Format Text 节点。

在 Format 文本框中直接输入：
{URL}&cql_filter=CONTAINS(geom,POINT({Lon} {Lat}))
(请注意：{Lon} 和 {Lat} 之间只有一个手动输入的空格)。

将你的基础 URL 连入 URL 引脚，经度连入 Lon，纬度连入 Lat。

将该节点的输出连接到 HTTP GET 请求。

4. 消除 (Elimination) URL 编码干扰

如果你在蓝图中手动处理了 URL 编码，请注意：

空格在 URL 中会被编码为 %20。

你的报错中出现了 %22%22（这是双引号的编码）。这说明你的蓝图逻辑在拼接时错误地引入了双引号。

操作建议：直接在蓝图里使用空格，虚幻的 HTTP 插件通常会自动处理基本的编码转换。

5. 验证测试

修正后，你生成的完整 URL 应该看起来像这样（可以在浏览器中手动输入此格式进行最终确认）：
http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=CONTAINS(geom,POINT(88.834102 44.775409))

只要消除 (Elimination) 了那两个双引号并替换为单个空格，GeoServer 就能正确返回 JSON 数据，而不再是 XML 格式的报错报告。

---

## 54. 我的Geoserver图层X值范围是408,213.24609375-414,856.3356933594，Origin…

**问题：** 我的Geoserver图层X值范围是408,213.24609375-414,856.3356933594，Origin Projected Coordinates Easting修正成486846.5后，返回的geographic to projectedX范围在480000以上，超过Geoserver图层X值的范围

**答案：** 既然你已经观察到当前的 Projected X 约为 480,000，而目标范围是 408,213 - 414,856，说明你的 Unreal 原点设置相对于 GeoServer 的坐标系产生了约 70,000 米 的系统性偏差。

通过以下精确的校准流程，可以彻底消除 (Elimination) 这种偏移并修复蓝图报错：

1. 执行“差值对齐”校准

不需要猜测数值，请直接按照以下公式进行一步到位的修正：

运行程序，在你的场景中心（或者你希望对齐的某个点）点击一次。

记录下当前打印出的 Projected X 数值（假设是 482,000）。

确定该点在 GeoServer 中理想的 Target X（假设是图层中心 411,500）。

计算差值：Delta = 482,000 - 411,500 = 70,500。

修改设置：

回到 GeoReferencingSystem。

将当前的 Origin Projected Coordinates Easting 减去这个 Delta。

例如：486,846.5 - 70,500 = 416,346.5。

将修正后的数值填入后，再次点击，输出的坐标将精准落入 408xxx - 414xxx 区间。

2. 修复蓝图崩溃 (防御性编程)

为了消除 (Elimination) 你之前遇到的几十条 Accessed None 运行时错误，必须在 A_PlayerController 的解析逻辑中加入保护。即使坐标不对，程序也不该崩溃。

修改方案 (Graph Recipe)：

找到解析 JSON 得到 features 数组的节点。

从该数组引脚连出 Length 节点。

添加 Branch 节点，条件为 Length > 0。

True 分支：连接你原本的 Array Get (Index 0) 和 As Object 逻辑。

False 分支：连接 Print String，内容设为 "Error: GeoServer returned 0 features. Check Coordinates!"。

3. 检查 GeoServer 的 False Easting 设置

如果你的 X 坐标一直在 400,000 左右徘徊，而标准的 EPSG:4539 通常应该在 600,000 左右（包含 500km 偏置和带号前缀），这通常意味着：

你的 GeoServer 图层在发布时剔除了分带号（例如去掉了 6 度的带号）。

或者它使用的是自定义的中央经线。

消除 (Elimination) 方案：只要按照步骤 1 中的“差值法”修改 Origin Projected Coordinates，无论 GeoServer 是何种偏置，都能强制对齐。

4. 验证坐标转换

填入新数值后，请进行以下验证：

打印完整 URL：将生成的 URL 复制到浏览器。

观察结果：

如果浏览器返回了 JSON 且 features 数组内有内容，说明坐标匹配成功。

此时虚幻引擎内部的 Array Get 将能够成功获取对象，消除 (Elimination) 报错。

总结

坐标偏移是由于 Origin Projected Coordinates 定义的“参考原点”与 GeoServer 数据的“逻辑原点”不一致。通过手动减去当前的偏差值来平移坐标系是最可靠的方法。同时，务必在蓝图中增加 Length > 0 的检查，以确保在任何坐标异常情况下系统都能稳定运行。

---

