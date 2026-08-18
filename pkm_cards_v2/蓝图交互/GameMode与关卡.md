## 96. 关卡生成的自动文件可以保存吗

**问题：** 关卡生成的自动文件可以保存吗

**答案：** 在虚幻引擎中，关于“自动文件”的保存需要分两种情况来讨论：一种是编辑器生成的自动备份文件（Autosaves），另一种是你在运行时（Runtime）生成的动态内容。

为了消除 (Elimination) 误解，请根据你的具体需求查看以下说明：

1. 恢复与保存编辑器的自动备份 (Autosaves)

如果你是指编辑器在崩溃或未保存时生成的 .uasset 备份：

文件位置：它们存储在项目文件夹的 Saved/Autosaves 目录下。

如何保存为正式文件：

通常在重新打开项目时，虚幻会弹出“载入内容（Restore Content）”窗口。

如果没有弹出，你可以手动进入该文件夹，将最新的备份文件复制到 Content 目录下的对应位置，并重命名消除 (Elimination) 掉后缀中的时间戳信息，替换损坏的原始文件。

2. 保存运行时生成（Spawn）的 Character 或内容

你在漫游过程中通过 SpawnActor 生成的 Character，在关闭游戏或停止 PIE（按下 Esc）后会自动消除 (Elimination)，不会自动保存到关卡中。

如果你希望将运行时的修改永久保存，有以下几种方法：

方法 A：在编辑器中使用“保持模拟修改”（Keep Simulation Changes）

如果你在 Simulate（模拟） 模式下生成了 Actor 或者是手动修改了属性：

选中场景中那个生成的 Actor。

按下键盘上的 K 键。

停止运行后，该 Actor 的状态会被保留在编辑器关卡中。

方法 B：将动态生成的模型保存为资产 (Bake to Static Mesh)

如果你是通过几何体脚本（Geometry Script）或过程化生成的模型：

操作：在建模模式（Modeling Mode）中，可以使用 Convert 工具。

保存：将生成的动态网格体（Dynamic Mesh）转换为 Static Mesh Asset。

这一步能将临时数据消除 (Elimination)，并转化为可以放入 Fab 资产库或永久引用的资源。

方法 C：使用 SaveGame 系统（针对玩家数据）

如果你希望下次运行游戏时，Character 还在上次的位置：

逻辑：你必须编写 SaveGame 蓝图逻辑。

步骤：在退出漫游前，将 Character 的 Transform（坐标、旋转）保存到 SaveGame 对象中。下次 BeginPlay 时，读取数据并重新执行 SpawnActor。

3. 自动生成文件的目录结构建议

为了确保你的自动生成内容不丢失，建议检查项目设置：

Project Settings -> Loading & Saving：

确保勾选了 Auto-save。

设置 Frequency（频率）以消除 (Elimination) 因突然崩溃导致的长时间工作丢失。

总结

如果你想保存崩溃备份：去 Saved/Autosaves 找回并替换。

如果你想保存生成的角色：使用 SaveGame 系统记录坐标。

如果你想保存生成的模型：使用 Modeling Mode 的 Convert 按钮将其“烘焙”为静态网格体资产。

通过明确这些文件的性质，你可以有效地管理并永久保留你生成的内容，消除 (Elimination) 丢失进度的风险。

---

## 101. 迁移项目后场景中的模型出现闪烁，如何解决

**问题：** 迁移项目后场景中的模型出现闪烁，如何解决

**答案：** 在迁移 Unreal Engine 项目后，模型出现闪烁（Flickering）通常是由于渲染设置不匹配、虚假阴影缓存或物理边界计算错误导致的。

你可以通过以下步骤排查并消除 (Elimination) 闪烁问题：

1. 调整阴影系统（虚拟阴影贴图 VSM）

UE5 默认使用虚拟阴影贴图（Virtual Shadow Maps），如果迁移后的模型精度较低或设置不当，会产生明显的锯齿状闪烁。

控制台命令：按下 ~ 键输入 r.Shadow.Virtual.NormalBias 0.5（或更高，如 1.0）。这可以消除 (Elimination) 因阴影偏移不足产生的“阴影粉刺”闪烁。

切换方案：如果闪烁严重，尝试在 Project Settings -> Rendering 中将 Shadow Map Method 从 Virtual Shadow Maps 切换回 Shadow Maps。

2. 解决 Z-Fighting（深度冲突）

如果闪烁表现为两个面交替出现，说明两个模型完全重叠了。

检查重叠：迁移过程中是否意外生成了重复的层或重复加载了关卡。

微调位移：将其中一个闪烁的模型在轴向上移动 0.1 单位，手动消除 (Elimination) 物理重合。

3. 开启/优化 Nanite

如果模型是 Nanite 且在远处闪烁，可能是由于代理网格体（Proxy Mesh）生成的错误。

重新构建数据：在菜单栏选择 Build -> Build All Landscapes 或 Build Nanite。

抗锯齿设置：在项目设置中，确保 Anti-Aliasing Method 设为 TSR (Temporal Super Resolution)。TSR 能有效稳定高频几何体的闪烁。

指令优化：使用 r.TSR.ShadingRejection.Flickering 1 来开启专用的闪烁抑制算法。

4. 修正 Actor 包围盒（Bounds Scale）

如果模型在特定视角下消失又出现（看起来像闪烁），通常是视锥体剔除（Occlusion Culling）计算错误。

现象：当你转动视角时，模型边缘发生闪烁。

修复：选中闪烁的模型，在 Details 面板搜索 Bounds Scale。将其从 1.0 增加到 1.5 或 2.0。

这会扩大模型的渲染判定范围，消除 (Elimination) 因物体中心点在屏幕外被误跳过渲染的问题。

5. 全局光照与反射 (Lumen)

如果闪烁表现为光斑或黑色噪点，这是 Lumen 的时间性累积问题。

后处理控制：在场景中放置 Post Process Volume（并设为 Infinite Bound）。

参数调整：在 Lumen Scene 设置中，提高 Final Gather Quality。

消除 (Elimination) 噪点：使用控制台命令 r.Lumen.Reflections.Temporal 1 来增强反射的稳定性。

6. 地形专用修复（如果是 LandscapeProxy 闪烁）

Nanite Skirts：如果你开启了 Nanite 地形，确保在地形属性中勾选了 Nanite Skirts。这能防止地形块接缝处因 LOD 切换产生的闪烁。

重建地形：在迁移后，务必执行一次 Landscape Build。

总结检查清单

控制台：尝试 r.Shadow.Virtual.NormalBias 1。

设置：确认抗锯齿为 TSR。

属性：将闪烁物体的 Bounds Scale 调大。

构建：执行 Build All。

通过这些调整，你可以恢复迁移后丢失的渲染稳定性，并彻底消除 (Elimination) 视觉上的闪烁干扰。

---

## 102. 执行 Build All具体是哪一项操作

**问题：** 执行 Build All具体是哪一项操作

**答案：** 在 Unreal Engine 5 中，执行 Build All 是一个自动化流程，它会按顺序运行场景中所有必要的预计算操作。

要执行此操作，请在编辑器顶部菜单栏中找到：

Build（构建）菜单 -> Build All Levels（构建所有关卡）

该操作具体包含以下关键子项：

Build Lighting（构建光照）：

如果你使用的是非 Lumen 的静态光照（Static Lighting），它会运行 Lightmass 来计算光照贴图。

即使使用 Lumen，它也会更新反射捕获（Reflection Captures）和天光贡献，消除 (Elimination) 迁移后可能出现的光照残留。

Build Geometry（构建几何体）：

重新计算场景中的 BSP 画笔和静态网格体的基础数据，确保物理碰撞与视觉模型同步。

Build Navigation（构建导航）：

如果场景中有 Nav Mesh Bounds Volume，它会重新扫描地面，更新 AI 的行走路径，这对你即将实现的自动路径漫游至关重要。

Build Nanite（构建 Nanite）：

重新验证场景中所有 Nanite 资产的流送数据，消除 (Elimination) 因资产迁移导致的 Nanite 网格体显示异常。

Build Landscapes（构建地形）：

针对你使用的 LandscapeProxy，它会重新生成地形的 LOD、草地映射和物理碰撞 Mip 层级。

操作建议与技巧

进度观察：点击后，右下角会弹出进度条。在构建过程中，电脑可能会由于高 CPU 占用而变得缓慢，这是正常现象。

针对性构建：如果你只想解决地形相关的闪烁或碰撞问题，可以只选择 Build -> Build Landscapes。

消除 (Elimination) 警告信息：构建完成后，通常会弹出一个 Message Log（消息日志） 窗口。请务必查看其中的警告（Warning），例如“Actor 具有重复的索引”，这些报错往往是导致闪烁的根本原因。

总结

直接点击 Build -> Build All Levels 是最稳妥的做法，它能一键消除 (Elimination) 迁移后由于各种缓存数据（光照、导航、地形、物理）不一致导致的渲染和逻辑 Bug。

---

## 103. Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例…

**问题：** Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件总光照贴图的非常大，并已自动降低。可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件总光照贴图的非常大，并已自动降低。可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件总光照贴图的非常大，并已自动降低。可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件总光照贴图的非常大，并已自动降低。可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件总光照贴图的非常大，并已自动降低。可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件总光照贴图的非常大，并已自动降低。可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
Landscape 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
InstancedFoliageActor_UAID_7C10C93F944841A602_1813466531 此实例化静态网格体组件的总光照贴图较大，可以考虑降低组件的光照贴图分辨率、或减少此组件中的网格体实例数量
未找到重要体积，且场景太大，自动合成的体积无法产生良好的效果。请添加一个紧密包裹的lightmass重要体积来优化场景质量及光照构建时间。
 === Lightmass crashed: ===
Assertion failed: (Index >= 0) & (Index < ArrayNum) [File:D:\build\++UE5\Sync\Engine\Source\Runtime\Core\Public\Containers\Array.h] [Line: 752] 
Array index out of bounds: 16800 from an array of size 16800
0x00007ff7eaaf9af3 UnrealLightmass.exe!Lightmass::FStaticMeshLOD::GetIndex() []
0x00007ff7eaafaf9d UnrealLightmass.exe!Lightmass::FStaticMeshStaticLightingMesh::GetTriangleIndices() []
0x00007ff7eaa6b3c9 UnrealLightmass.exe!Lightmass::FEmbreeGeometry::FEmbreeGeometry() []
0x00007ff7eaa7516a UnrealLightmass.exe!Lightmass::FEmbreeAggregateMesh::AddMesh() []
0x00007ff7eaaca8f0 UnrealLightmass.exe!Lightmass::FStaticLightingSystem::FStaticLightingSystem() []
0x00007ff7eaa7bd71 UnrealLightmass.exe!Lightmass::BuildStaticLighting() []
0x00007ff7eaaa10eb UnrealLightmass.exe!Lightmass::LightmassMain() []
0x00007ff7eaac3410 UnrealLightmass.exe!main() []
0x00007ff7eab316cc UnrealLightmass.exe!__scrt_common_main_seh() []
0x00007ffe5639e957 KERNEL32.DLL!UnknownFunction []
0x00007ffe5756427c ntdll.dll!UnknownFunction []

0x00007ff7eaaf9af3 UnrealLightmass.exe!Lightmass::FStaticMeshLOD::GetIndex() []
0x00007ff7eaafaf9d UnrealLightmass.exe!Lightmass::FStaticMeshStaticLightingMesh::GetTriangleIndices() []
0x00007ff7eaa6b3c9 UnrealLightmass.exe!Lightmass::FEmbreeGeometry::FEmbreeGeometry() []
0x00007ff7eaa7516a UnrealLightmass.exe!Lightmass::FEmbreeAggregateMesh::AddMesh() []
0x00007ff7eaaca8f0 UnrealLightmass.exe!Lightmass::FStaticLightingSystem::FStaticLightingSystem() []
0x00007ff7eaa7bd71 UnrealLightmass.exe!Lightmass::BuildStaticLighting() []
0x00007ff7eaaa10eb UnrealLightmass.exe!Lightmass::LightmassMain() []
0x00007ff7eaac3410 UnrealLightmass.exe!main() []
0x00007ff7eab316cc UnrealLightmass.exe!__scrt_common_main_seh() []
0x00007ffe5639e957 KERNEL32.DLL!UnknownFunction []
0x00007ffe5756427c ntdll.dll!UnknownFunction []

**答案：** 从你提供的日志来看，光照构建失败是由两个主要原因导致的：配置不当引发的内存/效率警告，以及特定模型引起的底层程序崩溃 (Lightmass Crash)。

由于程序已经崩溃（Assertion failed: Array index out of bounds），你需要按以下步骤操作来修复环境并消除 (Elimination) 报错：

1. 修复致命崩溃：清理缓存与查找错误模型

日志中的 Array index out of bounds 通常意味着某个模型的索引数据损坏，或者其光照贴图设置超出了 Lightmass 的处理限制。

清理 Swarm 缓存：

在 Windows 任务栏右下角找到 Swarm Agent 图标（黄色圆圈）。

打开窗口，点击菜单栏的 Cache -> Clean，然后点击 Cache -> Validate。

定位错误模型：

错误发生在 FStaticMeshLOD::GetIndex。这通常说明某个静态网格体（Static Mesh）或其 LOD 有问题。

检查最近添加或迁移的模型，尤其是那些有数万个实例的植物（Foliage）。尝试暂时隐藏一部分模型再次构建，通过排除法消除 (Elimination) 出有问题的具体资产。

2. 核心设置：添加 Lightmass 重要体积 (必做)

日志提示：“未找到重要体积…场景太大”。没有这个体积，Lightmass 会尝试计算整个关卡无穷远处的每一个像素，导致内存溢出。

操作：在左侧“放置 Actor”面板搜索 Lightmass Importance Volume。

设置：将其拖入场景，并缩放至仅覆盖玩家能够到达和看清的漫游区域。

效果：这会告诉引擎只在这个范围内计算高质量光照，极大地提高构建速度并消除 (Elimination) 崩溃风险。

3. 优化地形与植被的光照贴图分辨率

日志中大量的“总光照贴图较大”警告说明你的 Landscape 和 Foliage（植被）光照分辨率设置得太高了，超出了显存承载。

针对 Landscape：

选中地形（LandscapeProxy）。

在细节面板搜索 Static Lighting Resolution。

如果该值很大（如 10.0 或更高），请尝试降低它（例如改为 1.0 或 2.0）。数值越小，分辨率越低。

针对 Foliage（植被）：

打开 Foliage Mode（快捷键 Shift+3）。

选中你的所有植被类型。

在细节面板找到 Light Map Resolution，将其改为很小的值（如 8 或 16）。对于草木类，不需要高精度的光照贴图。

4. 彻底消除崩溃的替代方案：切换至 Lumen

如果你使用的是 UE5，且硬件支持（显卡支持光追或较新），最简单且能彻底消除 (Elimination) 这些复杂报错的方法是弃用烘焙光照，改用全动态光照：

打开 Project Settings -> Rendering。

将 Global Illumination 设为 Lumen。

将 Reflections 设为 Lumen。

将场景中所有灯光的 Mobility 设置为 Moveable（可移动）。

这样做你就不再需要运行 “Build Lighting”，从而绕过所有 Lightmass 崩溃问题。

5. 总结操作清单

添加 Lightmass Importance Volume 覆盖漫游区。

降低 地形（Landscape）的 Static Lighting Resolution。

降低 植被（Foliage）的 Light Map Resolution。

清理并验证 Swarm Agent 缓存。

如果依旧崩溃，考虑将场景灯光全部设为 Moveable 并使用 Lumen 动态渲染。

执行这些操作后，再次运行 Build All Levels，这些红色的错误和闪烁问题将会得到有效的消除 (Elimination)。

---

## 104. 这种情况需要从原项目重新迁移场景模型过来吗

**问题：** 这种情况需要从原项目重新迁移场景模型过来吗

**答案：** 在当前情况下，不建议立刻重新迁移，因为你面临的大多数警告（如 spruce_01 缺少碰撞、大型 Actor 阴影设置）属于资产配置问题，即使重新迁移，由于原项目的设置可能相同，这些问题依然会存在。

建议你先尝试“局部修复 + 批量编辑”。只有当出现“大面积模型丢失”或“资产完全损坏”时，才考虑重新迁移。

以下是具体的判断标准和修复策略，帮助你消除 (Elimination) 疑惑：

1. 为什么不需要立即重迁？

碰撞问题（spruce_01）：这是因为资源本身没有生成碰撞。你只需要在内容浏览器中打开该资产，添加一次碰撞，场景中所有的 600 多个实例都会自动修复。

阴影警告：这是 UE5 对渲染性能的提醒。即使重迁，由于模型体积大，UE 依然会报这个警。你需要手动在 Details 面板中关闭它们的 Cast Dynamic Shadow。

空元素问题：这是模型原始数据的问题，重迁通常无法解决，除非你在三维软件（如 3ds Max/Maya）中修复后再导入。

2. 必须重新迁移的信号（红灯）

如果出现以下情况，请重新执行迁移：

0 索引/0 三角形报错过多：如果你发现大部分模型都没有画面（一片虚无），说明迁移过程中 .uasset 文件引用关系断裂。

材质全部丢失：如果场景全是灰白格子，且无法通过简单的重新链接修复。

3. 高效修复方案：属性矩阵（Property Matrix）

针对那 651 个警告，你不需要一个一个改。利用虚幻引擎的属性矩阵工具可以快速消除 (Elimination) 警告：

在 World Outliner（世界大纲） 中，搜索 spruce_01 或报错的大型 Actor。

全选这些 Actor，右键 -> Asset Actions（资产操作） -> Bulk Edit via Property Matrix（通过属性矩阵批量编辑）。

在弹出的窗口右侧，找到 Cast Dynamic Shadow，一键取消勾选。

找到 Collision Presets，统一修改。

4. 正确的重迁方法（如果决定重迁）

如果你尝试修复后发现模型依然闪烁或报错，请按照以下标准流程重迁，以消除 (Elimination) 引用丢失：

在原项目中：选中整个关卡文件或模型文件夹。

右键 -> Asset Actions -> Migrate。

目标位置：务必选择新项目的 Content 文件夹（不要选子文件夹），这样能确保内部路径引用（如 /Game/Meshes/...）保持一致。

5. 修复 spruce_01 的具体动作

这是解决你“射线检测失败”最快的方法：

在内容浏览器搜索 spruce_01。

双击打开 -> 菜单栏 Collision -> Add 10DOP Simplified Collision。

保存。此时场景中所有关于此模型的碰撞警告都会立即消除 (Elimination)。

结论

先花 10 分钟在资产编辑器中修复 spruce_01 的碰撞，并使用属性矩阵关闭大型物体的动态阴影。如果这样做之后 Build All 依然崩溃或模型依然闪烁，再考虑使用 Migrate 工具进行完整重迁。这样可以节省大量不必要的资源导入时间。

---

## 105. Add 10DOP Simplified Collision应该选择XYZ中的哪个选项

**问题：** Add 10DOP Simplified Collision应该选择XYZ中的哪个选项

**答案：** 对于你的 spruce_01（云杉/树木）资产，建议选择 Add 10DOP-Z Simplified Collision。

以下是选择依据以及如何通过此设置消除 (Elimination) 问题的详细说明：

1. 为什么选择 10DOP-Z？

10DOP 代表“10面离散定向多胞形”（10-Discrete Oriented Polytope）。它是通过在盒子的 4 条边上切出倒角来逼近物体形状的。

后缀字母（X, Y, Z）的意思：它代表哪一个轴向保持“垂直/不被切角”。

针对树木 (Z-Axis)：树木通常是垂直生长的。选择 10DOP-Z 会使碰撞盒在顶部和侧面的边缘进行切角，但在垂直方向（Z轴）保持完整。

效果：这能生成一个比方块（Box）更圆润、更贴合树干和树冠轮廓的碰撞体，同时比 26DOP 更节省性能。

2. 具体的执行步骤

在静态网格体编辑器中点击 Collision -> Add 10DOP-Z Simplified Collision。

你会看到一个带有切角的绿色线框包裹住树木。

微调（可选）：如果觉得切角太严重，可以使用缩放工具（R键）在视口中调整这个绿色的碰撞框。

保存：点击保存后，场景中所有引用该模型的警告将立即消除 (Elimination)。

3. 选择错误会发生什么？

如果你选择 10DOP-X 或 10DOP-Y：碰撞盒的侧面会被切得很斜，导致角色走到树下时，明明还没碰到树干，就会被斜向的碰撞边界推开，甚至产生“滑坡”现象。

选择 10DOP-Z 能确保地面与树干交界处的碰撞是垂直且稳定的，这对玩家行走和射线检测最友好。

4. 解决“射线检测失败”的关联

当你为 spruce_01 添加了 10DOP-Z 碰撞后：

射线检测 (Line Trace)：现在能正确击中这些树木。

自动漫游：如果你的 Character 在漫游路径上遇到这些树，CharacterMovement 能够正确感知障碍物，而不会发生穿模或逻辑报错。

消除 (Elimination) 警告：地图检测（Map Check）中的“无简单或复杂碰撞”警告将彻底消失。

5. 补充建议

如果你追求极致的性能（例如场景中有成千上万棵树）：

对于远景的树，可以使用 Box Simplified Collision。

对于玩家近距离接触的树，10DOP-Z 是平衡性能与精确度的最佳方案。

通过这一设置，你可以快速修复资产缺陷，并消除 (Elimination) 由于碰撞数据缺失导致的漫游功能失效。

---

## 166. 在UI中设计按钮，使得点击时游戏切换到AirSim的游戏模式，具体的蓝图连线逻辑是什么

**问题：** 在UI中设计按钮，使得点击时游戏切换到AirSim的游戏模式，具体的蓝图连线逻辑是什么

**答案：** 在虚幻引擎中，动态切换 GameMode 实际上是通过重新加载关卡（Open Level）并携带特定的 options 字符串来实现的。因为 GameMode 是在关卡初始化时决定的，无法在不重启关卡的情况下直接更换。

以下是实现“点击按钮切换到 AirSimGameMode”的具体流程：

1. 准备工作

首先，你需要确定 AirSimGameMode 蓝图类的具体路径。

通常路径为：/AirSim/Blueprints/BP_AirSimGameMode.BP_AirSimGameMode_C

注意：后缀 _C 是蓝图类在作为 URL 参数时的标准格式。

2. UI 按钮蓝图逻辑

在你的 Widget Blueprint（控件蓝图）中，为切换按钮添加以下逻辑：

添加变量：创建一个 Name 类型的变量，命名为 TargetLevelName，默认值设为你当前关卡的名字（例如 L_StartMap）。

构建 Option 字符串：

使用 Append (String) 节点。

A 引脚 输入：?game=

B 引脚 输入：/AirSim/Blueprints/BP_AirSimGameMode.BP_AirSimGameMode_C

调用 Open Level：

搜索并放置 Open Level (by Name) 节点。

Level Name：连接你的 TargetLevelName 变量。

Options：连接刚才构建好的 Append 字符串。

3. 蓝图节点配方 (Graph Recipe)

[Button_Switch] -> [Event On Clicked]
 |
 V
[Get Current Level Name] (或者直接手动输入关卡名)
 |
 V
[Open Level (by Name)]
 |--- Level Name: "YourMapName"
 |--- Options: "?game=/AirSim/Blueprints/BP_AirSimGameMode.BP_AirSimGameMode_C"
4. 关键点：数据持久化

由于切换 GameMode 会导致关卡重启，所有内存中的临时变量会被消除 (Elimination)。如果你需要保留切换前的某些状态，请务必：

使用 GameInstance 存储数据：GameInstance 的生命周期贯穿整个游戏进程，不会因为切换关卡而消失。

使用 SaveGame：如果是需要跨 session 保存的数据。

5. 进阶：如何返回原有的 GameMode

如果你想通过按钮切回普通的第三人称或第一人称模式，只需更改 Options 字符串中的路径：

例如切回基础模式：?game=/Script/Engine.GameModeBase

或者切回你自定义的 BP：?game=/Game/Blueprints/MyCustomGameMode.MyCustomGameMode_C

6. 验证与调试

消除 (Elimination) 路径错误：如果点击后关卡加载了但没有出现 AirSim 的无人机，通常是路径写错了。你可以在内容浏览器中右键点击 BP_AirSimGameMode，选择 Copy Reference（复制引用），然后将路径粘贴到 Append 节点中，手动在末尾加上 _C。

查看日志：如果切换失败，按下 ~ 键打开控制台，查看是否有“Failed to load GameMode”的警告。

通过这种方法，你可以优雅地在同一个三维场景中，通过 UI 点击动作消除 (Elimination) 手动修改项目设置的繁琐步骤，实现仿真模式的即时启动。

---

## 167. 可以使用UI按钮切换至创建的AirSim的UI吗

**问题：** 可以使用UI按钮切换至创建的AirSim的UI吗

**答案：** 是的，你可以通过 UI 按钮点击事件来动态创建并切换到 AirSim 的 UI（即 BP_AirSimHUD 控件）。这是一种非常灵活的做法，可以让你在自己的主菜单和 AirSim 仿真界面之间自由切换，同时消除 (Elimination) 了对特定 GameMode 的强依赖。

以下是实现这一功能的详细步骤和蓝图逻辑：

1. 资产与前提条件

主 UI (Main UI)：你当前正在使用的 UI 界面，其中包含一个“进入仿真”按钮。

AirSim UI 资产：通常名为 BP_AirSimHUD（位于插件的 Content/Blueprints 目录下）。

场景准备：确保你的关卡中已经手动放置了 SimModeWorldMultiRotor（无人机模式）或 SimModeWorldBase Actor，否则 UI 加载后将无法获取飞行数据。

2. 蓝图构建步骤（在你的主 UI 内部）

你需要为按钮的 OnClicked 事件编写逻辑。为了保证操作流畅，我们需要处理 UI 的创建、显示以及鼠标状态的消除 (Elimination)。

步骤逻辑：

创建 AirSim 控件：如果尚未创建，则实例化它。

存为变量：将返回的引用保存，避免重复创建造成内存浪费。

添加到视口：将其显示在屏幕上。

隐藏当前 UI：隐藏或移除当前的主 UI。

设置输入模式：将输入焦点从单纯的 UI 切换到游戏，以便你可以操作无人机。

3. 图表配方 (Graph Recipe)

在你的 Widget Blueprint（主菜单）中：

[变量列表]
- AirSimRef (类型: BP_AirSimHUD_C, 对象引用)

[事件图表]
[Button_StartSim] -> [Event On Clicked]
 |
[Is Valid?] (检查 AirSimRef)
 |--- [Not Valid]: [Create Widget] (Class: BP_AirSimHUD) -> [Set AirSimRef]
 |--- [Is Valid]: (直接连入下一步)
 |
[AirSimRef] -> [Add to Viewport] (ZOrder 设置高一点，如 10)
 |
[Remove from Parent] (移除当前主 UI 按钮所在的界面)
 |
[Get Player Controller]
 |
[Set Input Mode Game And UI] (这样既能操作无人机，又能点击 AirSim 上的按钮)
 |
[Set Show Mouse Cursor] (设置为 False，或者根据需要保留)
4. 如何“切回”主 UI (消除仿真界面)

如果你想在 AirSim 界面中增加一个“返回”按钮，或者按 ESC 键退出仿真 UI：

在 BP_AirSimHUD 内部（或者在你的 Level Blueprint 中捕获按键）：

调用 AirSimRef -> Remove from Parent。

Create Widget (你的主 UI) -> Add to Viewport。

Set Input Mode UI Only 并 Set Show Mouse Cursor (True)。

5. 性能与最佳实践

引用管理：不要每次点击按钮都 Create Widget，这会产生多个 UI 实例重叠。使用 Is Valid 节点检查变量，可以消除 (Elimination) 重复创建导致的性能下降和视觉错误。

Z-Order 控制：AirSim 的 UI 包含很多调试信息，建议将其 ZOrder 设置得比普通 UI 高，确保它不会被背景装饰遮挡。

输入模式切换：

如果你想在显示 AirSim UI 时依然能用键盘控制无人机，请务必使用 Set Input Mode Game and UI。

如果你发现无法控制无人机，请点击一下屏幕，确保焦点从 UI 按钮转移到了游戏视口。

6. 验证测试

在 PIE 模式下运行。

点击你设计的按钮。

验证：AirSim 的状态栏（如位置、速度信息）是否出现在屏幕上，且原有的 UI 按钮是否已消除 (Elimination)。

尝试使用键盘 WASD 键，观察无人机是否能正常响应。

通过这种方式，你可以把 AirSim 当作你游戏中的一个“模块”或“小游戏”来调用，而无需重启关卡或强制修改 GameMode。

---

## 168. 如果我想在设计的UI中加入一个按键功能，点击可先将游戏模式切换为None，再切换为AirSimGameMode，具体的蓝…

**问题：** 如果我想在设计的UI中加入一个按键功能，点击可先将游戏模式切换为None，再切换为AirSimGameMode，具体的蓝图连线逻辑应该是怎样的

**答案：** 在虚幻引擎中，GameMode（游戏模式） 是受保护的核心对象，它无法在游戏运行时（Runtime）实时无缝切换。如果你尝试在蓝图中直接“设置”GameMode，你会发现没有这样的节点，因为 GameMode 的更改必须伴随关卡的重新加载或重置。

为了实现你描述的“刷新”效果（即通过 UI 按钮先设为 None 再设为 AirSim），最可靠且标准的方法是使用 Open Level 节点并配合 Options 参数。

以下是实现这一功能的逻辑和步骤：

1. 核心概念

None 状态：在加载关卡时不传递任何参数，引擎将使用项目设置中的默认模式。

AirSim 状态：在加载关卡时通过 URL 参数 ?game=... 强制指定 AirSimGameMode。

刷新机制：通过重新加载当前地图来消除 (Elimination) 内存中错误的 GameMode 状态。

2. 蓝图连线逻辑 (UI Widget)

假设你的按钮叫 Btn_SwitchToAirSim。

步骤逻辑：

获取当前关卡名称：使用 Get Current Level Name。

构建 Options 字符串：我们需要告诉引擎使用哪一个 GameMode 类。

调用 Open Level：执行关卡切换。

连线配方 (Graph Recipe)：

[Button OnClicked (Btn_SwitchToAirSim)]
 |
[Get Current Level Name] --------------------┐
 | |
[Open Level (by Name)] <---------------------┘ (连接到 Level Name 输入端)
 |
[Options (输入项)] : ?game=/Script/AirSim.AirSimGameMode

注意参数路径：?game= 后面的路径必须是 AirSimGameMode 的完整类路径。通常是 /Script/AirSim.AirSimGameMode（如果是 C++ 原始类）或者指向你创建的蓝图路径（例如 /Game/Blueprints/MyAirSimBP.MyAirSimBP_C）。

3. 如果你需要“先 None 再 AirSim”的连线逻辑

由于必须重启关卡，你无法在一个按钮事件里完成“切换两次”的视觉动作（因为第一次切换就会关闭当前 UI 并重启进程）。

如果你是为了消除 (Elimination) 之前的崩溃隐患，通常直接加载一次正确的 AirSimGameMode 就足够了。如果你一定要模拟这个过程，可以使用 GameInstance（在关卡间持久存在）来做一个简单的状态机：

UI 点击 -> 设置 GameInstance 里的变量 TargetMode = 1 -> Open Level (不带参数，即 None)。

Level Blueprint (BeginPlay) -> 检查 GameInstance 里的 TargetMode 是否等于 1。

如果是 -> 设置 TargetMode = 0 (防止无限循环) -> Open Level (带上 ?game=AirSim 参数)。

4. 更好的替代方案：动态创建 AirSim 逻辑

如果你不希望重新加载关卡（因为这会造成黑屏），另一种思路是不通过 GameMode 切换，而是直接在 UI 按钮点击时：

Spawn Actor from Class：手动生成 BP_SimModeWorldMultiRotor。

Add to Viewport：手动创建并显示 BP_AirSimHUD。

这种方式可以消除 (Elimination) 重启关卡的开销，但需要你手动处理无人机的生成位置和玩家控制权（Possess）的移交。

5. 测试与注意事项

URL 语法：? 是参数分隔符，game= 是固定键名。格式必须极其精确，否则会退回到默认模式。

鼠标焦点：在 Open Level 后，UI 会被销毁。记得在关卡重启后，通过 BeginPlay 重新设置输入模式（Input Mode）。

消除 (Elimination) 残留：使用 Open Level 是最彻底的清理方式，它能保证所有物理状态和 AirSim 的 API 接口都是从零开始初始化，从而避免你之前遇到的 setupClockSpeed 崩溃。

---

## 169. 动态创建 AirSim 逻辑具体的蓝图连线应该是什么

**问题：** 动态创建 AirSim 逻辑具体的蓝图连线应该是什么

**答案：** 动态创建 AirSim 逻辑可以在不重启关卡的情况下启动仿真，这非常适合在现有的游戏工程中灵活开启/关闭 AirSim 功能。

这种方式的逻辑核心是：手动生成 AirSim 的“仿真中心”，然后让玩家控制器（PlayerController）接管生成的无人机。

核心步骤与资产准备

需要生成的类： BP_SimModeWorldMultiRotor (这是 AirSim 的核心仿真逻辑)。

需要创建的 UI： AirSimHUD (提供飞行数据显示)。

无人机引用： 运行时生成的 AirSimPawn。

蓝图实现方案 (UI 按钮点击事件)

1. 生成仿真模式 (SimMode)

首先要生成 SimMode Actor，它会读取 settings.json 并负责在 PlayerStart 处生成无人机。

Graph Recipe:

Event: OnClicked (Button_StartAirSim)

Node 1: SpawnActor From Class

Class: 选择 BP_SimModeWorldMultiRotor (或 SimModeWorldMultiRotor)

Spawn Transform: 使用 Get Player Camera Manager -> Get Camera Transform (或者预设一个固定的位置)

Collision Handling: Always Spawn, Ignore Collisions

2. 等待无人机生成并获取引用

因为 AirSim 内部是异步生成无人机的，我们需要一个微小的延迟来确保无人机已出现在场景中。

Graph Recipe:

Node 2: Delay (时长：0.2s)

Node 3: Get All Actors of Class

Component Class: 选择 AirSimPawn (或者你的无人机基类)

Node 4: Get (a copy) (索引为 0)

Target: 将此输出连接到变量或直接下一步。

3. 移交控制权 (Possess)

通过 Possess 节点，让玩家能够操作这台无人机。

Graph Recipe:

Node 5: Get Player Controller

Node 6: Possess

Target: 连接 Player Controller

In Pawn: 连接刚才获取到的 AirSimPawn 引用。

4. 初始化 AirSim 飞行界面 (HUD)

由于不是通过 GameMode 启动，我们需要手动添加飞行 UI。

Graph Recipe:

Node 7: Create Widget

Widget Class: 选择 BP_AirSimHUD (或插件内对应的 HUD 类)

Node 8: Add to Viewport

Node 9: Remove from Parent (目标：当前的设置菜单 UI，以便消除 (Elimination) 遮挡)

完整逻辑连线图描述

[UI 按钮点击]
 |
[SpawnActor BP_SimModeWorldMultiRotor] --(Transform 设为 0,0,0 即可)
 |
 [Delay 0.2s] (给插件时间去解析 JSON 并生成无人机)
 |
[Get All Actors of Class (AirSimPawn)]
 |
 [Get Index 0] ---------------------------┐
 | |
[Get Player Controller] |
 | |
 [Possess] <------------------------------┘ (由控制权接管无人机)
 |
[Create Widget (BP_AirSimHUD)]
 |
[Add to Viewport]
 |
[Remove from Parent (Self)] (关闭当前的切换菜单)

性能与最佳实践

消除 (Elimination) 重复生成：在 SpawnActor 之前，先使用 Get Actor Of Class 检查是否已经存在 SimModeWorldMultiRotor。如果已存在，直接执行 Possess 即可，避免多次生成导致物理时钟冲突。

物理子步 (Substepping)：即便动态生成，仍需确保在 Project Settings 中开启了物理子步，否则无人机飞行会抖动。

相机切换：Possess 之后，虚幻会自动将视口切到无人机的相机。如果视角不对，请检查无人机蓝图内的相机组件是否设置为 Auto Activate。

消除 (Elimination) 崩溃风险：这种动态方式最大的好处是，如果 settings.json 有误，只有这一个按钮点击会报错，而不会像 GameMode 强制启动那样导致整个引擎在加载关卡时闪退。

---

## 170. Spawn Transform这一步中怎么使用预设的固定位置

**问题：** Spawn Transform这一步中怎么使用预设的固定位置

**答案：** 在虚幻引擎蓝图中，为 SpawnActor 节点提供预设固定位置主要有三种专业做法。你可以根据该位置是“硬编码”还是“场景内可见”来选择。

方案一：使用“Make Transform”节点（手动输入坐标）

如果你已经知道确切的 X, Y, Z 坐标，这是最直接的方法。

在蓝图图表中右键搜索并添加 Make Transform 节点。

在 Location（位置）输入框中手动输入坐标（例如：X=500.0, Y=200.0, Z=100.0）。

如果需要调整朝向，在 Rotation 中输入角度（例如：Yaw=90.0 使其转向）。

将 Make Transform 的返回值连接到 SpawnActor 的 Spawn Transform 输入引脚上。

方案二：使用“Target Point”作为场景参考（最推荐）

这种方式最为灵活，你可以在编辑器视口中直接拖动该点来调整位置，而不需要修改代码。

在场景中放置参考点：在虚幻编辑器左上角的“快速添加到项目”菜单中，搜索 Target Point（目标点），将其拖入场景中你想要无人机出现的位置。

在蓝图中引用它：

在关卡蓝图中，选中该 Target Point 后右键即可创建引用。

如果是 UI 蓝图，请使用 Get Actor Of Class 节点，并将类设置为 Target Point。

获取位置：从 Target Point 引用中拉出引线，搜索 Get Actor Transform。

连接：将获取到的 Transform 连接到 SpawnActor 节点。

提示：使用 Target Point 可以消除 (Elimination) 反复运行游戏并猜测坐标数值的繁琐过程。

方案三：创建 Transform 变量

如果你想在 UI 蓝图的“细节”面板中随时修改这个位置，可以使用变量。

在蓝图左侧的 Variables（变量）列表中点击“+”，创建一个新变量。

将变量类型更改为 Transform。

编译（Compile）蓝图，然后在该变量的 Default Value（默认值）中输入你预设的坐标。

将该变量拖入图表，选择 Get，并连接到 SpawnActor。

蓝图连线示例 (Graph Recipe)

[方案二：场景参考点逻辑]

[Get Actor Of Class (Target Point)] 
 |
[Get Actor Transform] --------------------┐
 |
 (Spawn Transform)
 ↓
[Button Clicked] -> [SpawnActor BP_SimModeWorldMultiRotor]
开发建议：

防止碰撞闪退：在 SpawnActor 节点上，务必将 Collision Handling Override 设置为 Always Spawn, Ignore Collisions。这能确保即使预设位置稍微穿进了地板或墙壁，模拟器也能成功启动并消除 (Elimination) 因生成失败导致的后续空指针崩溃。

高度注意：预设位置的 Z 轴 应该设置得稍高一点（例如比地面高 100-200 单位），以防止无人机在生成瞬间因与地面物理判定重叠而发生“弹射”或爆炸。

---

## 171. 切换无人机BP_SimModeWorldMultiRotor和BP_AirSimHUD后，场景中看不到无人机模型，无人机…

**问题：** 切换无人机BP_SimModeWorldMultiRotor和BP_AirSimHUD后，场景中看不到无人机模型，无人机UI加载出来后页面显示空白且无法点击

**答案：** 这种情况通常是因为 动态生成流程（Spawn Sequence） 与 AirSim 内部初始化逻辑 之间存在时间差或配置冲突。AirSim 的无人机并不是在 SpawnActor 的那一刻瞬间产生的，而是由 SimMode 读取 settings.json 后异步创建的。

以下是修复这三个问题的具体方案，旨在消除 (Elimination) 初始化不完全导致的失效：

1. 解决“看不到无人机模型”：配置与延时

如果模型没出现，通常是 SimMode 还没有完成 settings.json 的解析，或者生成的坐标在相机视野之外。

检查 Settings.json：确保 AutoCreate 设置为 true。

增加延时：在 SpawnActor BP_SimModeWorldMultiRotor 之后，必须给它足够的物理帧来生成无人机。

蓝图修正：[SpawnActor BP_SimModeWorldMultiRotor]
 |
[Delay 0.5s] <-- 必须增加此延时，消除生成时差
 |
[Get All Actors of Class (BP_FlyingPawn)]
 |
[Possess]

2. 解决“HUD 页面显示空白”：数据关联

AirSim 的 HUD 需要连接到运行中的 ApiProvider 才能获取速度、高度等数据。如果先加载 HUD 以后加载无人机，数据绑定会失败。

初始化顺序：确保先 Possess 无人机，再 Create Widget。

手动刷新 API：如果依然空白，在 Create Widget 后调用 HUD 内部的刷新函数（如果有），或者确保 SimMode 已经成功启动。

调试检查：按下键盘上的 F1。如果 AirSim 的内置帮助界面能出来，说明插件在运行；如果连 F1 都没反应，说明 SimMode 根本没运行起来。

3. 解决“UI 无法点击”：输入模式锁定

这是最常见的问题。虚幻引擎在 Possess 无人机后，通常会把输入模式切回“仅游戏”，导致鼠标点击失效。

解决方案：在添加 HUD 后，显式设置输入模式。

蓝图连线 (Graph Recipe)：[Add to Viewport (BP_AirSimHUD)]
 |
[Get Player Controller] 
 |
[Set Input Mode Game and UI] <-- 允许控制无人机的同时点击 UI
 |
[Set Show Mouse Cursor (True)] <-- 消除鼠标消失的问题

4. 深度排查：检查大世界坐标（Origin）

如果你在旧工程中开启了 Large World Coordinates (LWC)，且场景中心点距离太远，无人机可能会因为坐标偏移过大而在生成瞬时被引擎裁切（Culling）。

检查 Outliner：点击运行后，查看编辑器右侧的 World Outliner。

* 如果有 BP_FlyingPawn 实例但看不见：检查它的 Location 是否是极大的数值。

* 如果没有 BP_FlyingPawn：说明 SimMode 初始化失败。请查看 Output Log，搜索 AirSim 关键字，确认是否有 “settings.json not found” 或 “Vehicle creation failed” 的报错。

总结操作流：

生成 SimMode。

等待 0.5 秒（关键：消除 (Elimination) 异步生成的竞争风险）。

获取并 Possess 无人机。

创建并添加 HUD。

设置 Input Mode Game and UI 并 Show Mouse Cursor。

按照这个顺序操作，可以解决模型不可见、数据不更新以及鼠标无法点击的问题。

---

## 172. LoginId:15f35a5c45ec48c9befffe7e1cce8220 EpicAccountId:bb540…

**问题：** LoginId:15f35a5c45ec48c9befffe7e1cce8220
EpicAccountId:bb540f2f125e45eca3e91bb353460102

Unhandled Exception: 0xe06d7363

KERNELBASE
VCRUNTIME140
msvcp140
UnrealEditor_AirSim!USimHUDWidget::onToggleRecordingButtonClick() [C:\AirSimProject\Plugins\AirSim\Source\SimHUD\SimHUDWidget.cpp:25]
UnrealEditor_CoreUObject
UnrealEditor_CoreUObject
UnrealEditor_CoreUObject
UnrealEditor_CoreUObject
UnrealEditor_CoreUObject
UnrealEditor_CoreUObject
UnrealEditor_UMG
UnrealEditor_UMG
UnrealEditor_UMG
UnrealEditor_SlateCore
UnrealEditor_Slate
UnrealEditor_Slate
UnrealEditor_Slate
UnrealEditor_Slate
UnrealEditor_ApplicationCore
UnrealEditor_ApplicationCore
UnrealEditor_ApplicationCore
UnrealEditor_ApplicationCore
user32
user32
InkObj
atlthunk
user32
user32
UnrealEditor_ApplicationCore
UnrealEditor
UnrealEditor
UnrealEditor
UnrealEditor
UnrealEditor
UnrealEditor
kernel32
ntdll

**答案：** 分析你提供的崩溃报告，问题锁定在 USimHUDWidget::onToggleRecordingButtonClick() 函数（SimHUDWidget.cpp 第 25 行）。

崩溃根本原因

当你点击 HUD 上的录制按钮时，C++ 代码会尝试调用 AirSim 的录制服务。由于你采用了手动动态生成的流程，在点击按钮的瞬间，以下两个条件之一可能尚未满足，导致了空指针（Null Pointer）崩溃：

SimMode 尚未完全就绪：getSimMode() 返回了空值。

ApiProvider 尚未绑定无人机：录制逻辑找不到可以采集数据的无人机对象。

这属于典型的异步初始化竞态条件。为了消除 (Elimination) 此崩溃，我们需要对插件源码进行加固。

解决方案 1：修改 C++ 源码（彻底修复）

你需要为 AirSim 插件添加防御性代码。

修改文件: Plugins/AirSim/Source/SimHUD/SimHUDWidget.cpp
定位函数: onToggleRecordingButtonClick

请将该函数修改为如下形式，增加 if 判空保护：

void USimHUDWidget::onToggleRecordingButtonClick()
{
 // 获取 SimMode 实例
 auto sim_mode = getSimMode();
 
 // 关键修正：增加判空检查，消除空指针引用导致的 0xe06d7363 错误
 if (sim_mode && sim_mode->getApiProvider() && sim_mode->getApiProvider()->getVehicleSimApi()) 
 {
 // 只有当仿真模式和车辆 API 都存在时，才允许切换录制状态
 sim_mode->getApiProvider()->getVehicleSimApi()->toggleRecording();
 }
 else 
 {
 // 如果没准备好，打印警告而不是直接闪退
 UE_LOG(LogTemp, Warning, TEXT("AirSim: Recording failed. SimMode or Vehicle API not ready yet."));
 }
}
修改完成后，请务必关闭编辑器，删除 Binaries 文件夹并重新编译项目。

方案 2：配置 settings.json（环境修复）

AirSim 的录制功能需要一个有效的保存路径。如果 settings.json 中配置缺失，某些版本的 AirSim 在尝试访问文件系统时也会抛出异常。

请确保你的 Documents/AirSim/settings.json 中包含录制配置块：

{
 "SettingsVersion": 1.2,
 "SimMode": "Multirotor",
 "Recording": {
 "RecordInterval": 0.05,
 "RecordOnMove": false,
 "Cameras": [
 { "CameraName": "0", "ImageType": 0, "PixelsAsFloat": false, "Compress": true }
 ]
 },
 "Vehicles": {
 "Drone1": {
 "VehicleType": "SimpleFlight",
 "AutoCreate": true
 }
 }
}

方案 3：蓝图逻辑逻辑优化（UI 修复）

为了防止用户在无人机还没生成出来时就点击“录制”，你应该在蓝图中控制按钮的可点击状态：

初始状态：将 UI 中的录制按钮设置为 Disabled（不可用）。

开启逻辑：在你的生成流程中，执行完 Possess 之后，再增加一个 Delay 1.0s。

激活按钮：获取 HUD 引用，将录制按钮的状态设为 Enabled。

为什么之前的工程不崩溃？

在新工程或默认模式下，GameMode 会在关卡加载的第一时间同步初始化所有对象。而你的手动 UI 切换模式打乱了这个顺序，导致 UI 先于物理对象出现。

通过以上 C++ 判空保护和配置更新，你可以有效消除 (Elimination) 这个因初始化顺序不匹配导致的致命闪退。

---

## 173. SpawnActor From Class 中的Transform:如何设为 0, 0, 0

**问题：** SpawnActor From Class 中的Transform:如何设为 0, 0, 0

**答案：** 在虚幻引擎蓝图中，将 SpawnActor 的 Transform 设为 0, 0, 0（即世界坐标原点，无旋转，缩放为 1）有两种最快捷的方法：

方法一：直接在节点上“分割”引脚（最快）

这是最常用的技巧，可以直接在 SpawnActor 节点上输入数值，无需添加额外节点。

在 SpawnActor 节点上，找到 Spawn Transform 输入引脚（橙色）。

右键点击该引脚，选择 分割结构体引脚 (Split Struct Pin)。

这时它会展开为 Location、Rotation 和 Scale。

再次右键点击展开后的 Location（向量引脚），选择 分割结构体引脚 (Split Struct Pin)。

这时它会展开为 Location X、Location Y 和 Location Z。

此时，你会看到所有数值默认都已经是 0.0。保持它们不变，即可实现在 0, 0, 0 位置生成。

方法二：使用“Make Transform”节点（最清晰）

如果你希望逻辑在图表中清晰可见，可以使用专用节点。

在图表空白处右键搜索并添加 Make Transform 节点。

该节点默认的 Location 是 (0,0,0)，Rotation 是 (0,0,0)，Scale 是 (1,1,1)。

将 Make Transform 的返回值引脚直接连接到 SpawnActor 的 Spawn Transform 输入端。

为什么设为 0,0,0 是安全的？

消除 (Elimination) 位置依赖：对于 SimModeWorldMultiRotor 和 SimHUD 这类“逻辑型 Actor”（非实体模型），它们在世界中的物理位置通常并不重要，因为它们主要负责后台计算和界面显示。

自动定位：AirSim 的无人机生成位置是由 settings.json 和场景中的 PlayerStart 决定的，而不是由 SimMode Actor 本身的位置决定的。

注意事项：

虽然坐标设为 0, 0, 0，但请确保在 SpawnActor 节点上：

Collision Handling Override 设置为 Always Spawn, Ignore Collisions。

这样即使原点坐标处有地板或其他物体，也能消除 (Elimination) 因碰撞判定导致 Actor 生成失败的风险。

---

## 174. World Settings中的重载场景重力应如何设置

**问题：** World Settings中的重载场景重力应如何设置

**答案：** 在虚幻引擎中设置场景重力是确保物理模拟稳定性的关键。对于 AirSim 这种高精度仿真插件，错误的重力设置可能导致无人机飞行抖动或系统崩溃。

以下是设置重载场景重力的详细步骤：

1. 访问 World Settings 面板

在虚幻编辑器顶部菜单栏点击 Window（窗口）。

选择 World Settings（世界设置）。

该面板默认通常出现在编辑器右侧（与 Details 面板相邻）。

2. 配置重力参数

在 World Settings 面板中找到 Physics（物理） 分类：

Override World Gravity（重载世界重力）：勾选此复选框。这允许该关卡忽略项目全局设置，使用独立的重力数值。

Global Gravity Z（全局重力 Z）：

标准地球重力：输入 -980.0。

注意单位：虚幻引擎使用厘米（cm）为单位，因此 \(-9.8 \, m/s^2\) 对应的是 \(-980 \, cm/s^2\)。

消除 (Elimination) 风险：请勿将其设为 0 或正数。如果设为 0，AirSim 的飞行 PID 控制器将失去反馈目标，导致无人机在生成瞬间因数值溢出而崩溃或“弹射”出地图。

3. 与 AirSim 的协同设置

AirSim 插件内部也有自己的重力计算逻辑。为了确保两者一致，建议：

保持默认方向：确保重力方向始终指向 Z 轴负方向。

消除 (Elimination) 抖动：如果你发现无人机在地面试图起飞时剧烈抖动，请检查 Project Settings（项目设置） -> Physics -> Max Physics Delta Time。将其设置为 0.016667 (60fps) 或更小的值，以配合 -980 的重力加速度。

4. 为什么这对你的崩溃问题很重要？

你之前提到的 setupClockSpeed 崩溃，部分原因是 AirSim 在初始化时会读取关卡的物理环境（包括重力设置）。如果 WorldSettings 中的重力参数处于非法状态或正在被其他逻辑频繁修改，会导致时钟同步失败。

通过手动勾选 Override World Gravity 并显式填入 -980.0，你为 AirSim 提供了一个确定的物理基准，从而消除 (Elimination) 了因物理环境不确定导致的初始化异常。

5. 测试验证

修改完成后，点击 Save（保存） 关卡。

运行程序，观察 Output Log（输出日志）。

如果重力设置成功，AirSim 在启动时不会弹出关于 Gravity initialization failed 的警告。

---

## 175. 搜索不到Finish Spawning Actor节点

**问题：** 搜索不到Finish Spawning Actor节点

**答案：** 在虚幻引擎蓝图中，Finish Spawning Actor 是一个上下文相关（Context Sensitive）的节点。如果你直接在空白处搜索它，它是不会出现的。

要调出这个节点，请遵循以下精确步骤：

1. 开启“延迟生成”模式

普通的 SpawnActor from Class 节点不会提供这个接口。你需要让节点进入“延迟加载”状态。

找到你的 SpawnActor From Class 节点。

右键点击该节点，选择 “切换为延迟生成” (Convert to Spawn Actor Deferred)。

注意：如果菜单中没有这个选项，通常是因为你没有在该 Actor 蓝图中设置任何“生成时公开”(Expose on Spawn) 的变量。但没关系，请看步骤 2。

2. 通过引线调出节点（最通用的方法）

这是最稳妥的办法，可以消除 (Elimination) 搜索不到节点的困扰：

从 SpawnActor 节点的 Return Value（蓝色引脚）拉出一条引线。

在松开鼠标弹出的搜索框中，输入 Finish Spawning。

此时 Finish Spawning Actor 节点就会出现在列表中。

选中它，节点会自动出现在图表中，并已经与你的 Actor 引用相连。

3. 完整的蓝图生成逻辑配方 (Graph Recipe)

为了消除 (Elimination) 之前提到的崩溃，你的连线必须看起来像这样：

节点 1: Begin Spawning Actor from Class (或者已经转换为延迟模式的 SpawnActor)

Class: BP_SimModeWorldMultiRotor

节点 2: Delay (时长设为 0.2s)

节点 3: Finish Spawning Actor

Target: 连接到节点 1 的 Return Value。

Spawn Transform: 依然设为 0, 0, 0。

节点 4: Delay (时长设为 0.5s)

后续: 执行 Possess 和 Create HUD 逻辑。

为什么在普通 Spawn 节点后找不到它？

在虚幻引擎的逻辑中：

普通 SpawnActor: 会在执行到该节点的一瞬间完成所有 C++ 初始化（包括 BeginPlay）。因此不需要“Finish”步骤。

延迟 SpawnActor: 它会先创建 Actor 实例但暂停初始化。这给了你一个时间窗口去设置变量或等待环境加载，最后必须调用 Finish Spawning Actor 来手动触发 BeginPlay。

专家提示：使用延迟生成并配合 Delay 节点，是解决 AirSim 动态生成时物理引擎崩溃的最佳手段。这能确保在 BeginPlay 里的 C++ 代码执行前，所有内存分配都已完成，从而有效消除 (Elimination) 空指针异常。

---

## 176. 告诉我使用 Open Level 节点并配合 Options 参数实现GameMode（游戏模式）切换具体的蓝图连线逻辑

**问题：** 告诉我使用 Open Level 节点并配合 Options 参数实现GameMode（游戏模式）切换具体的蓝图连线逻辑

**答案：** 在虚幻引擎中，通过 Open Level (by Name) 节点的 Options 参数切换 GameMode 是一种非常高效的方法，尤其适用于需要在不同关卡间动态指定规则，或是在同一地图上实现不同玩法（如：探索模式与消除模式的切换）。

核心原理

Options 字符串本质上是附加在 URL 后面的命令行参数。要指定 GameMode，需要使用关键字 ?Game=。

对于 C++ 类：使用路径并以 _C 结尾（虽然它是 C++ 类，但引擎路径引用通常如此）。

对于蓝图类：必须使用完整引用的路径，并以 _C 结尾。

1. 资产与准备清单

目标地图名称：例如 MainCity。

目标 GameMode 蓝图：例如 BP_BattleGameMode。

获取路径：在内容浏览器中右键点击该 GameMode 蓝图，选择 “复制引用” (Copy Reference)。

示例引用：Blueprint'/Game/Modes/BP_BattleGameMode.BP_BattleGameMode'

2. 蓝图连线步骤 (Graph Recipe)

为了消除 (Elimination) 手打路径导致的拼写错误，推荐使用 Format Text 或 Append 节点。

逻辑流程：

节点 1: Format Text (格式化文本)

Format: ?Game={Path}_C

Path (输入): 将刚才复制的引用粘贴进来，但要去掉两边的单引号和前缀。

最终格式应类似：?Game=/Game/Modes/BP_BattleGameMode.BP_BattleGameMode_C

节点 2: Open Level (by Name)

Level Name: 输入关卡名（如 MainCity）。

Options: 将 Format Text 的输出连接到此处。

连线图示（文字版）：

[ 自定义事件/按钮点击 ]
 |
[ Format Text ] ---------------------> [ Open Level (by Name) ]
 - Format: "?Game={path}_C" - Level Name: "MyMapName"
 - path: "/Game/Blueprints/BP_MyGM" - Options: (连接来自 Format Text)

3. 如何指定特定的 AirSim GameMode

如果你是为了配合 AirSim 使用，路径通常如下（假设插件安装在项目内）：

Options 内容：
?Game=/AirSim/Blueprints/BP_AirSimGameMode.BP_AirSimGameMode_C

4. 进阶技巧：动态选择 GameMode

如果你有多个游戏模式，可以利用 Select 节点来动态构建字符串：

创建一个 Enum (枚举)，列出所有模式（如：Race, FreeFlight, Elimination）。

使用 Select 节点，根据枚举值输出对应的完整路径字符串。

通过 Append 节点加上前缀 ?Game=。

将结果插入 Open Level。

5. 测试与注意事项

消除 (Elimination) 常见错误：确保路径末尾有 _C。如果没有这个后缀，引擎可能无法正确识别并加载该蓝图类作为游戏模式，从而退回到默认模式。

验证方法：进入新关卡后，按下键盘上的 ~ 键打开控制台，输入 stat game。在输出信息中可以查看到当前生效的 GameMode 名称。

打包注意：如果通过 Options 动态加载 GameMode，确保该蓝图被引用或包含在打包设置中，否则在构建版本中可能会因为资源未被包含而导致加载失败。

通过这种方式，你可以灵活地在同一张地图上实现多种游戏逻辑的切换，且无需为每种模式制作单独的地图副本。

---

## 177. 告诉我Format Text (格式化文本)以获得GameMode这一步的详细蓝图连线逻辑

**问题：** 告诉我Format Text (格式化文本)以获得GameMode这一步的详细蓝图连线逻辑

**答案：** 在虚幻引擎中，使用 Format Text 节点构建 Options 参数是最安全且最直观的方法。这种方法能够消除 (Elimination) 手动拼接字符串时遗漏问号或后缀的低级错误。

以下是实现这一功能的详细步骤和蓝图连线逻辑：

1. 准备 GameMode 的引用路径

在内容浏览器中找到你的 GameMode 蓝图（或 C++ 类）。

右键点击它，选择 复制引用 (Copy Reference)。

复制出来的字符串示例： Blueprint'/Game/Core/BP_CombatGameMode.BP_CombatGameMode'

2. 构建蓝图逻辑 (Graph Recipe)

第一步：放置并设置 Format Text 节点

在蓝图图表中右键搜索并添加 Format Text 节点。

在节点的 Format 文本框内直接输入以下内容（包含括号）：
?Game={GM_Path}_C

当你按下回车后，节点会自动生成一个名为 GM_Path 的输入引脚。

第二步：处理并填入路径

创建一个 String 类型变量，或者直接在 GM_Path 引脚处拉出连线创建一个 Make Literal String 节点。

将第一步复制的路径粘贴进去，并进行修剪：

原始： Blueprint'/Game/Core/BP_CombatGameMode.BP_CombatGameMode'

修剪后： /Game/Core/BP_CombatGameMode.BP_CombatGameMode

注意：去掉开头的 Blueprint' 和末尾的 '。

第三步：连接至 Open Level

添加 Open Level (by Name) 节点。

将 Format Text 节点的 Result (返回结果) 输出引脚连接到 Open Level 的 Options 输入引脚。

引擎会自动在 Text 和 String 之间添加一个转换节点。

3. 详细连线逻辑图示

[节点：Format Text]
 Format: "?Game={GM_Path}_C"
 引脚 [GM_Path] (String/Text) <--- 输入修剪后的完整资产路径 (例如: /Game/Modes/MyGM.MyGM)
 引脚 [Result] (Text) --------|
 |
 V
[节点：Open Level (by Name)] |
 引脚 [Level Name] <---------- 输入你的地图名称 (例如: Desert_Map)
 引脚 [Options] <------------- (自动转换) 连接来自 Format Text 的 Result

4. 关键点拨：为什么要加 _C？

在虚幻引擎的 URL 选项系统中，所有蓝图类的资产路径都必须添加 _C 后缀。如果不加此后缀，引擎会尝试将其作为普通的 C++ 类加载，从而导致加载失败并回退到项目默认的 GameMode。

5. 常见问题排除 (Elimination)

路径中包含空格：如果你的资产路径中有空格，这种方法可能会失效。请确保你的文件夹和蓝图命名遵循 PascalCase 或下划线命名法。

大小写敏感：虽然虚幻引擎在很多地方不区分大小写，但在 Options 字符串中，建议严格遵循资产原始的大小写格式。

连线类型不匹配：Open Level 的 Options 引脚需要 String 类型，而 Format Text 输出的是 Text 类型。连线时虚幻会自动创建 To String 转换节点，这是正常的。

通过这个逻辑，你可以通过改变输入到 GM_Path 的字符串，在同一个关卡启动时自由切换不同的玩法模式。

---

## 178. 点击切换游戏模式按钮后出现如下警告：Error at startup:[json.exception.parse_err…

**问题：** 点击切换游戏模式按钮后出现如下警告：Error at startup:[json.exception.parse_error.101]parse error at line 6,column 34:syntax error while parsing object key-invalid literal;last read:"ScalableClock",/';excepted string literal

**答案：** 这个错误是由 AirSim 的底层 JSON 解析器抛出的。它表明你的 Documents/AirSim/settings.json 配置文件中存在语法错误。

之所以在你“切换游戏模式”后才出现，是因为 AirSim 插件在新的 GameMode 加载并执行 BeginPlay 时，会尝试重新读取并解析该配置文件。

1. 错误诊断 (Elimination)

错误信息：parse error ... "ScalableClock", /'; excepted string literal
这意味着在 JSON 文件的第 6 行附近，解析器在读取到 "ScalableClock" 之后，遇到了一个非法字符 /。

产生原因：

非法的注释：JSON 标准格式不支持使用 // 或 /* */ 进行注释。你可能尝试在 ScalableClock 后面加注释。

拼写错误：在逗号后面多打了一个斜杠。

2. 修复方法

请执行以下步骤来消除 (Elimination) 该错误：

打开文件夹：C:\Users\<你的用户名>\Documents\AirSim\。

使用记事本或 VS Code 打开 settings.json。

找到关于 ClockType 或 ScalableClock 的行。

删除所有斜杠 / 及其后面的文字。

正确的 JSON 示例：

请确保你的配置文件结构类似下面这样（注意逗号的使用）：

{
 "SeeDocsAt": "https://github.com/Microsoft/AirSim/blob/main/docs/settings.md",
 "SettingsVersion": 1.2,
 "SimMode": "Multirotor",
 "ClockType": "ScalableClock",
 "OriginGeopoint": {
 "Latitude": 47.641468,
 "Longitude": -122.140165,
 "Altitude": 122
 }
}
3. 常见排查点

检查末尾逗号：JSON 中最后一项设置的末尾不能有逗号。

错误："ClockType": "ScalableClock", }

正确："ClockType": "ScalableClock" }

严禁使用注释：

错误："ClockType": "ScalableClock", // 使用缩放时钟 （这会直接触发你遇到的 101 错误）。

引号匹配：确保所有的键（Key）和字符串值（Value）都包裹在双引号 " 中。

4. 为什么切换模式会触发它？

当你使用 Open Level 切换到 AirSimGameMode 时，AirSim 会启动其初始化序列。由于你之前修改了 C++ 代码中的 setupClockSpeed（加入了对 getSettings() 的调用），插件必须解析 settings.json 来获取 ClockType 的值。

如果 JSON 格式损坏，解析器会抛出 std::exception，在虚幻引擎中表现为 Error at startup 弹窗或直接崩溃。

建议：修复 JSON 文件后，直接重启项目即可，无需重新编译 C++ 代码。

---

## 192. 为什么点击运行关卡后，部分在关卡中放置的树木、建筑等没有加载到关卡场景中，如何解决

**问题：** 为什么点击运行关卡后，部分在关卡中放置的树木、建筑等没有加载到关卡场景中，如何解决

**答案：** 如果在编辑器（Editor）中能看到树木和建筑，但点击“运行（Play）”后它们消失了，这通常是因为虚幻引擎 5 的 World Partition（世界分区） 系统或 Streaming（流送） 逻辑没有正确加载这些区域。

请按以下步骤操作，以消除 (Elimination) 资产丢失的问题：

1. 检查 World Partition 的加载状态

虚幻引擎 5 使用世界分区来优化大地图。如果你在编辑器里手动“Load（加载）”了某个区域，但这部分区域没有被标记为运行时加载，运行后就会消失。

解决方法：在编辑器顶部菜单打开 Window > World Partition > World Partition Editor。

在弹出的网格窗口中，选中你建筑所在的区域，右键选择 Load Selected Cells。

关键设置：选中场景中消失的 Actor（如树木或建筑），在 Details（细节） 面板中搜索 Grid Placement。

如果该资产必须始终存在，将 Grid Placement 改为 Always Loaded。

如果是远景，确保它的 Loading Range（加载范围） 足够大。

2. 检查数据层 (Data Layers)

你可能无意中将这些资产分配到了一个默认被禁用的 Data Layer 中。

打开 Window > World Partition > Data Layer Outliner。

检查是否有任何层级的 Initial State 被设为了 Unloaded。

如果某些层在运行时没有被逻辑激活，其中的建筑和树木就会被消除 (Elimination) 掉，不显示在关卡中。

3. 检查 Actor 的隐藏设置

检查这些 Actor 的基础属性，确保它们没有被设置为“仅编辑器可见”：

选中消失的 Actor，在 Details 面板中搜索 Hidden in Game。确保该勾选框是取消状态。

搜索 Is Editor Only。确保它是取消状态（如果是 True，它只会在编辑器显示，运行后会彻底消失）。

4. HLOD (分层细节级别) 未构建

如果你开启了 HLOD，且距离摄像机较远，引擎会尝试显示 HLOD 简化模型。如果 HLOD 还没构建，远处就会空无一物。

临时测试：在控制台输入 wp.Runtime.HLOD 0 来关闭 HLOD。如果建筑出现了，说明你需要重新构建 HLOD。

构建方法：菜单栏 Build > Build HLODs。

5. 碰撞与生成位置冲突 (Spawn Collision)

如果你的建筑是通过蓝图动态生成的，或者树木是 Foliage（植被），检查是否有碰撞重叠导致生成失败：

在生成节点的 Spawn Hazard Handling Override 中，选择 Always Spawn, Ignore Collisions。这能防止因为碰撞重叠而消除掉生成的资产。

6. 调试工具：查看运行时加载情况

运行游戏后，在控制台输入以下命令来观察到底哪些“单元格”被加载了：

wp.Runtime.ToggleDrawRuntimeHash2D 1

你会看到一个 2D 图表，绿色的方块代表已加载区域。如果你的建筑所在的方块是红色的，说明玩家距离太远或加载半径设置太小。

建议总结：
大多数情况下，这都是由于 World Partition 的 Loading Range（加载距离） 过短导致的。请在 World Settings 中调大 Runtime Hash 的 Loading Range 属性，以确保玩家能看到更远处的物体。

---

## 193. 显示在关卡编辑器中的实例在关卡运行后都会加载到关卡中吗

**问题：** 显示在关卡编辑器中的实例在关卡运行后都会加载到关卡中吗

**答案：** 答案是：不一定。

在虚幻引擎 5 中，“编辑器可见”并不等同于“运行时可见”。为了消除 (Elimination) 这种不一致，你需要了解以下几种导致资产在运行后“失踪”的机制：

1. 世界分区 (World Partition) 的加载策略

这是最常见的原因。在编辑器中，你可以手动加载（Load）所有区域的单元格以便编辑，但在运行（Play）时，引擎遵循以下规则：

空间加载 (Spatially Loaded)：如果 Actor 的 Is Spatially Loaded 勾选了，它只有在玩家（Streaming Source）靠近它的一定范围内（Loading Range）才会被加载。如果你运行后的起始点离物体太远，该物体在运行瞬间会被消除 (Elimination) 出场景。

非加载状态：如果你在 World Partition 编辑器窗口中右键点击了“Unload”，虽然物体还在 Outliner 里，但在关卡中是看不见的。

2. 数据层 (Data Layers) 的影响

如果资产被分配到了某个 Data Layer：

如果该 Data Layer 的 Initial State（初始状态） 设为 Unloaded，那么即便它在编辑器里显示，运行后也会被卸载。

只有状态为 Loaded 或 Activated 的数据层在运行后才会保持显示。

3. Actor 的属性过滤

部分属性会直接阻止资产进入运行环境：

Actor Hidden In Game：如果勾选，它只在编辑器显示，运行后变透明，但物理碰撞可能还在。

Is Editor Only：如果勾选，这个 Actor 根本不会被打包或带入运行内存，它是彻底被消除 (Elimination) 掉的。

Level Instance 模式：如果你使用了关卡实例（Level Instance），其 Streaming Mode 如果设置不当，可能导致子关卡内容未被触发加载。

4. 植被 (Foliage) 的剔除距离

对于成片的树木和草地（Foliage）：

在植被编辑器中有一个 Cull Distance（剔除距离） 设置。如果运行时的摄像机超出了这个距离，植被会立即消失。

编辑器窗口有时会忽略这个剔除距离以方便预览，但运行（Play）时会严格执行。

5. 预览与运行的差异清单

资产状态
编辑器内 (Editor)
运行后 (Runtime)

Always Loaded
永远可见
永远可见

Spatially Loaded
取决于手动 Load/Unload
取决于玩家距离

Hidden In Game
可见
不可见

Data Layer: Unloaded
可见 (如果手动开启)
不可见

解决方法建议：

对于建筑：选中它，在细节面板中将 Grid Placement 设置为 Always Loaded，这样可以确保它不受距离影响，始终加载。

对于大范围树木：检查 World Settings 中的 Loading Range，确保其数值大于玩家到树木的距离。

验证方法：运行游戏后，按下 F8 键弹出控制台，在场景中飞向原本消失的位置。如果靠近后物体出现了，说明是流送距离 (Streaming Distance) 的问题。

通过调整 Grid Placement 和 Data Layer 状态，你可以确保在编辑器中布置的所有实例都能在运行时稳定显示，消除 (Elimination) 资产随机加载失败的困扰。

---

## 194. 怎么在运行的关卡中查看实例是否加载

**问题：** 怎么在运行的关卡中查看实例是否加载

**答案：** 在运行（Play）过程中，你可以通过以下三种专业方法来实时监测实例的加载状态，从而消除 (Elimination) 对资产是否存在的疑惑：

1. 使用“F8 弹出”模式与大纲视图 (推荐)

这是最直接的方法，可以在不停止运行的情况下检查场景树。

操作：在运行（PIE）时，按下键盘上的 F8 键。

此时你的控制权会从玩家角色脱离，恢复为编辑器相机。

查看 Outliner（大纲视图）：

正常颜色：如果 Actor 名称显示为正常白色，说明它已加载。

置灰或缺失：如果在 Outliner 中找不到该 Actor，或者它显示为置灰状态（且带有“Unloaded”标记），说明它已被消除 (Elimination) 出运行时环境。

技巧：在 Outliner 的搜索框输入 Actor 名字，如果搜索不到，说明它确实没有被加载到当前的内存中。

2. 使用 World Partition 运行时调试命令

如果你正在使用世界分区系统，可以通过控制台命令可视化查看加载区域：

按下键盘的 ~ 键打开控制台，输入并执行以下命令：

wp.Runtime.ToggleDrawRuntimeHash2D 1

查看画面：屏幕上会出现一个平面网格图。

绿色方块：表示当前已成功加载到内存中的单元格。

红色方块：表示未加载的单元格。

蓝色圆点/箭头：代表你的玩家位置（Streaming Source）。

通过这个图，你可以直观地看到你的建筑或树木是否落在“绿色区域”内。

3. 查看实时统计数据 (Stat Commands)

如果你怀疑是内存瓶颈导致实例被卸载，可以使用统计命令：

控制台输入：stat levels。

屏幕右侧会显示当前加载的所有子关卡或分区状态。

绿色：已加载并可见。

红色：未加载。

黄色：正在加载中。

如果你的实例属于某个特定分区且该分区显示为红色，那么实例肯定不会显示。

4. 消除 (Elimination) 视觉误判：检查碰撞

有时实例加载了但因为材质问题（如透明度、Shader 报错）不可见：

按下 F8 弹出后，在控制台输入：pxvis collision 或点击查看模式改为 Wireframe（线框模式）。

如果你能看到建筑的碰撞框或线框，说明实例已经加载，只是渲染出现了问题（比如变透明了）。

5. 检查“数据层”实时状态

如果使用了数据层，可以在运行时查看它们的激活情况：

控制台输入：wp.Runtime.DumpDataLayers。

这会在 Output Log（输出日志） 中打印出当前所有数据层的状态（Active, Loaded, Unloaded）。

如果你的树木所在的层显示为 Unloaded，那么它们在运行场景中是不存在的。

总结

最简单高效的流程是：运行 -> F8 -> 在 Outliner 中搜索实例 -> 选中实例按 ‘F’ 键聚焦。如果聚焦后镜头飞向一片虚无，说明该实例已被运行时逻辑消除 (Elimination)。

---

## 195. 这和未加载的实例放置在子关卡中有关吗

**问题：** 这和未加载的实例放置在子关卡中有关吗

**答案：** 是的，这与子关卡（Sub-levels）的加载机制有着直接且重大的关系。在虚幻引擎 5 中，如果你使用了传统的“关卡流送（Level Streaming）”或“关卡实例（Level Instance）”，子关卡中的内容并不会自动全部加载。

为了消除 (Elimination) 这种不加载的情况，请检查以下几个核心关联点：

1. 流送方法 (Streaming Method) 设置

在“Levels（关卡）”窗口中，每个子关卡都有一个加载方式。

Blueprint（蓝图加载）：这是默认设置。这意味着除非你通过蓝图显式调用 Load Stream Level 节点，否则该子关卡在运行时永远不会出现。

Always Loaded（始终加载）：如果你希望这些树木和建筑在运行后立即显示，右键点击子关卡，将 Streaming Method 改为 Always Loaded。

2. 世界分区 (World Partition) 与子关卡的冲突

如果你在开启了 World Partition 的主关卡中手动放入了传统的子关卡，可能会导致逻辑混乱：

Level Instances：在 UE5 中，建议将子关卡作为 Level Instance 拖入场景。

嵌入模式 (Embedded)：选中场景中的 Level Instance Actor，在细节面板中查看其 Level Behavior。

如果是 Embedded，子关卡中的 Actor 会被拆散并直接合并到主关卡的 World Partition 网格中，遵循主关卡的距离加载规则。

如果是 Level Streaming，它会作为一个独立的整体进行流送。如果没触发加载指令，整个子关卡都会被消除 (Elimination) 掉。

3. “空间加载”属性的继承

如果子关卡被设置为 Embedded 模式，那么子关卡内所有 Actor 的 Is Spatially Loaded 属性将起作用：

如果子关卡里的树木勾选了“空间加载”，而主关卡的玩家起始点（Player Start）距离这些树木太远，那么即使子关卡本身加载了，里面的树木也会因为距离原因被消除 (Elimination) 掉而不显示。

4. 消除 (Elimination) 路径：检查层级关系

请确认你的操作流程：

打开 Window > Levels。

查看消失的资产所属的子关卡，其左侧的小圆点是否为深色（未加载）。

右键该关卡 -> Change Streaming Method -> 切换为 Always Loaded。

重新运行（Play），查看资产是否出现。

5. 坐标偏移问题

有时子关卡加载了，但由于“世界原点偏移（World Origin Rebasing）”或子关卡本身的坐标不在主关卡视野内，导致看起来像没加载：

在运行时按 F8，在 Outliner 中找到子关卡里的某个 Actor。

双击它，看相机飞向哪里。如果坐标极其遥远（如数百万个单位之外），说明是坐标对齐问题。

总结建议

如果这些建筑和树木是关卡的基础组成部分，最稳健的做法是：

消除 (Elimination) 复杂性：将这些资产从子关卡中移出，直接放入主关卡（Persistent Level）。

或者：确保子关卡的流送方式设为 Always Loaded。

或者：如果使用 Level Instance，确保其加载范围（Loading Range）覆盖了你的初始位置。

---

## 210. 切换植物模式时显示无法在PIE中编辑植物，该如何解决

**问题：** 切换植物模式时显示无法在PIE中编辑植物，该如何解决

**答案：** 在虚幻引擎中，当你在运行预览（Play In Editor，简称 PIE）时尝试切换到植物模式（Foliage Mode），系统会弹出“无法在 PIE 中编辑植物”的提示。这是因为植物的绘制和编辑属于编辑器阶段（Editor-time）的操作，而 PIE 是一种运行时模拟。

要消除 (Elimination) 该限制并恢复编辑功能，请按照以下步骤操作：

1. 停止运行模拟

植物模式需要直接修改关卡资产数据，这在游戏运行状态下是被锁定的。

操作：按下键盘上的 Esc 键，或者点击顶部工具栏上的红色 Stop（停止） 按钮退出 PIE 模式。

结果：退出运行后，你将能够正常进入植物模式并使用笔刷工具。

2. 核心原因说明

编辑器 vs 运行时：植物系统（Instanced Static Meshes）为了性能优化，在游戏运行时是静态合并的。

数据安全：虚幻引擎为了防止在测试游戏逻辑时意外破坏场景资产，禁止在模拟过程中修改地形和植物分布。通过这种方式，引擎消除 (Elimination) 了因运行时误操作导致关卡数据损坏的风险。

3. 如果你需要在运行时动态生成植物

如果你希望在游戏过程中（而非编辑器中）实现植物的产生或消除 (Elimination)，你不能使用“植物模式”笔刷，而需要使用以下技术：

Procedural Content Generation (PCG)：使用 UE5 的 PCG 图表，可以根据逻辑在运行时动态生成植被。

蓝图生成：使用 SpawnActorFromClass 或者针对高性能需求的 AddInstance（用于实例化静态网格体组件）来实现在游戏逻辑触发时放置物体。

4. 常见排查 checklist

如果退出 PIE 后依然无法编辑，请检查以下几点：

当前模式：确保在左上角的模式选择器中确实选中了 Foliage。

激活层：如果你使用了世界分区（World Partition），确保你要编辑的区域所在的层级（Data Layer）不是锁定或隐藏状态。

选中资源：在植物面板中，必须先勾选你想要放置的静态网格体资产前面的复选框，否则笔刷将无法工作。

通过停止 PIE 会话，你可以立即消除 (Elimination) 报错并恢复对场景中植被资产的创作与修改。

---

