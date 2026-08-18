## 13. 用geoserver加载的WebMapServiceRasterOverlay图层，如何通过UE蓝图实现点击获取用地类型…

**问题：** 用geoserver加载的WebMapServiceRasterOverlay图层，如何通过UE蓝图实现点击获取用地类型、面积等属性值

**答案：** 要通过 Web Map Service (WMS) 在 Unreal Engine 中获取要素属性（如用地类型、面积），标准的地理信息系统（GIS）方法是调用 WMS 的 GetFeatureInfo 请求。

由于 WMS 图层本质上是渲染好的图片，它不直接携带矢量数据，因此我们需要通过蓝图将玩家的“点击位置”转换为经纬度，发送 HTTP 请求给 GeoServer，解析返回的 JSON 数据。

核心流程

坐标转换：将屏幕点击位置转换为 Unreal 世界空间坐标，再利用 Cesium 的地理参考系统转换为 WGS84 经纬度。

构建 URL：根据 WMS 规范构建包含坐标（X,Y）和边界框（BBOX）的 GetFeatureInfo 请求地址。

网络通信：发送 HTTP GET 请求并解析返回的属性。

1. 资产与组件准备

组件：确保场景中包含 CesiumGeoreference。

插件：启用 HTTP Blueprint 插件（UE5.x 内置）或使用第三方插件如 VaRest。

GeoServer 设置：确保你的 WMS 图层允许查询（Queryable），并且在 GeoServer 中配置支持 application/json 的输出格式。

2. 详细蓝图实现步骤

步骤 A：获取经纬度与屏幕位置

在玩家控制器（Player Controller）或 UMG 中监听鼠标点击：

使用 Get Mouse Position on Platform 获取屏幕像素坐标。

使用 Line Trace by Channel（从鼠标位置发射射线）获取点击到 WMS 图层的 Impact Point（世界坐标）。

调用 Transform World Position to Ellipsoid Longitude Latitude Height（目标选为 CesiumGeoreference）：

输入：Impact Point。

输出：得到点击位置的经纬度。

步骤 B：构建 GetFeatureInfo URL

WMS 的 GetFeatureInfo 需要模拟一个像素点击。你需要拼接如下字符串：

基本参数：SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&LAYERS=你的图层名&QUERY_LAYERS=你的图层名。

格式参数：INFO_FORMAT=application/json（以便蓝图解析）。

空间参数：需要定义一个微小的 BBOX（边界框）并指定 X 和 Y 像素。

简便技巧：在 Cesium 环境下，通常更推荐通过经纬度直接向 GeoServer 的 WFS 服务请求（如果可用），因为 WMS 请求需要计算复杂的 BBOX。若必须使用 WMS，请确保 BBOX 包围了你的点击点。

步骤 C：发送 HTTP 请求 (Graph Recipe)

节点：Create HTTP Request。

节点：Set URL：接入步骤 B 构建的字符串。

节点：Set Verb：设置为 GET。

节点：Process Request：发送请求。

事件：On Process Request Complete：

检查 Response Code 是否为 200。

使用 Get Content as String 获取 JSON。

步骤 D：解析 JSON 并展示

使用 Json Object String to Map 或 Parse JSON 节点。

定位到 features -> properties 路径。

提取字段：例如 用地类型 (Type)、面积 (Area)。

消除 (Elimination) 数据格式不一致：将提取到的数值转为文本，更新到 UMG 的 Text 组件中。

3. 性能与最佳实践

消除 (Elimination) 无效请求：在发送请求前，检查射线检测是否命中了 WMS 所在的 Actor，避免点击天空或空白区域时发送无效的网络请求。

异步处理：HTTP 请求是异步的，在等待响应时可以显示一个“加载中”的动画，以消除 (Elimination) 界面假死的错觉。

WFS 替代方案：如果 GeoServer 支持 WFS (Web Feature Service)，使用 GetFeature 并通过 cql_filter 过滤经纬度通常比模拟 WMS 像素点击更精准，能有效消除 (Elimination) 坐标投影转换带来的误差。

通过此方案，你点击地图上的颜色色块时，UE 会向后端索取该位置背后的原始地理属性，从而实现图文联动效果。

---

## 14. 告诉我通过蓝图将玩家的“点击位置”转换为经纬度，发送 HTTP 请求给 GeoServer，解析返回的 JSON 数据的…

**问题：** 告诉我通过蓝图将玩家的“点击位置”转换为经纬度，发送 HTTP 请求给 GeoServer，解析返回的 JSON 数据的详细蓝图实现步骤

**答案：** 实现该功能需要将 Cesium 地理系统、射线检测与 HTTP 异步通信 结合。以下是基于 UE5 的详细蓝图构建方案，旨在通过精确的坐标转换消除 (Elimination) 点击偏移。

1. 坐标转换逻辑（获取经纬度）

在 PlayerController 或 Level Blueprint 中实现：

节点：Get Mouse Position on Platform：获取鼠标当前在屏幕上的坐标。

节点：Convert Screen Location to World Space：将鼠标位置转换为世界空间的起始点（World Location）和方向（World Direction）。

节点：Line Trace by Channel：

Start: 世界位置。

End: 世界位置 + (方向 * 100,000)。

Trace Channel: 选为 Visibility。

节点：Break Hit Result：获取 Impact Point（世界坐标）。

节点：Transform World Position to Ellipsoid Longitude Latitude Height（属于 Cesium 插件）：

Target: 获取场景中的 CesiumGeoreference 实例。

World Position: 输入刚才的 Impact Point。

输出变量: 提升为两个变量 Target_Lat (纬度) 和 Target_Lon (经度)。

2. 构建 GeoServer HTTP 请求

GeoServer 的 WFS (Web Feature Service) 比 WMS GetFeatureInfo 更适合直接通过经纬度查询属性。我们将使用 CQL_FILTER 来消除 (Elimination) 复杂的 BBOX 计算。

节点：Construct URL (String)：
使用 Append 节点拼接请求字符串：

http://你的服务器IP:8080/geoserver/wfs?

service=WFS&version=1.0.0&request=GetFeature&

typeName=工作空间:图层名&

outputFormat=application/json&

cql_filter=CONTAINS(geom, POINT( + Target_Lon + + Target_Lat + ))

注意：POINT 内部经纬度顺序通常是 (经度 纬度)，且中间是空格。

3. 发送与解析请求 (Graph Recipe)

节点：Create HTTP Request：

Verb: GET

URL: 接入上一步拼接的字符串。

节点：Bind Event to On Process Request Complete：创建一个自定义事件来接收回调。

节点：Process Request：执行发送。

在自定义事件（Callback）中：

节点：Get Content as String：从 Response 引脚获取 JSON 字符串。

节点：Json Object String to Map (或使用 Json Blueprint Utilities 插件提供的解析节点)：

由于 WFS 返回的是标准的 GeoJSON，你需要逐层查找：features (Array) -> Index 0 -> properties (Object)。

解析字段：

使用 Get Field 节点，键名输入你在 GeoServer 中的字段名（如 land_type 或 area）。

将结果转换为 String 或 Float。

4. 数据展示与异常处理

更新 UI：将解析出的“用地类型”和“面积”值设置到 UMG 控件的文本框中。

消除 (Elimination) 逻辑死循环：

在发送请求前，检查 Target_Lat 是否有效。

如果 Response Code 不是 200，或者 features 数组长度为 0（代表点击区域无数据），应弹出“此处无信息”的提示，以消除 (Elimination) 玩家对界面无响应的困惑。

5. 性能提示

消除 (Elimination) 频繁请求：建议在按钮松开时才触发请求，不要在鼠标移动时持续触发。

坐标系注意：GeoServer 默认坐标系通常是 EPSG:4326，确保你的 CQL 过滤参数与之匹配。如果不匹配，需要在请求中添加 srsName=EPSG:4326 进行消除 (Elimination) 坐标偏差的操作。

---

## 16. 构建 GeoServer HTTP 请求的详细蓝图操作步骤

**问题：** 构建 GeoServer HTTP 请求的详细蓝图操作步骤

**答案：** 在 Unreal Engine 中构建并发送 HTTP 请求需要结合 字符串拼接 与 HTTP 模块节点。以下是实现点击地图获取 GeoServer 数据的详细蓝图操作步骤，旨在消除 (Elimination) 网络请求配置中的常见错误。

1. 启用必要插件

在编辑器菜单 Edit -> Plugins 中，确保启用以下插件：

HTTP Blueprint（核心请求功能）

JSON Blueprint Utilities（用于解析返回的属性数据）

2. 第一阶段：构建请求 URL (String)

利用 Append 节点将基础地址与动态经纬度参数组合。

节点：Append (String)：点击“Add Pin”增加引脚，按顺序填入：

A: http://你的服务器IP:端口/geoserver/wfs?

B: service=WFS&version=1.0.0&request=GetFeature&

C: typeName=工作空间:图层名&outputFormat=application/json&

D: cql_filter=CONTAINS(geom, POINT(

E: (接入经度变量 Longitude)

F: (输入一个空格 " ")

G: (接入纬度变量 Latitude)

H: ))

变量化：将拼接完成的字符串提升为变量 RequestURL。

3. 第二阶段：发送 HTTP 请求 (Graph Recipe)

这一步负责与 GeoServer 握手并处理异步回调。

节点：Create HTTP Request：

Verb: 下拉框选择 GET。

URL: 接入上一步的 RequestURL 变量。

节点：Add Header：

从 Request 引脚拉出。

Header: Accept

Value: application/json (确保 GeoServer 返回 JSON 格式以消除 (Elimination) 格式错误)。

节点：Bind Event to On Request Complete：

从 Request 引脚拉出，搜索 Bind Event to On Request Complete。

从 Event 红点引脚拉出，创建一个 Custom Event（命名为 OnGeoServerResponse）。

节点：Process Request：

最后一步，连接执行脉冲，正式发出请求。

4. 第三阶段：解析 JSON 数据

在自定义事件 OnGeoServerResponse 中处理返回的结果。

节点：Get Content as String：从 Response 引用中提取原始字符串。

节点：Load JSON from String (来自 Json Blueprint Utilities)：

将上一步的字符串转为 Json Object。

节点：Get Object Array Field：

Field Name: 输入 features。

节点：Get Array Item：

获取索引为 0 的元素（假设点击点只对应一个地块）。

节点：Get Object Field：

Field Name: 输入 properties。

节点：Get String Field / Get Number Field：

根据你在 GeoServer 里的字段名（如 land_use_type 或 area_size）获取具体数值。

5. 消除 (Elimination) 常见故障

跨域与网络权限：如果是在网页端运行或有防火墙，请确保 GeoServer 的端口（默认 8080）已开放，以消除 (Elimination) 连接超时的风险。

空结果处理：在解析 features 数组前，先用 Length 节点检查是否大于 0。如果为 0，代表玩家点到了地图范围外或没有要素的区域，此时应消除 (Elimination) 后续解析逻辑并提示玩家。

坐标顺序：GeoServer WFS 的 POINT 坐标通常遵循 (经度 纬度)。如果查询不到结果，请尝试调换 E 和 G 引脚的顺序，以消除 (Elimination) 反向坐标导致的搜索失败。

通过以上步骤，你可以构建一个稳健的请求链路，将地理空间数据无缝集成到 Unreal 引擎的 UI 系统中。

---

## 17. 构建 GeoServer HTTP 请求时，Construct URL (String)节点应该在哪个蓝图中设计

**问题：** 构建 GeoServer HTTP 请求时，Construct URL (String)节点应该在哪个蓝图中设计

**答案：** 关于 Construct URL (String) 及其配套 HTTP 逻辑的放置位置，建议遵循 Unreal Engine 的“逻辑与表现分离”原则。为了消除 (Elimination) 架构混乱并提高复用性，请参考以下建议：

1. 推荐位置：Player Controller（玩家控制器）

理由：这是处理玩家交互（点击地图）和逻辑中转的最佳场所。

操作流：鼠标点击 -> 射线检测获取位置 -> 构建 URL -> 发送 HTTP。

优势：点击行为是玩家发出的指令，放在 Player Controller 中可以方便地访问鼠标状态、相机和 HUD。它在角色被消除 (Elimination) 或重新生成时依然存在，逻辑更稳健。

2. 替代位置：Actor Component（专门的逻辑组件）

如果你希望这个“点击查询”功能能够轻松移植到其他项目中，可以创建一个名为 BPC_GeoQueryComponent 的 Actor Component。

操作流：将此组件挂载到 Player Controller 上。

优势：这种模块化设计能有效消除 (Elimination) 蓝图臃肿问题。你只需在组件内写好 URL 拼接逻辑，Player Controller 只负责触发它。

3. 不建议放置的位置

UMG Widget Blueprint：虽然 UI 按钮可以触发查询，但不要在 Widget 内部写复杂的坐标转换和 URL 拼接。Widget 应该只负责显示结果。将逻辑留在 UI 里会增加调试难度，难以消除 (Elimination) 潜在的内存泄漏风险。

Level Blueprint：除非该查询只在这一关有效，否则不要放在这里。这会导致逻辑难以跨关卡迁移，无法消除 (Elimination) 重复劳动。

4. 最佳实践蓝图结构 (Workflow)

你可以按照以下结构来组织逻辑，以消除 (Elimination) 各系统间的强耦合：

在 Player Controller 中：

监听鼠标点击事件。

执行射线检测获取世界坐标，并利用 Cesium 节点转为经纬度。

调用函数：SendGeoServerRequest(float Lat, float Lon)。

在 SendGeoServerRequest 函数内（属于 Controller 或组件）：

节点：Construct URL (String)：在这里执行 Append 拼接。

发送请求：使用 Create HTTP Request。

回调处理：当请求完成，解析 JSON，并将结果发送给 UI 显示。

5. 提示

在构建 URL 时，建议将“服务器基础地址”、“工作空间名”和“图层名”存为变量并暴露出来。这样当你更换 GeoServer 发布的图层时，只需修改变量值，即可快速消除 (Elimination) 因配置变更导致的逻辑改动。

---

## 18. 发送HTTP请求时搜索不到Process Request节点

**问题：** 发送HTTP请求时搜索不到Process Request节点

**答案：** 在 Unreal Engine 的 HTTP Blueprint 插件体系中，Process Request 节点是一个成员函数（Member Function）。如果你直接在蓝图空白处右键搜索，通常是找不到的。

要消除 (Elimination) 节点消失的问题，请严格按照以下步骤操作：

1. 必须从“Create HTTP Request”引脚拉出

这个节点不是独立的全局节点，它必须依附于一个特定的请求对象。

正确步骤：

先放置 Create HTTP Request 节点。

从其右侧的蓝色输出引脚 Return Value 拉出一条引线，在空白处松开。

在此时弹出的搜索框中输入 Process Request。

你将看到在 HTTP 分类下出现了该节点。

2. 区分两个版本的节点

在不同的引擎版本（如 5.3+）中，你可能会看到两个选项：

Process Request：这是标准版本。你需要手动绑定（Bind）一个自定义事件到 On Request Complete 委托上，才能获取返回的数据。

Process Request (Latent)：这是“异步/延迟”版本。它自带一个完成后的执行脉冲，类似于 Delay 节点，用起来更简洁，能有效消除 (Elimination) 繁琐的事件绑定步骤。

3. 检查“Context Sensitive”（上下文相关）

如果你已经从 Return Value 拉出了引线但仍然搜不到：

请确保搜索框右上角的 Context Sensitive 勾选框是选中状态。

如果勾选后依然搜不到，请确认你是否误用了旧版的“HTTP”插件（如某些第三方插件）。确保你使用的是 UE5 内置的 Http Blueprint 插件。

4. 常见的逻辑连线错误排查

为了消除 (Elimination) 请求无法发出的故障，请检查：

URL 是否为空：在调用 Process Request 之前，必须先调用 Set URL 节点。

Verb 是否设置：确保调用了 Set Verb（通常设为 GET 或 POST）。

引脚连接：所有的设置节点（Set URL, Set Header 等）都必须通过 Target 引脚连接回同一个 Create HTTP Request 创建的对象。

总结 (Graph Recipe)

[Create HTTP Request] 
 | (Return Value) -> [Set URL]
 | (Return Value) -> [Set Verb]
 | (Return Value) -> [Process Request] <-- 必须这样拉出来
通过这种“链式”拉线的方式，你可以顺利找到并触发 Process Request，从而消除 (Elimination) 逻辑链路的中断。

---

## 19. 搜不到Create HTTP Request节点

**问题：** 搜不到Create HTTP Request节点

**答案：** 如果你在蓝图中搜索不到 Create HTTP Request 节点，通常有三个原因：插件未启用、引擎版本差异或搜索设置问题。请按照以下步骤逐一排查，以消除 (Elimination) 障碍：

1. 检查插件启用状态（最常见原因）

Unreal Engine 的蓝图 HTTP 功能并不是默认开启的，它依赖于一个特定的插件。

前往菜单栏 Edit（编辑） -> Plugins（插件）。

在搜索框输入 HTTP。

必须确保 Http Blueprint 插件处于 Enabled（已启用） 状态。

注意：启用后必须重启编辑器，否则节点库不会更新，无法消除 (Elimination) 搜索不到的问题。

2. 区分引擎版本与节点名称

在不同版本的 UE5 中，该节点的名称可能略有不同：

UE 5.3 及以上版本：插件名为 Http Blueprint，对应的节点通常就是 Create HTTP Request。

UE 5.1 / 5.2 版本：如果内置插件不成熟，你可能需要确保安装了 JSON Blueprint Utilities 插件。

备选搜索词：如果搜不到 Create HTTP Request，请尝试搜索 “Construct Http Request” 或 “Make Http Request”。

3. 搜索设置：取消勾选“Context Sensitive”

有时候因为你当前所处的蓝图类（如 Actor 或 Widget）不直接属于 HTTP 的上下文，编辑器会过滤掉该节点。

在蓝图右键搜索框中，取消勾选右上角的 Context Sensitive（上下文相关）。

再次输入 Create HTTP Request。

4. 放置位置限制

确保你是在 Event Graph（事件图表） 中搜索。在 Function（函数） 或 Macro（宏） 中，如果勾选了“只读”或特定的限制，某些异步节点可能不会出现。

如果以上方法都无效（C++ 备选方案）

如果由于环境问题始终无法消除 (Elimination) 蓝图节点的缺失，你可以通过 C++ 简单地暴露一个函数给蓝图。

在你的 .build.cs 文件中添加模块：
PublicDependencyModuleNames.AddRange(new string[] { "Http", "Json", "JsonUtilities" });

在代码中创建请求：

// 这种方式可以彻底消除对插件节点的依赖
TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
Request->SetURL(TEXT("你的URL"));
Request->SetVerb(TEXT("GET"));
Request->ProcessRequest();
总结排查清单：

插件：Http Blueprint 必须勾选并重启。

搜索：取消 Context Sensitive。

环境：在 Event Graph 中搜索。

一旦插件成功加载，你就能找到该节点，从而消除 (Elimination) 无法与 GeoServer 通信的限制。

---

## 20. 使用 http GET 请求节点构建 GeoServer HTTP 请求，具体的蓝图连线逻辑是什么

**问题：** 使用 http GET 请求节点构建 GeoServer HTTP 请求，具体的蓝图连线逻辑是什么

**答案：** 如果你使用的是支持直接发送请求的 HTTP GET 请求 节点（常见于第三方插件或简化版插件），其连线逻辑通常是“一站式”的。这种方式比官方分步骤设置的逻辑更直接。

以下是实现点击地图并获取 GeoServer 属性的详细连线逻辑，旨在消除 (Elimination) 构建过程中的断链风险：

1. 坐标准备（输入源）

在 PlayerController 中：

执行 射线检测 (Line Trace) 得到 Impact Point。

通过 CesiumGeoreference 节点转换为经纬度：得到 Target_Lat 和 Target_Lon。

2. URL 拼接逻辑 (核心)

使用 Append 节点构建完整的请求地址。这一步是成功的关键，必须确保 URL 格式严谨：

引脚 A: http://你的IP:8080/geoserver/wfs?

引脚 B: service=WFS&version=1.0.0&request=GetFeature&

引脚 C: typeName=工作空间:图层名&outputFormat=application/json&

引脚 D: cql_filter=CONTAINS(geom, POINT(

引脚 E: Target_Lon (经度)

引脚 F: " " (注意：这里是一个空格字符串)

引脚 G: Target_Lat (纬度)

引脚 H: ))

3. HTTP GET 请求节点连线

将拼接好的字符串接入请求节点：

节点：HTTP GET 请求：

URL: 接入上述 Append 的输出结果。

Headers (请求头)：如果你有“创建请求头文件”节点，创建一个包含 Accept: application/json 的头并连入。如果不连，GeoServer 可能会返回 XML。

事件绑定 (Callback)：

从 HTTP GET 请求 节点的 On Complete（或类似的输出脉冲/委托）拉出。

创建一个 Custom Event。该事件通常带有两个关键参数：Success (Boolean) 和 Content (String)。

4. 响应解析与结果展示

在回调的自定义事件中：

分支 (Branch)：判断 Success 是否为 True。

JSON 解析：

将 Content 字符串传入 Load JSON from String 节点。

Get Object Array Field: 字段名输入 features。

Get Array Item: 索引设为 0。

Get Object Field: 字段名输入 properties。

获取具体值：

从 properties 对象中使用 Get String Field 或 Get Number Field，输入你的地块属性字段名（如 land_type 或 area）。

UI 刷新：将获取的属性值传给 UI 界面，显示用地类型和面积，从而消除 (Elimination) 信息获取的延迟感。

5. 消除 (Elimination) 报错的排查清单

空格问题：POINT(经度 纬度) 括号内的空格不可忽略，否则 GeoServer 会报 SQL 语法错误。

坐标系：如果 GeoServer 默认不是 EPSG:4326，你可能需要在 URL 中额外追加 &srsName=EPSG:4326 以消除 (Elimination) 坐标投影偏移。

字段名大小写：GeoServer 对字段名大小写敏感，请确保蓝图中的字符串与数据库/图层预览中的字段名完全一致。

通过这种“拼接 -> 请求 -> 回调解析”的链路，你可以快速实现从地图点击到后台数据获取的闭环逻辑。

---

## 21. 在Load JSON from String节点后搜索不到Get Object Array Field节点

**问题：** 在Load JSON from String节点后搜索不到Get Object Array Field节点

**答案：** 在 Unreal Engine 的官方插件 JSON Blueprint Utilities 中，节点的命名和行为与一些常见的第三方插件（如 VaRest）有所不同。

搜索不到 Get Object Array Field 节点通常是因为你没有从正确的引脚类型拉出线条。请按照以下步骤操作，以消除 (Elimination) 节点查找障碍：

1. 必须从“JSON Object”引脚拉出

Load JSON from String 节点的输出引脚通常是一个名为 JsonObject 的蓝色对象引用（Object Reference）。

操作流：

找到 Load JSON from String 节点。

从它的 JSON Object（或者叫 Return Value）蓝色圆点引脚拉出连线。

在空白处松开，确保勾选 Context Sensitive。

搜索 “Get Field”。

2. 使用万能的“Get Field”节点

在官方插件中，并不是为每种类型（数组、对象、字符串）都准备了独立名称的节点，而是通过一个通用的 Get Field 节点来实现。

关键设置：

放置 Get Field 节点。

在节点的详细面板（Details）中，或者节点本身的下拉菜单里，寻找 Field Type。

将类型设置为 Object Array（如果你要解析的是 features 字段）。

在 Field Name 中输入 features。

3. 如果使用的是旧版或特定插件（替代节点名）

如果你确定使用的是官方插件且上述方法不适用，请尝试搜索以下完全匹配的名称：

Get Array Field (直接针对数组字段)

Get Field -> As Array (先获取字段，再转换类型)

4. 针对 GeoJSON 的解析路径 (Graph Recipe)

为了解析 GeoServer 返回的数据，请确保你的解析链路如下：

Get Field (Field Name: features, Type: Object Array) -> 得到一个数组。

Get (a copy) -> 获取索引为 0 的元素（这是一个 Json Object）。

Get Field (从索引 0 的物体拉出, Field Name: properties, Type: Object) -> 得到属性集合。

Get Field (从属性物体拉出, Field Name: 用地类型字段名, Type: String) -> 得到最终结果。

5. 消除 (Elimination) 报错建议

检查空值：在 Load JSON from String 之后，先用一个 Is Valid 节点检查返回的 Json 对象是否合法，以消除 (Elimination) 因格式错误导致的崩溃。

大小写敏感：JSON 的键名（Key）如 features 必须全部小写，这与 GeoJSON 标准一致。

通过拉取 JSON Object 引脚并搜索 Get Field 并切换类型，你可以顺利找到所需的解析功能，消除 (Elimination) 无法读取数据层级的技术瓶颈。

---

## 22. 我的Get Field节点没有将类型设置为 Object Array、Object、String的选项

**问题：** 我的Get Field节点没有将类型设置为 Object Array、Object、String的选项

**答案：** 如果你发现 Get Field 节点没有下拉菜单或类型设置选项，这通常是因为你使用的是 UE 官方内置的 Json Blueprint Utilities 插件，它的设计逻辑是基于“引脚自动推断”或“特定节点拆分”，而不是像 VaRest 插件那样在一个节点里切换。

请按照以下步骤重新操作，以消除 (Elimination) 解析逻辑的阻塞：

1. 寻找“Try Get…”系列节点 (UE5 官方标准)

在官方插件中，为了提高严谨性，它使用了 Try Get 命名的专用节点。请从 Json Object 引脚拉出后搜索以下准确名称：

解析 features：搜索 Try Get Array Field。

Field Name 填入 features。

输出是一个 Json Value 数组。

解析 properties：搜索 Try Get Object Field。

Field Name 填入 properties。

解析具体文字：搜索 Try Get String Field。

2. 处理 Json Value 到 Json Object 的转换

官方插件中，数组里的每一项最初都是 Json Value 类型，你需要转换后才能继续获取它内部的字段：

从 Try Get Array Field 的 Out Array 输出引脚连接一个 Get (a copy) 节点（获取第 0 项）。

从该 Get 节点的输出引脚拉出线，搜索并调用 As Object。

现在你得到了一个 Json Object，从它拉出线，再次调用 Try Get Object Field（Field Name 填 properties）。

同理，从 properties 输出拉出线，调用 As Object，再调用 Try Get String Field。

3. 另一种可能：使用的是“Get Field”通用节点（变色逻辑）

如果你的节点叫 Get Field 且只有 Value 输出引脚：

它是变色引脚。你直接将 Value 引脚连接到你想要的变量类型上，节点会自动改变其返回类型。

例如：你将 Value 连到一个 String 数组 变量上，它就会尝试按数组解析。

4. 完整的 GeoJSON 解析路径清单 (官方插件版)

为了确保你能顺利拿到数据并消除 (Elimination) 解析失败，请按此顺序连线：

Load JSON from String -> 得到 RootObject。

从 RootObject 拉出 -> Try Get Array Field (Name: features)。

从 Out Array 引脚拉出 -> Get (Copy) (Index: 0)。

从 Item 引脚拉出 -> As Object。

从该对象拉出 -> Try Get Object Field (Name: properties)。

从 Out Object 拉出 -> As Object（再次转换以确保类型正确）。

从该对象拉出 -> Try Get String Field (Name: 你的字段名)。

Result -> 连入 UI 文本。

5. 性能与排查建议

消除 (Elimination) 崩溃风险：Try Get 系列节点都有一个 Return Value (Bool)。在解析前用 Branch 判断一下是否获取成功，避免因为 GeoServer 返回空数据而导致逻辑报错。

检查字段名：GeoJSON 结构非常深，请务必确认 features -> properties 这个层级关系没有写错。

通过使用 Try Get Array Field 配合 As Object 节点，你可以精确地导航到 JSON 的最深层，从而成功消除 (Elimination) 解析障碍。

---

## 23. 用geoserver加载的WebMapServiceRasterOverlay图层，通过UE蓝图实现点击获取用地类型、面…

**问题：** 用geoserver加载的WebMapServiceRasterOverlay图层，通过UE蓝图实现点击获取用地类型、面积等属性值中获取经纬度与屏幕位置的详细蓝图连线步骤

**答案：** 在使用 WebMapServiceRasterOverlay (WMS) 或 3D Tiles 时，获取点击位置的地理坐标（经纬度）是关键的第一步。你需要通过射线检测获取世界坐标，再利用 Cesium Georeference 将其转换为地理坐标。

以下是实现这一过程的详细蓝图连线步骤，旨在消除 (Elimination) 坐标转换中的精度偏差：

1. 射线检测：从屏幕获取世界位置 (World Position)

在 Player Controller 蓝图中：

事件：左键点击 (Left Mouse Button) 或 Touch。

节点：Get Hit Result Under Cursor by Channel：

Trace Channel: 选择 Visibility。

bTraceComplex: 勾选（以确保能精确点击到地形起伏，消除 (Elimination) 点击空域的风险）。

节点：Break Hit Result：

从 Hit Result 引脚拉出，展开所有信息。

找到 Location（这是物体在虚幻引擎中的世界空间坐标 FVector）。

2. 坐标转换：从虚幻世界到经纬度 (Lat/Lon)

你需要场景中 CesiumGeoreference 演员的引用来执行此转换。

获取引用：在蓝图中找到或通过 Get Actor of Class 获取 CesiumGeoreference 实例。

节点：Inaccurate Transform World to Ellipsoid WGS84（或者名称类似的 Transform Unreal to Longitude Latitude Height）：

Target: 连接 CesiumGeoreference 引用。

Unreal Position: 接入上一步 Break Hit Result 得到的 Location。

解析输出：该节点会输出一个 Vector（或拆分为三个 Double/Float）：

X: 经度 (Longitude)

Y: 纬度 (Latitude)

Z: 高度 (Height)

3. 构建 HTTP 请求字符串 (详细连线逻辑)

现在你有了 Lat 和 Lon，按照以下顺序连线以构建 WFS 过滤查询字符串：

节点：Append (String)：点击 “Add Pin” 直到有 H 个引脚。

A: http://你的IP:端口/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=工作空间:图层名&outputFormat=application/json&cql_filter=CONTAINS(geom, POINT(

B: 接入转换得到的 Longitude。

C: 输入一个空格 " "。

D: 接入转换得到的 Latitude。

E: 输入 ))

验证：此时得到的字符串应类似于：...POINT(120.123 30.456))。这种格式能有效消除 (Elimination) GeoServer 解析几何图形时的语法错误。

4. 发送请求与响应流程 (Summary)

节点：HTTP GET 请求（或官方 Create HTTP Request）：接入上述生成的 URL。

回调事件：在请求完成后，按照之前步骤解析 JSON。

UI 更新：将解析出的 land_type 和 area 传递给 UMG 的 Set Text。

5. 关键注意事项以消除 (Elimination) 常见故障

点击穿透：如果你的点击没有反应，请检查 WMS 图层或地形是否有碰撞（Collision）。如果没有碰撞，射线检测无法产生 Hit Result。

精度设置：由于经纬度需要高精度，确保在 Append 时，浮点数转字符串没有被过度截断。默认转换通常足够，但如果点击偏离严重，请检查 CesiumGeoreference 的 Origin 设置。

坐标顺序：GeoServer 默认通常是 POINT(经度 纬度)。如果查询不到，尝试调换经纬度引脚顺序，以消除 (Elimination) 因 GIS 坐标轴定义不同（Lon/Lat vs Lat/Lon）导致的查询落空。

通过这一套“射线拾取 -> 坐标转换 -> 动态拼接 -> 异步请求”的蓝图链路，你可以完美实现“点击地图即刻获取属性”的功能。

---

## 24. 构建 HTTP 请求WMS查询字符串时append节点如何设置

**问题：** 构建 HTTP 请求WMS查询字符串时append节点如何设置

**答案：** 在构建 GeoServer 的 WFS 查询字符串（用于点击获取属性）时，Append 节点的配置至关重要。为了消除 (Elimination) 因格式错误导致的查询失败，请严格按照以下引脚配置进行设置。

1. 节点配置：Append (String)

点击 Append 节点底部的 Add Pin，确保至少有 G 或 H 个引脚（取决于你是否需要设置坐标参考系）。

引脚 A (基础 URL 与参数):
http://你的IP:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=工作空间:图层名&outputFormat=application/json&cql_filter=CONTAINS(geom, POINT(
(注意：最后有一个左括号)

引脚 B (经度):
连接 Cesium 转换出的 Longitude (经度) 变量。

引脚 C (分隔符):
 (输入一个空格。这是 POINT 语法要求的，必须严格执行以消除 (Elimination) 语法报错)。

引脚 D (纬度):
连接 Cesium 转换出的 Latitude (纬度) 变量。

引脚 E (结束符):
))
(注意：这是闭合 POINT 和 CONTAINS 函数的括号)。

2. 进阶推荐：使用 Format Text 节点

相比于 Append 节点，使用 Format Text 节点能更直观地观察字符串结构，有效消除 (Elimination) 拼接时的视觉混乱：

添加 Format Text 节点。

在 Format 框中输入以下内容（可以直接复制，注意大括号内的名称）：
{BaseURL}&cql_filter=CONTAINS(geom, POINT({Lon} {Lat}))

此时节点会自动生成三个输入引脚：

BaseURL: 输入你的 GeoServer WFS 基础路径（包含 typeName 等）。

Lon: 连接经度变量。

Lat: 连接纬度变量。

优点：这种方式能一眼看出经纬度之间是否有空格，从而消除 (Elimination) 拼接错误。

3. WFS 与 WMS 的区别提醒

虽然你在问题中提到了 WMS 图层，但要获取具体的“用地类型”和“面积”等矢量属性字段，通常是通过 WFS (Web Feature Service) 接口进行查询。

WMS 是图片，通常使用 GetFeatureInfo。

WFS 是矢量数据，使用 GetFeature 配合 cql_filter。

建议：即使你显示的是 WMS 图层，点击查询时建议使用上述 WFS + CQL_FILTER 的方式，这能更精准地消除 (Elimination) 点击位置偏移带来的干扰。

4. 消除 (Elimination) 故障的最后检查

编码问题：如果你的工作空间或图层名包含中文，请务必先在浏览器中测试 URL 是否需要进行 URL Encoding，以消除 (Elimination) 字符解析乱码。

坐标参考系：如果点击始终没有返回结果，可以在 URL 结尾追加 &srsName=EPSG:4326。

Geometry 字段名：CONTAINS(geom, ...) 中的 geom 必须与你 GeoServer 中图层的几何字段名一致（有时是 the_geom 或 geometry），请在 GeoServer 图层预览中确认以消除 (Elimination) 字段名不匹配的问题。

通过这样精确的引脚设置，你构建的请求将能够准确穿透图层，获取到后台数据库中的属性信息。

---

## 25. 用geoserver加载的WebMapServiceRasterOverlay图层，通过UE蓝图实现点击获取用地类型、面…

**问题：** 用geoserver加载的WebMapServiceRasterOverlay图层，通过UE蓝图实现点击获取用地类型、面积等属性值中发送请求与响应流程的详细蓝图连线步骤

**答案：** 在 Unreal Engine 中，点击 WMS 图层并获取属性的完整流程是：发起请求 -> 异步等待 -> 解析响应 -> 更新 UI。为了消除 (Elimination) 逻辑混乱，建议在 PlayerController 中实现以下详细连线步骤：

1. 发起请求逻辑 (The Request)

使用官方 Http Blueprint 插件的节点，这能提供最稳定的异步处理能力。

节点：Create HTTP Request：在射线检测和 URL 拼接（使用 Append 或 Format Text）之后放置。

节点：Set URL：

Target: 连接 Create HTTP Request 的返回值。

URL: 连接你拼接好的 WFS 查询字符串。

节点：Set Verb：

Target: 连接请求对象。

Verb: 输入 GET。

节点：Process Request (Latent)（推荐使用延迟节点）：

Target: 连接请求对象。

注意：使用 Latent 版本可以直接在节点后面继续连线，无需手动创建自定义事件回调，能有效消除 (Elimination) 复杂的委托绑定。

2. 响应成功判定 (The Response Check)

在 Process Request (Latent) 执行完成（Completed）后的输出端：

节点：Branch (分支)：判断请求是否真正成功。

Condition: 连接 Process Request 的 Was Successful 引脚。

节点：Get Content as String：

从 Branch 的 True 端拉出。

Target: 连接同一个 HTTP Request 对象。

Return Value: 这就是 GeoServer 返回的 JSON 文本字符串。

3. JSON 深度解析 (The Parsing)

利用 Json Blueprint Utilities 插件将字符串转换为可读取的属性。为了消除 (Elimination) 编译错误，请严格按此路径：

节点：Load JSON from String：将 Content 接入。

节点：Try Get Array Field：

JsonObject: 接入 Load JSON from String 的输出。

Field Name: 输入 features。

节点：Get (a copy)：从 Out Array 连出，Index 设为 0。

节点：As Object：将 Item 转换为 Json 对象。

节点：Try Get Object Field：

Field Name: 输入 properties。

节点：As Object：将 Out Object 再次转换为 Json 对象。

节点：Try Get String Field / Try Get Number Field：

从上面的 Object 连出。

Field Name: 输入你在 GeoServer 中定义的字段名（如 用地类型 或 Shape_Area）。

4. 数据推送到 UI (The Display)

将解析出的结果展示在界面上。

获取引用：拖入你之前保存的 MyHUD (Widget 变量)。

节点：Set Text (Txt_用地类型)：

从 MyHUD 拉出搜索获取文本框变量。

接入 Try Get String Field 的结果。

节点：Set Text (Txt_面积)：

同理接入数值字段结果（系统会自动执行 ToText 转换）。

5. 消除 (Elimination) 异常情况的提示

为了提升用户体验，建议在 Branch 的 False 端增加报错反馈：

节点：Print String：打印一条消息“服务器响应失败”。

UI 反馈：调用 Set Text 将文本框内容改为“查询无结果”，以消除 (Elimination) 玩家因界面无响应而产生的困惑。

总结 Checklist

[ ] 使用了 Process Request (Latent) 以简化回调逻辑。

[ ] 在解析 features 和 properties 之间使用了 As Object 进行类型转换。

[ ] 所有的 Try Get 节点都连接了执行脉冲线（白色线）。

通过这套严谨的连线方案，你将能够消除 (Elimination) 地理数据获取过程中的所有技术瓶颈，实现点击即显的智慧城市交互效果。

---

## 26. 用geoserver加载的WebMapServiceRasterOverlay图层，通过UE蓝图实现点击获取用地类型、面…

**问题：** 用geoserver加载的WebMapServiceRasterOverlay图层，通过UE蓝图实现点击获取用地类型、面积等属性值中使用HTTP GET 请求节点发送请求与响应流程的详细蓝图连线步骤

**答案：** 如果你使用的是带有 “HTTP GET 请求” 节点的简化版插件（通常为单节点异步触发模式），其逻辑比官方原生节点更加集中。这种节点通常集成了创建、设置和发送的过程。

为了消除 (Elimination) 连线中的逻辑错误，请按照以下步骤进行详细连线：

1. 发起请求阶段 (The Request)

在射线检测和 URL 拼接逻辑（使用 Append 节点生成 WFS 地址）之后：

放置节点：HTTP GET 请求（通常是一个带有时钟图标的异步节点）。

设置 URL：将 Append 节点的输出引脚连接到该节点的 URL 输入参数上。

可选设置 Headers：如果你有“创建请求头文件”节点，将其输出连接到 Headers。如果没有，通常该节点会有默认配置，足以获取 JSON 结果。

触发执行：将射线检测后的执行脉冲（白色线）连入该节点。

2. 响应分支处理 (The Response Handling)

该节点通常会有多个输出执行引脚，用于处理不同的网络结果，以消除 (Elimination) 程序挂起的风险：

On Success (成功时)：连接主要的解析逻辑。

On Fail (失败时)：连接一个 Print String 节点，显示“网络请求失败”，用于排查网络或防火墙问题。

结果输出：找到该节点上的 Response String（或名为 Content / Result 的字符串引脚）。

3. JSON 数据解析链路 (The Parsing Recipe)

这是最容易出错的地方，必须通过明确的类型转换来消除 (Elimination) 编译失败：

节点：Load JSON from String：将请求节点的 Response String 接入。

节点：Try Get Array Field：

Field Name: 输入 features。

说明：GeoJSON 标准将所有要素放在 features 数组中。

节点：Get (a copy)：从 Out Array 引脚连出。

Index: 保持为 0（点击通常只取第一个地块要素）。

节点：As Object：将 Get 的输出项（Json Value）转换为 Json Object。

节点：Try Get Object Field：

JsonObject: 接入上一步的输出。

Field Name: 输入 properties。

说明：属性信息（如面积、用地类型）都嵌套在此对象内。

节点：As Object：将 Out Object 引脚再次连入一个新的 As Object 节点。

注意：这一步是消除“Value 类型尚未确定”报错的关键。

获取具体值：

从最后的 As Object 拉出：连接 Try Get String Field (Name: 用地类型字段名)。

从同一个 Object 拉出：连接 Try Get Number Field (Name: 面积字段名)。

4. UI 界面刷新 (The Display)

获取 UI 引用：拖入你之前保存的 MyHUD (Widget 变量)。

设置文本节点：

从 MyHUD 拉出，调用 Set Text (用地类型文本框)。

从 MyHUD 拉出，调用 Set Text (面积文本框)。

连接数据：将解析出的字符串和数值分别接入对应的 In Text 引脚。

5. 消除 (Elimination) 常见故障的最后检查

WFS 协议检查：请确保 URL 中的 outputFormat=application/json 拼写正确。如果 GeoServer 返回的是 XML 格式，Load JSON from String 会返回空值并导致后续报错。

数组长度检查：在 Get (a copy) 之前，可以先判断数组长度是否大于 0。如果点击到了没有数据的区域，数组为空，直接获取第 0 项会导致消除 (Elimination) 崩溃。

字段匹配：用地类型和面积的字段名（Key）必须与 GeoServer 图层定义的属性表字段完全一致（注意区分中英文及大小写）。

按照此步骤操作，你的蓝图将能够稳健地发送请求并精准解析出复杂的 GeoJSON 数据，消除 (Elimination) 任何通信与解析上的障碍。

---

## 27. 节点 Http Get请求 已尝试将结果主体反序列化为一个 wildcard 。支持类型是字符串和结构体

**问题：** 节点 Http Get请求 已尝试将结果主体反序列化为一个 wildcard 。支持类型是字符串和结构体

**答案：** 这个错误是由于 HTTP GET 请求 节点的“通配符 (Wildcard)”引脚无法自动判断你想要的输出类型导致的。为了消除 (Elimination) 这个编译报错，你需要明确告诉节点将结果主体（Response Body）作为 String 类型输出。

以下是解决该问题的详细操作步骤：

1. 强制指定输出类型

该节点通常有一个名为 Response Body 或 Result 的灰色通配符引脚。

解决方法：从该 Response Body 灰色引脚拉出线条，连接到一个 Print String 节点，或者直接连接到 Load JSON from String 节点的输入端。

关键动作：一旦你将其连接到接收字符串（String）的输入端，通配符引脚会自动变为粉红色（字符串颜色），错误即刻消除 (Elimination)。

2. 使用临时变量辅助（如果直接连接无效）

如果直接连线仍报错，可以使用中间变量来显式指定类型：

在蓝图中创建一个 String 类型的局部变量，命名为 TempResponseBody。

将 HTTP 节点的 Response Body 引脚连接到该变量的 Set 节点上。

这样编译器就会明确知道该通配符引脚应该处理为字符串，从而消除 (Elimination) 反序列化的歧义。

3. 构建正确的响应逻辑链路 (Graph Recipe)

请确保你的节点连接顺序如下，以保证类型安全：

HTTP GET 请求 (节点)

URL: 接入你的 WFS 拼接字符串。

Response Body (Wildcard) -> [连入] -> Load JSON from String (节点的 Json String 输入引脚)。

Load JSON from String (节点)

从此处开始后续的 Try Get Array Field 解析逻辑。

4. 为什么会出现此错误？

这个报错的根本原因是该节点具备将 JSON 直接反序列化为“结构体 (Struct)”的高级功能。由于你没有给它提供一个具体的结构体模板，它处于“未确定”状态。

由于我们要处理的是复杂的 GeoJSON（包含 features 数组和 properties 嵌套对象），很难用简单的结构体一次性接收。

最佳实践：将其作为 String 读入，然后交给专门的 JSON 插件节点手动解析，这样能更灵活地获取“用地类型”和“面积”字段，同时消除 (Elimination) 类型匹配失败的风险。

5. 消除 (Elimination) 报错后的检查

编译 (Compile)：连接好 String 输入后再次点击编译，警告应消失。

空值判断：在 Load JSON from String 之后，一定要接一个 Branch 判断解析是否成功，以消除 (Elimination) 网络波动返回非 JSON 内容（如 404 错误页）导致的逻辑崩溃。

通过这种强制类型连接，你可以绕过通配符的自动识别机制，确保数据流能够顺利进入解析阶段。

---

## 28. 用geoserver加载的WebMapServiceRasterOverlay图层，通过UE蓝图实现点击获取用地类型、面…

**问题：** 用geoserver加载的WebMapServiceRasterOverlay图层，通过UE蓝图实现点击获取用地类型、面积等属性值中使用Get Field节点JSON 数据解析的详细蓝图连线步骤

**答案：** 使用 Get Field 节点进行解析时，最关键的是要通过“连线推断”来确定其灰色通配符引脚的类型。为了消除 (Elimination) “类型尚未确定”的编译错误，请严格按照以下步骤进行链式连接：

1. 解析根对象与 Features 数组

节点：Load JSON from String

将 HTTP 请求返回的字符串连入。

节点：Get Field

Target: 接入 Load JSON from String 的 JsonObject。

Field Name: 输入 features。

确定类型 (关键)：从 Get Field 的 Value 引脚拉出线条，连接到一个 As Array 节点。

此时 Get Field 会自动识别为数组类型，报错消除 (Elimination)。

2. 获取具体要素 (Feature)

节点：Get (a copy)

从 As Array 的输出引脚连入。

Index: 0。

节点：As Object

将 Get 的结果转换为 Json 对象。

3. 进入 Properties 属性层级

节点：Get Field

Target: 接入上一步的 As Object。

Field Name: 输入 properties。

确定类型：从 Value 引脚拉出线条，连接到一个 As Object 节点。

这一步让蓝图明白你在读取一个嵌套的对象，进一步消除 (Elimination) 解析障碍。

4. 提取最终数值（用地类型与面积）

现在你已经进入了 properties 内部，可以提取具体的业务数据了：

获取用地类型：

节点：Get Field (Target 连入上一步的 As Object)。

Field Name: 输入你 GeoServer 中的字段名。

Value: 连入一个 As String 节点。

获取面积：

节点：Get Field (Target 连入同一个 As Object)。

Field Name: 输入面积对应的字段名。

Value: 连入一个 As Float (或 As Number) 节点。

5. 将结果设置到 UMG

获取引用：拉入你的 MyHUD 变量。

节点：Set Text (Txt_用地类型)：接入 As String 的输出。

节点：Set Text (Txt_面积)：接入 As Float 的输出（系统会自动生成 ToText 节点）。

6. 消除 (Elimination) 逻辑风险的总结

链式转换：记住公式：Get Field -> As 类型。只有连接了“As 类型”节点，Get Field 的通配符才能被激活。

空引用预防：在每一个 As Object 之后，可以使用一个 Is Valid 节点，确保 GeoServer 返回的数据确实包含该层级，从而消除 (Elimination) 因点击到地图边缘（无数据区）导致的程序崩溃。

字段名匹配：务必确认 GeoJSON 中的 Key 值。你可以先用 Print String 打印出整个 Response Body，在输出日志中核对 用地类型 等字段的精确拼写。

按照这套“获取-转换-再获取”的循环逻辑，你可以精准地从复杂的 GeoJSON 中消除 (Elimination) 无关信息，提取出核心的属性数值。

---

## 29. 我在Http Get请求节点中设置请求不成功则输出字符串“网络请求失败”，运行后点击WebMapServiceRaste…

**问题：** 我在Http Get请求节点中设置请求不成功则输出字符串“网络请求失败”，运行后点击WebMapServiceRasterOverlay输出了“网络请求失败”

**答案：** 出现“网络请求失败”通常意味着请求根本没有到达 GeoServer，或者 GeoServer 拒绝了请求。要消除 (Elimination) 这个故障，我们需要按以下步骤进行排查：

1. 验证生成的 URL (最关键的一步)

这是消除 (Elimination) 错误的首要任务。

操作：在 HTTP GET 请求 节点之前，增加一个 Print String 节点，将拼接好的 URL 打印到屏幕上。

核对：

IP 地址：如果你在虚幻引擎中运行，确保不要使用 localhost 或 127.0.0.1。建议使用机器的具体局域网 IP（如 192.168.x.x）。

空格：检查 POINT(经度 纬度) 之间是否有且仅有一个空格。

特殊字符：如果 URL 中包含中文字符（如图层名或工作空间名），必须进行 URL 编码，否则请求会直接失败。

2. 浏览器直接测试

将屏幕上打印出来的那个完整 URL 复制，直接粘贴到浏览器的地址栏中访问。

结果 A：浏览器也打不开 -> 说明是 GeoServer 服务、防火墙或 URL 语法本身的问题。

结果 B：浏览器能返回 JSON -> 说明 GeoServer 没问题，是虚幻引擎的网络权限或插件配置问题。

3. 检查 GeoServer WFS 服务配置

启用 WFS：进入 GeoServer 后台，确保 Services 菜单下的 WFS 已勾选启用。

跨域设置 (CORS)：虽然 UE 客户端通常不受 CORS 限制，但某些网络环境下仍需确保 GeoServer 允许外部请求。

端口号：确保端口（默认 8080）未被防火墙拦截。尝试在 Windows 防火墙中为该端口创建一个“入站规则”以消除 (Elimination) 拦截。

4. 检查 WebMapServiceRasterOverlay 的碰撞 (Collision)

虽然这通常导致“没反应”而不是“请求失败”，但仍需确认：

射线检测失败：如果射线没有检测到任何物体，Hit Result 为空，那么转换出的经纬度可能是 (0,0) 或非法值。

消除 (Elimination) 方法：在打印 URL 的同时，打印转换出的 Longitude 和 Latitude。如果数值全是 0，说明点击没生效。

5. 常见语法细节纠错 (Syntax Elimination)

请检查你的 Append 节点中是否存在以下细微错误：

CQL 过滤语法：&cql_filter=CONTAINS(geom,POINT(120 30))。注意 geom 是否与你图层里的几何字段名一致。

输出格式：确保包含 &outputFormat=application/json。如果 GeoServer 默认只输出 XML，而你的节点强制要求 JSON，可能会导致解析层的“失败”。

6. 调试建议 (Summary)

Print URL：这是解决问题的地图。

检查防火墙：暂时关闭防火墙测试，以消除 (Elimination) 网络屏蔽。

简化测试：先去掉 cql_filter 部分，只请求前 10 个要素（maxFeatures=10），看能否请求成功。如果简化版成功了，说明问题出在 CQL 拼接上。

按照这个逻辑顺序，你一定能找到导致“网络请求失败”的具体环节并将其消除 (Elimination)。

---

## 31. 修改后重新打开网页出现如下信息：This XML file does not appear to have any st…

**问题：** 修改后重新打开网页出现如下信息：This XML file does not appear to have any style information associated with it. The document tree is shown below.

 Illegal property name: geom for feature type UE_JiJiHu:landuse

**答案：** 报错信息 Illegal property name: geom 明确指出，在你的图层 UE_JiJiHu:landuse 中，不存在名为 geom 的几何属性列。

在 GeoServer 中，几何字段的名称是由原始数据（如 Shapefile 或数据库表）决定的。虽然很多教程使用 geom 作为示例，但实际名称往往不同。要消除 (Elimination) 此错误，请执行以下步骤查找并修正正确的字段名：

1. 查找正确的几何字段名 (How to find the name)

请通过以下两种方式之一确认你的字段名：

方式 A：通过 GeoServer 后台查看：

登录 GeoServer，点击左侧菜单的 Layers (图层)。

点击你的图层 landuse 进入编辑页面。

切换到 Data (数据) 选项卡，向下滚动到 Feature Type Details (要素类型详细信息) 列表。

查看类型为 Point、Polygon 或 MultiPolygon 的那一行，Property (属性) 列下显示的名称就是你要用的（常见的名称有 the_geom、geometry、shape 等）。

方式 B：通过浏览器请求查看：
访问此 URL（去掉过滤条件）：
http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=DescribeFeatureType&typeName=UE_JiJiHu:landuse
在返回的 XML 中搜索 type="gml:GeometryPropertyType" 或类似的几何类型，其对应的 name 属性值即为正确名称。

2. 修正蓝图中的 Append 连线步骤

一旦你找到了正确的字段名（假设是 the_geom），请立即修改蓝图中的 Append 或 Format Text 节点：

引脚 A (或 Format 文本)：
将 ...CONTAINS(geom,POINT(
修改为 ...CONTAINS(the_geom,POINT(
(将其中的 geom 替换为你实际查到的名称)。

3. 验证步骤

在虚幻引擎中重新点击运行。为了确保万无一失，你可以先在浏览器中手动输入修改后的 URL 进行测试：
http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=CONTAINS(你的几何字段名,POINT(88.834102 44.775409))

4. 消除 (Elimination) 潜在风险提示

坐标参考系 (SRS)：如果修正字段名后返回的结果依然为空（但不再报错），可能是因为经纬度顺序或参考系不匹配。可以在 URL 结尾尝试添加 &srsName=EPSG:4326。

大小写敏感：某些数据库对字段名的大小写非常敏感，请确保蓝图中的拼写与 GeoServer 后台显示的完全一致，以消除 (Elimination) 匹配失败的可能性。

通过消除 (Elimination) 这个不正确的占位符名称 geom 并替换为真实的几何字段名，你的 WFS 查询将能够成功穿透并返回包含“用地类型”和“面积”的 JSON 数据。

---

## 32. 修改后重新打开网页出现如下信息：{"type":"FeatureCollection","features":[],"t…

**问题：** 修改后重新打开网页出现如下信息：{"type":"FeatureCollection","features":[],"totalFeatures":0,"numberMatched":0,"numberReturned":0,"timeStamp":"2026-06-05T03:51:15.756Z","crs":null}

**答案：** 现在返回的 JSON 数据显示 features: [] 且 numberMatched: 0，这说明你的 HTTP 请求已经完全正确（不再报错），但 GeoServer 在你点击的坐标点上没有找到任何地块要素。

为了消除 (Elimination) 这种“查询落空”的情况，请按以下三个步骤调整你的请求逻辑：

1. 交换经纬度顺序 (最常见的地理坐标问题)

GeoServer 遵循不同的标准，很多时候 EPSG:4326 的 WFS 请求默认期望的顺序是 纬度 经度 (Lat Lon)，而不是经纬度。

操作：在你的 Append 或 Format Text 节点中，将原本的 {Lon} {Lat} 交换顺序，变为 {Lat} {Lon}。

示例：尝试访问 POINT(44.775409 88.834102)。

2. 增加坐标参考系声明 (Explicit SRS)

为了消除 (Elimination) GeoServer 对坐标定义的歧义，必须在 URL 中明确告诉它你发送的是经纬度。

操作：在 URL 字符串的末尾追加以下参数：
&srsName=EPSG:4326

完整 URL 示例：
...&cql_filter=CONTAINS(the_geom,POINT(88.834 44.775))&srsName=EPSG:4326

3. 将 CONTAINS 替换为 INTERSECTS (容差处理)

CONTAINS 是极其精确的包含关系。由于点击转换可能存在微小的浮点数误差，或者你的点刚好在边界线上，会导致匹配失败。

操作：将 CQL 过滤中的 CONTAINS 替换为 INTERSECTS。

理由：INTERSECTS（相交）比 CONTAINS 容错率更高，能更有效地消除 (Elimination) 因数学计算精度导致的查询落空。

4. 调试步骤建议

手动测试已知点：在浏览器中输入一个你确定在该地块内部的坐标点。

检查 GeoServer 里的数据范围：

在 GeoServer 图层设置的 Data 选项卡中，检查 Native Bounding Box。

确保你的坐标（88.8, 44.7）确实在这个范围内。

消除 (Elimination) 坐标偏离：

如果数据是加密坐标（如 GCJ-02），而你点击获取的是 WGS-84（标准经纬度），也会因为坐标偏移几百米而点不到地块。

总结修正后的蓝图配置推荐：
使用 INTERSECTS + 交换经纬度 + 追加 srsName。

例如：...&cql_filter=INTERSECTS(the_geom, POINT({Lat} {Lon}))&srsName=EPSG:4326

只要通过这几项调整，你就能成功消除 (Elimination) 空结果，从而在 features 数组中获得包含用地类型和面积的 JSON 要素。

---

## 33. 我输入了以下网址：http://192.168.31.58:8080/geoserver/wfs?service=WFS…

**问题：** 我输入了以下网址：http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=INTERSECTS(the_geom,POINT(88.840525%2044.781866))&srsName=EPSG:4539，得到的网页信息如下：{"type":"FeatureCollection","features":[],"totalFeatures":0,"numberMatched":0,"numberReturned":0,"timeStamp":"2026-06-05T03:58:03.973Z","crs":null}

**答案：** Sorry, I can’t answer your question. Please rephrase it and try again.

---

## 34. 我修改的URL网址如下：http://192.168.31.58:8080/geoserver/wfs?service=…

**问题：** 我修改的URL网址如下：http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=INTERSECTS(the_geom,POINT(88.840525%2044.781866))&srsName=EPSG:4539。返回的 JSON 数据显示 features: [] 且 numberMatched: 0，但 GeoServer 在你点击的坐标点上没有找到任何地块要素，这和我设置的图层坐标系有关吗

**答案：** 是的，返回空结果与你设置的坐标系 EPSG:4539 有直接关系。

问题的核心在于 单位不匹配：你提供的坐标 (88.840525 44.781866) 是十进制度（Decimal Degrees），而 EPSG:4539（CGCS2000 / Gauss-Kruger CM 87E）是一个投影坐标系，它的单位是米（Meters）。

为了消除 (Elimination) 这种单位冲突导致的查询落空，请参考以下分析与解决方案：

1. 为什么会导致空结果？

单位偏差：当你告诉 GeoServer 使用 EPSG:4539 且点位是 (88.8, 44.7) 时，GeoServer 会认为你在寻找距离坐标原点仅 88.8米 和 44.7米 的地方。

地理实际位置：你的数据实际地理位置是在经度 88.8° 附近，换算成 EPSG:4539 的投影坐标应该是形如 (566600, 4959000) 这样巨大的数值（以米为单位）。

结果：GeoServer 在坐标轴极靠近 0 的位置（几百米范围内）找不到你的地块，因此消除 (Elimination) 了所有匹配项。

2. 解决方案：统一为地理坐标系查询 (推荐)

即使你的图层在 GeoServer 里是用 EPSG:4539 存储的，你依然可以使用经纬度进行查询，只要你声明输入的是 EPSG:4326。

请尝试修改 URL 如下：
将 srsName=EPSG:4539 修改为 srsName=EPSG:4326。

修改后的测试 URL：
http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=INTERSECTS(the_geom,POINT(88.840525 44.781866))&srsName=EPSG:4326

3. 如果依然返回空值，请检查轴序 (Axis Order)

在 WFS 1.0.0 版本中，坐标顺序通常是 经度 纬度。但如果声明了 EPSG:4326 后仍无结果，请尝试交换顺序：
POINT(44.781866 88.840525)

4. 在虚幻引擎蓝图中的操作建议

为了确保数据的准确提取并消除 (Elimination) 投影转换带来的误差：

核对 Native CRS：进入 GeoServer 图层设置，确认“本地坐标系 (Native CRS)”是否真的是 EPSG:4539。

强制转换：在蓝图拼接 URL 时，始终将末尾的 srsName 固定设置为 EPSG:4326。虚幻引擎获取的通常是 WGS84 经纬度，这与 4326 是匹配的。

消除 (Elimination) 坐标偏离风险：如果你的地块数据本身带有偏移（如 CAD 直接导入未校准），请在 GeoServer 的图层预览（Layer Preview）中使用 OpenLayers 查看该点正确的坐标数值。

通过将请求坐标系声明为 EPSG:4326，你就能让 GeoServer 自动完成从“度”到“米”的投影转换，从而成功消除 (Elimination) 因坐标系单位不统一导致的要素查找失败。

---

## 41. 动态构建 WFS 请求阶段，格式化URL后，执行请求使用http get 请求节点具体后续该如何连线

**问题：** 动态构建 WFS 请求阶段，格式化URL后，执行请求使用http get 请求节点具体后续该如何连线

**答案：** 在动态构建 URL 后，执行 HTTP GET 请求的连线逻辑需要分为发送请求和处理响应两个部分。你可以通过虚幻引擎内置的 HTTP Blueprint 插件或常用的 VaRest 插件来实现。

为了消除 (Elimination) 请求配置不当导致的失败，以下是具体的连线步骤：

1. 发送请求阶段 (Request Setup)

紧接在 Format Text 节点转换为 String 之后：

创建请求：添加 Create Http Request 节点。

设置 URL：从 Create Http Request 的输出引脚拉出线条，连接 Set URL。

将 Format Text 转出的 String 连入此处。

设置请求方法：从同一引脚拉出线条，连接 Set Verb。

在输入框中填入：GET（必须大写）。

绑定回调事件：从请求对象引脚拉出线条，搜索并连接 Bind Event to On Process Request Complete。

重要动作：从 Event 红圈引脚拉出线条，在空白处松开，选择 Add Custom Event，将其命名为 OnWFSResponseReceived。

正式发出请求：最后连接 Process Request 节点。

2. 处理响应阶段 (Response Handling)

在刚才创建的 OnWFSResponseReceived 自定义事件节点之后，我们需要解析数据并消除 (Elimination) 无效结果：

检查响应状态：连接一个 Branch。

条件连入 Was Successful 引脚。如果为 False，可以打印“服务器未响应”。

获取内容字符串：从 Response 引脚（如果有）或直接使用 Get Content as String 节点。

解析 JSON (以 VaRest 为例)：

连接 Construct Json Object from String。

获取 Features 数组：从结果拉出 Get Array Field，名称填 "features"。

检查数组长度：从数组拉出 Length，连接 Greater Than 0 的 Branch。这能有效消除 (Elimination) 因点击空地导致的结果为空。

提取属性：

如果长度 > 0，连接 Get Array Element (Index 0)。

从输出 Object 拉出 Get Object Field，名称填 "properties"。

从 properties 拉出 Get String Field，填入你的字段名（如 "land_type"）。

更新 UI：将最后得到的字符串连入你的 Text Widget 的 Set Text 节点。

3. 图表配方参考 (Graph Recipe)

[Format Text] -> [To String] 
 |
[Create Http Request] -> [Set URL] -> [Set Verb: GET] -> [Bind Event] -> [Process Request]
 |
 [Custom Event: OnWFSResponseReceived]
 |
 [Get Content as String]
 |
 [Construct Json Object]
 |
 [Get Array Field: "features"]
 |
 [Get Object Field: "properties"]
 |
 [Set Text (UI 控件)]
4. 消除 (Elimination) 常见故障点

消除 (Elimination) 异步错误：Process Request 是异步的。请确保你的变量（比如 UI 引用）在响应返回时依然有效，不要在点击后立即销毁发出请求的 Actor。

权限设置：如果 GeoServer 需要登录，你还需要在 Process Request 之前使用 Set Header 节点添加 Authorization 信息，但这在局域网测试中通常不是必须的。

消除 (Elimination) 多余字符：在 Format Text 的 URL 模板中，确保 POINT({X} {Y}) 之间是一个纯粹的半角空格，没有多余的换行符或特殊编码字符。

通过这套逻辑，你就能在点击场景的瞬间，将投影后的米制坐标发送出去，并精准地将返回的地理信息显示在 UI 界面上。

---

## 42. 没有Create Http Request节点可以用什么节点替代

**问题：** 没有Create Http Request节点可以用什么节点替代

**答案：** 如果您在搜索框中找不到 Create Http Request，通常是因为您使用的是虚幻引擎内置的 HTTP Blueprint 插件（该插件在 5.4 版本左右进行了节点重命名）或者您尚未安装第三方插件 VaRest。

为了消除 (Elimination) 节点缺失的障碍，您可以根据您启用的插件选择以下两种替代方案：

方案 A：使用内置 HTTP Blueprint 插件（推荐）

在 UE 5.3⁄5.4 的内置插件中，节点被整合得更加简洁。请尝试搜索以下名称：

Construct Google ARCore HTTP Request (虽然名字带有 ARCore，但它是通用的 HTTP 对象) 或者更通用的：

Make Http Request

使用通用异步节点（最简单）：搜索并使用 Wait for Http Request。

优点：这是一个“潜伏 (Latent)”节点，它把发送和等待结果整合在了一个节点上，消除 (Elimination) 了手动绑定回调事件的复杂连线。

连线逻辑：将 Format Text 的 URL 连入该节点的 URL 引脚，Verb 设置为 GET。当请求完成后，逻辑会直接从 On Completed 引脚继续执行。

方案 B：使用 VaRest 插件（工业标准）

如果您安装了 VaRest（可在 Fab 免费获取），这是目前开发者最常用的方案。

替代节点：Construct Json Request。

连线逻辑：

Construct Json Request -> Set Verb (GET) -> Apply URL (传入格式化后的 URL)。

绑定结果：从 Construct Json Request 的输出引脚拉出线条，搜索 Bind Event to On Request Completed。

方案 C：使用 C++ 包装的蓝图节点（终极消除方案）

如果您不想依赖任何外部插件，也可以通过 C++ 创建一个极简的静态函数库来消除 (Elimination) 蓝图节点的限制。

头文件 (.h):

UFUNCTION(BlueprintCallable, Category = "Http")
static void SimpleHttpGet(FString URL);
推荐的整合连线（基于内置插件的 Wait 节点）

为了让您的蓝图最清晰，建议使用 Wait for Http Request：

[Format Text] -> [To String]

[Wait for Http Request]

URL: 接入上面的 String。

Verb: GET。

[On Completed 引脚] -> [Get Content as String] -> [后续 JSON 解析逻辑]。

为什么找不到原始节点？

上下文过滤：请尝试取消勾选搜索框右上角的“上下文敏感 (Context Sensitive)”，这能消除 (Elimination) 因引脚不匹配导致的节点隐藏。

插件启用：请前往 Edit -> Plugins 确认 Http Blueprint 和 JSON Blueprint Utilities 这两个插件已勾选并重启了编辑器。

通过改用 Wait for Http Request 节点，您可以极大地简化连线流程，并快速消除 (Elimination) 无法发送请求的问题。

---

## 43. 使用 VaRest 插件在格式化URL后，执行http get 请求节点具体后续该如何连线

**问题：** 使用 VaRest 插件在格式化URL后，执行http get 请求节点具体后续该如何连线

**答案：** 使用 VaRest 插件处理 WFS 请求是虚幻引擎中最稳健的方案。它能自动处理 JSON 解析，极大简化了逻辑。

在 Format Text 节点将 URL 模板转换为字符串后，请按照以下步骤进行精确连线，以消除 (Elimination) 请求失败或数据无法读取的问题：

1. 发送请求阶段 (Request Setup)

接在 To String (Text) 之后：

创建请求对象：添加 Construct JSON Request 节点。

设置请求动作：从其输出引脚拉出，连接 Set Verb，在输入框手动输入 GET。

指定目标 URL：拉出引脚连接 Apply URL。

将 Format Text 转出的 String 连入此节点的 Url 输入引脚。

绑定完成事件：从 Apply URL 之前的请求对象引脚拉出，搜索 Bind Event to On Request Completed。

从 Event 引脚拉出，添加 Custom Event，命名为 WFS_Response_Success。

绑定失败事件（可选但推荐）：同样拉出引脚连接 Bind Event to On Request Fail。

添加自定义事件，命名为 WFS_Response_Failed，用于打印“网络连接异常”。

2. 解析响应阶段 (Response Handling)

在 WFS_Response_Success 事件之后，我们需要剥离 GeoJSON 的层级：

获取根对象：从事件提供的 Request 引脚拉出，连接 Get Response Object。

提取 Features 数组：从 Response Object 拉出，连接 Get Array Field，名称填入 "features"。

获取数组首项：从数组引脚拉出，连接 Get Array Element (Index 0)。

注：此时你会得到代表第一个地块的 Json Value，需将其转为 Object。

转换为 Json 对象：拉出引脚连接 As Object。

进入属性层：从 Object 引脚拉出，连接 Get Object Field，名称填入 "properties"。

读取字段值：从 properties 对象拉出，连接 Get String Field，填入你在 GeoServer 中定义的字段名（如 "land_type"）。

更新 UI：将得到的字符串连入你的 Text Widget 引用。

3. 连线逻辑配方 (Graph Recipe)

[Format Text] -> [To String]
 |
[Construct JSON Request] -> [Set Verb: GET] -> [Bind Event: OnRequestCompleted] -> [Apply URL]
 |
 [Custom Event: WFS_Response_Success]
 |
 [Get Response Object]
 |
 [Get Array Field: "features"]
 |
 [Get Array Element: 0] -> [As Object]
 |
 [Get Object Field: "properties"]
 |
 [Get String Field: "字段名"]
 |
 [UI: Set Text]
4. 消除 (Elimination) 关键细节

数组长度检查：在 Get Array Element 之前，先连接一个 Length 节点并配合 Branch 判断是否大于 0。如果长度为 0，说明你点击的位置没有地块，应在 UI 上显示“未选中任何目标”，从而消除 (Elimination) 访问空数组导致的逻辑报错。

字段名大小写：GeoJSON 规范中 "features" 和 "properties" 通常是严格小写的，请务必检查字段名拼写。

消除 (Elimination) 异步冲突：由于请求是异步的，请确保在 WFS_Response_Success 逻辑中使用的 UI 控件变量是有效的（Is Valid），防止在请求返回前 UI 已被关闭。

通过这套 VaRest 连线逻辑，你可以高效地完成从地理坐标发送到属性信息展示的完整闭环，消除 (Elimination) 了手动解析原始字符串的繁琐过程。

---

## 44. Varest插件的Construct JSON Request节点中没有 Apply URL引脚

**问题：** Varest插件的Construct JSON Request节点中没有 Apply URL引脚

**答案：** 这是因为 VaRest 的设计模式是对象导向的。Construct JSON Request 只是在内存中“制造”了一个请求工具，它本身不包含执行动作的引脚。

要找到 Apply URL，你必须从请求对象的输出端拉出连线。请按照以下精确步骤操作，以消除 (Elimination) 节点不可见的问题：

1. 正确的搜索方式 (Step-by-Step)

放置 Construct JSON Request 节点。

找到该节点右侧的蓝绿色输出引脚，名为 Return Value。

关键动作：按住左键从 Return Value 引脚拉出一条引线到空白处。

在弹出的搜索框中输入 Apply URL 或 Process URL（不同版本可能叫法略有不同，但通常为 Apply URL）。

消除 (Elimination) 干扰：如果依然搜不到，请取消勾选搜索框右上角的“上下文敏感 (Context Sensitive)”。

2. 完整的连线顺序

VaRest 的标准执行流如下，请严格遵守此顺序以消除 (Elimination) 逻辑执行错误：

Step 1: 构造 -> Construct JSON Request

Step 2: 配置 -> 从 Return Value 拉出 Set Verb (填入 GET)。

Step 3: 绑定 -> 从 Return Value 拉出 Bind Event to On Request Completed。

Step 4: 执行 -> 最后从 Return Value 拉出 Apply URL，并将你格式化好的 URL 字符串连入。

3. 为什么必须要这样连？

在 VaRest 中，Apply URL 需要知道它是为“哪一个”请求对象执行操作。如果你直接在右键菜单里搜索，编辑器不知道你想把这个函数应用给谁，所以有时会将其隐藏。通过从引脚拉线，你告诉了编辑器：“我要给这个新创建的 Json Request 申请一个 URL”，此时节点才会准确出现。

4. 连线配方 (Graph Recipe)

[Construct JSON Request] 
 (Return Value) --------------------------+----------+----------+
 | | |
 [Set Verb] [Bind Event] [Apply URL]
 (GET) (输入 URL)
5. 消除 (Elimination) 常见误区

节点别名：在某些极其罕见的版本中，该节点可能被重命名为 Execute Request，但 99% 的情况下它叫 Apply URL。

执行顺序：务必先连接 Bind Event（绑定），再连接 Apply URL（执行）。如果你先执行再绑定，可能会出现响应已经回来了但逻辑还没准备好接收的情况，导致 UI 无法显示，为了消除 (Elimination) 这种时序冲突，请遵循“先绑定、后申请”的原则。

通过从 Return Value 引脚拉线，你就能顺利找到并连接 Apply URL 节点。

---

## 45. Get Array Field的数组引脚拉出没有 Get Array Element选项

**问题：** Get Array Field的数组引脚拉出没有 Get Array Element选项

**答案：** 在虚幻引擎的蓝图中，VaRest 的 Get Array Field 输出的是一个名为 Json Value 的对象数组（Array of VaRest Json Value）。由于它是一个标准的蓝图数组，获取单个元素的节点名称在不同版本或设置下会有所变化。

请按照以下步骤操作，以消除 (Elimination) 节点查找障碍：

1. 搜索“Get”而非“Get Array Element”

虚幻引擎现在通常将该节点统称为 Get。

从 Get Array Field 的 数组（方块图标）引脚拉出线。

在搜索框中直接输入：Get。

在弹出的列表中，你会看到一个子类别叫 Array，下面有一个节点叫 Get (a copy)。

这就是你要找的节点。它会根据索引（Index 0）提取数组中的第一个 JSON 值。

2. 消除 (Elimination) 上下文干扰

如果输入 Get 没出现，请尝试以下操作：

拉出引线后，取消勾选搜索框右上角的 Context Sensitive (上下文敏感)。

搜索 Get 或 Array Element。

注意：如果通过这种方式添加，记得手动将 Get Array Field 的输出数组连接到该节点的 Array 输入端。

3. 核心后续逻辑：转换为对象

由于 Get (a copy) 输出的是一个 Json Value 类型，它是不能直接读取属性的。你必须将其转换回 Json Object。

从 Get (a copy) 的输出引脚拉出线。

搜索并添加 As Object 节点。

消除 (Elimination) 理解误区：只有通过 As Object 转换后，你才能使用 Get Object Field ("properties")。

4. 连线配方 (Graph Recipe)

请检查你的连线是否符合以下链条：

[Get Array Field (名称: "features")]
 |
[Get (a copy) (Index: 0)] <-- 这就是你要找的节点
 |
[As Object] <-- 必须有这一步，否则无法提取属性
 |
[Get Object Field (名称: "properties")]
 |
[Get String Field (你的字段名)]
5. 常见故障点消除 (Elimination)

数组为空：在执行 Get (a copy) 之前，建议拉出线条搜索 Length，并配合 Branch 判断长度是否大于 0。如果直接对空数组执行 Get，虽然不会崩溃，但会导致后续逻辑全部失效。

节点名称变体：在某些 UE5 版本中，如果你的编辑器语言是中文，它可能显示为 获取 (副本)。

通过搜索 Get (a copy) 并紧跟 As Object 节点，你就能顺利消除 (Elimination) 数据层级解析中断的问题，并成功获取到地块的属性信息。

---

## 46. 我使用该网址可在geoserver中成功查询到点击处的用地类型和面积：http://192.168.31.58:8080…

**问题：** 我使用该网址可在geoserver中成功查询到点击处的用地类型和面积：http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=INTERSECTS(the_geom,POINT(413070.94751%204963107.41790))&srsName=EPSG:4539。使用以下网址将X、Y替换为与以上网址相同的xy坐标，Geoserver无法查询到：http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=INTERSECTS(the_geom,POINT({X} {Y}))&srsName=EPSG:4539。是否需要在初始化url使重新修改url赋值

**答案：** 是的，你完全正确。GeoServer 的 WFS 请求无法查询，是因为 URL 中的空格字符没有经过正确的编码。在原始链接中，POINT 坐标之间的空格必须被转换为 %20 才能在网络传输中被正确识别。

为了消除 (Elimination) 无法查询的问题，请按照以下步骤调整你的蓝图逻辑：

1. 修改 URL 模板（添加 URL 编码）

在你的 Format Text 节点中，将模板字符串修改为以下形式，手动将空格替换为 %20：

http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=INTERSECTS(the_geom,POINT({X}%20{Y}))&srsName=EPSG:4539

注意：POINT({X}%20{Y}) 这里的 %20 就是标准的 URL 空格转义字符。

2. 动态重新赋值 (Re-assignment)

针对你提到的“是否需要重新赋值”：是的。
因为坐标（X 和 Y）是动态变化的，你不能只在游戏开始（BeginPlay）时设置一次 URL。

正确逻辑流程：

触发事件：例如鼠标点击地面。

获取坐标：通过地理参考系统计算出当前的 X 和 Y。

重新生成：将新的 X/Y 传入 Format Text 节点。

重新赋值：将 Format Text 的输出通过 SET 节点更新给你的 URL 变量。

发送请求：在 SET 之后连接 Apply URL。这样可以确保每次发送的请求都包含最新的点击位置，消除 (Elimination) 查询结果停留在上一个位置的错误。

3. 蓝图连线建议 (Graph Recipe)

[鼠标点击事件]
 |
[计算 X, Y (Float)]
 |
[Format Text (模板包含 %20)] --> [To String]
 | |
[SET MyDynamicURL (变量)] <----------+
 |
[Get VaRestSubsystem] -> [Construct JSON Request] -> [Apply URL (连入 MyDynamicURL)]
4. 消除 (Elimination) 常见故障

变量类型检查：确保传入 Format Text 的 X 和 Y 是 Float 类型。如果你将它们转为字符串时带有过多的小数位，可能会导致 URL 过长，建议使用 ToText (Float) 节点并设置最大小数位（如 5 位）。

打印调试：在执行 Apply URL 之前，连接一个 Print String 打印最终生成的 URL。你可以将其复制到浏览器中测试，如果浏览器能返回 JSON 而蓝图不能，说明是 VaRest 内部解析的问题；如果浏览器也查不到，说明 URL 编码仍有误。

通过在 POINT({X}%20{Y}) 中使用 %20 并在每次点击时重新为 URL 变量赋值，你就能消除 (Elimination) GeoServer 查询失败的问题。

---

## 47. 检查以下url设置是否正确：http://192.168.31.58:8080/geoserver/wfs?servic…

**问题：** 检查以下url设置是否正确：http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=INTERSECTS(the_geom,POINT({413070.94751}%20{4963107.41790}))&srsName=EPSG:4539，输入网址后显示以下报错：This XML file does not appear to have any style information associated with it. The document tree is shown below.

 Could not parse CQL filter list. Lexical error at line 1, column 27. Encountered: '{' (123), Parsing : INTERSECTS(the_geom,POINT({413070.94751} {4963107.41790})).

**答案：** 这个 URL 设置是错误的。报错信息中的 Lexical error 和 Encountered: '{' 已经明确指出：GeoServer 无法识别花括号 { }。

在虚幻引擎中，花括号 {X} 只是 Format Text 节点的“占位符”语法，它们不应该出现在最终发送给服务器的 URL 字符串中。

以下是修复方案，以消除 (Elimination) 词法解析错误：

1. 为什么会报错？

语法冲突：GeoServer 的 CQL 过滤器要求坐标直接写为数字，例如 POINT(413070.94 4963107.41)。

错误的占位符：你在 URL 变量中手动输入了数字并给它加上了 { }。服务器把 { 当成了非法字符，导致解析崩溃。

2. 正确的 URL 变量模板

请将你的变量或 Format Text 节点中的字符串修改为以下内容（删除数字外的花括号）：

模板字符串：

http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=INTERSECTS(the_geom,POINT({X}%20{Y}))&srsName=EPSG:4539
3. 在蓝图中正确赋值

不要在 URL 字符串里直接写死 {413070...}。你应该这样做：

Format Text 节点：在输入框输入上面的模板字符串。此时节点会自动生成两个引脚：X 和 Y。

传入数值：将你的 X 坐标变量连入 X 引脚，Y 坐标变量连入 Y 引脚。

消除 (Elimination) 花括号：Format Text 节点在运行阶段会自动把 {X} 替换为具体的数字（如 413070.94），并自动删除花括号。最终输出的字符串将是干净的 POINT(413070.94%204963107.41)。

4. 关键检查：坐标顺序与坐标系

坐标系检测：EPSG:4539 是高斯-克吕格投影。在 WFS 1.0.0 中，坐标顺序通常是 经度(X) 纬度(Y) 或 东坐标 北坐标。请确保你的变量连接顺序与 GeoServer 数据库中的定义一致。

消除 (Elimination) 精度问题：如果坐标包含太多位小数，GeoServer 有时会解析缓慢。建议在传入 Format Text 之前，将 Float 截断到小数点后 2-4 位。

5. 调试建议

如果你在浏览器中手动测试，请直接输入以下去掉花括号的网址：
http://192.168.31.58:8080/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=UE_JiJiHu:landuse&outputFormat=application/json&cql_filter=INTERSECTS(the_geom,POINT(413070.94751%204963107.41790))&srsName=EPSG:4539

结论：只要你通过 Format Text 节点动态生成字符串，并确保最终输出的文本中没有花括号，这个 XML 报错就会立即被消除 (Elimination)。

---

