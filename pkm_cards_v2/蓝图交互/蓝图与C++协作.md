## 28. 已创建的蓝图类如何转为C++类继续编辑

**问题：** 已创建的蓝图类如何转为C++类继续编辑

**答案：** 在 Unreal Engine 中，将已有的蓝图类（Blueprint Class）转为 C++ 类并不是一个“一键自动化”的过程，而是一个“手动迁移 + 重新关联”的工作流。其核心思想是创建一个 C++ 基类，然后让原有的蓝图类继承自这个新的 C++ 类。

以下是标准的操作步骤：

1. 核心流程概述

识别基类：确认当前蓝图继承自哪个父类（如 Actor, Character, Pawn）。

创建 C++ 基类：新建一个相同类型的 C++ 类。

迁移变量与函数：使用 UPROPERTY 和 UFUNCTION 在 C++ 中声明蓝图原有的逻辑。

重父类化（Reparenting）：将蓝图的父类改为新创建的 C++ 类。

清理逻辑：逐步将蓝图节点替换为 C++ 代码实现。

2. 详细操作步骤

第一步：查看蓝图的当前父类

在蓝图编辑器中，查看右上角的 Parent class（例如 Actor）。这决定了你稍后创建 C++ 类时应选择的父类。

第二步：利用“预览等效 C++ 标头”辅助开发

UE 提供了一个实用工具来辅助转换：

在内容浏览器中，右键点击蓝图资源。

选择 预览等效 C++ 标头 (Preview Equivalent C++ Header)。

这将打开一个窗口，展示蓝图中的变量、组件和函数在 C++ 中对应的声明代码。你可以将其作为编写 .h 文件的参考。

第三步：创建 C++ 基类

点击 Tools > New C++ Class。

选择与原蓝图相同的父类（例如 Character）。

命名类（建议使用类似 BasePlayer 的命名，以区别于原蓝图）。

在生成的 .h 文件中，声明你需要迁移的变量和函数：// 示例：将蓝图变量搬到 C++
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
float Health;

// 示例：声明一个在蓝图中实现的事件（如角色被“淘汰”时）
UFUNCTION(BlueprintImplementableEvent, Category = "Events")
void OnEliminated();

第四步：重父类化蓝图（Reparent）

这是最关键的一步，让蓝图和 C++ 建立继承关系：

打开你的蓝图类。

在上方菜单栏选择 File > Reparent Blueprint。

在列表中搜索并选择你刚刚创建的 C++ 类。

注意：此时蓝图可能会报错，因为 C++ 中定义的变量名可能与蓝图中现有的变量冲突。你需要删除蓝图中重复的局部变量，转而使用从 C++ 继承来的变量。

第五步：迁移逻辑（手动重写）

蓝图的连线逻辑无法自动转为代码，你需要在 .cpp 文件中手动实现。

如果某些逻辑你想保留在蓝图，但在 C++ 中调用，请使用 BlueprintImplementableEvent。

如果你想在 C++ 中写好底层逻辑，但允许蓝图进行重写或扩展，请使用 BlueprintNativeEvent。

3. 进阶建议与最佳实践

逐步迁移：不要试图一次性把所有逻辑都转为 C++。先将关键的性能敏感部分（如 Tick 中的逻辑、复杂的数学计算、大规模数据处理）迁移到 C++，UI 和视觉表现逻辑可以保留在蓝图中。

消除冲突：在 C++ 中定义变量后，蓝图会自动继承。如果原蓝图中有同名变量，请务必先重命名或删除蓝图变量，以避免编译错误或逻辑混乱。

核心重定向（Core Redirects）：如果你在大规模重构并更改了类名或变量名，可能需要配置 DefaultEngine.ini 中的 CoreRedirects，以防止已放置在关卡中的实例引用丢失。

避免“淘汰”蓝图：最理想的架构是 C++ 作为底层框架，蓝图作为配置和表现层。不要把所有东西都写死在 C++ 里，利用 UPROPERTY 暴露参数给设计师在蓝图中调整。

4. 测试与验证

编译 C++：在编辑器中点击 Compile 按钮或通过 Live Coding 编译。

检查默认值：在蓝图的 Class Defaults 中检查从 C++ 继承来的属性是否正确显示。

运行 PIE：进入游戏测试功能是否与转换前一致。若逻辑涉及角色“淘汰”（elimination），请确保在 C++ 的逻辑处理中正确触发了相关的事件。

---

## 29. 在父类C++中编写函数，再使用子类蓝图类调用该函数是否可行

**问题：** 在父类C++中编写函数，再使用子类蓝图类调用该函数是否可行

**答案：** 在 Unreal Engine 中，这不仅可行，而且是 C++ 与蓝图混编的核心推荐工作流（即：C++ 定义底层逻辑，蓝图进行上层扩展和调用）。

要实现这一点，你只需要在 C++ 函数声明上方添加正确的 UFUNCTION 宏。

1. 核心方法：使用 BlueprintCallable

如果你在 C++ 父类中写了一个逻辑函数，想让子类蓝图能直接像“普通节点”一样调用它，请按照以下步骤操作：

C++ 父类代码 (.h)

UCLASS()
class MYPROJECT_API AMyBaseActor : public AActor
{
 GENERATED_BODY()

public:
 // BlueprintCallable 允许蓝图调用此函数
 // Category 决定了它在蓝图右键菜单中的分类
 UFUNCTION(BlueprintCallable, Category = "MyCustomLogic")
 void CalculateHealing(float Amount);
};
C++ 父类实现 (.cpp)

void AMyBaseActor::CalculateHealing(float Amount)
{
 // 这里编写你的 C++ 核心逻辑
 UE_LOG(LogTemp, Log, TEXT("Calculating healing: %f"), Amount);
}

2. 进阶方法：不同场景下的 UFUNCTION 标记

根据你的需求，有三种最常见的标记方式：

标记符
效果
适用场景

BlueprintCallable
蓝图可以调用该 C++ 函数。
像“加血”、“开火”这种由 C++ 写死的通用功能。

BlueprintNativeEvent
C++ 提供默认实现，蓝图可以覆盖（Override）它。
C++ 写好基础逻辑，但允许蓝图在执行前后增加特效或声音。

BlueprintImplementableEvent
C++ 不提供实现，完全由蓝图编写逻辑。
C++ 负责在特定时机触发（如“当玩家进入范围”），具体表现由蓝图决定。

3. 如何在蓝图中调用？

编译代码：保存文件并点击编辑器下方的 Compile（或使用 Live Coding）。

打开蓝图：打开继承自该 C++ 类的子类蓝图。

搜索节点：在 Event Graph（事件图表）中点击右键，输入你在 Category 中定义的名称或函数名（如 Calculate Healing）。

连接连线：你会看到一个带蓝色“F”图标的函数节点，直接连线即可使用。

4. 关键注意事项

访问修饰符：函数必须声明在 public 或 protected 下。如果声明在 private 下，子类蓝图将无法搜索到该函数。

重父类化：如果你是先创建了蓝图，后来才写的 C++ 基类，别忘了在蓝图编辑器的 File -> Reparent Blueprint 中将蓝图的父类改为你的 C++ 类。

返回值与参数：C++ 函数的参数会自动变成蓝图节点的输入引脚，返回值会变成输出引脚。

const 关键字：如果你的函数标记为 const（例如 void GetData() const;），它在蓝图中会自动显示为绿色的“纯函数”（Pure Function），即没有执行线（白线），通常用于获取数据。

总结： 这种“C++ 声明、蓝图调用”的模式是提高性能和开发效率的最佳手段。通过这种方式，你可以把复杂的数学运算或性能敏感的操作留在 C++ 中，而把灵活的游戏逻辑交给蓝图。

---

## 31. 编写好父C++类后，子蓝图该如何调用

**问题：** 编写好父C++类后，子蓝图该如何调用

**答案：** 编写好 C++ 父类并定义了相关变量和函数后，让子蓝图调用这些内容通常分为三个核心环节：重新设置父类、调用函数、重写事件。

以下是详细的操作指南：

第一步：将蓝图关联到 C++ 类（重父类化）

如果你的蓝图是之前创建好的，你需要告诉它现在的“父亲”是哪个 C++ 类。

打开你的蓝图类。

在顶部菜单栏点击 File（文件） > Reparent Blueprint（重载父项蓝图）。

在搜索框输入你编写的 C++ 类名并选中它。

验证：查看蓝图编辑器右上角的 Parent class，确认它已显示为你新写的 C++ 类。

第二步：调用 C++ 函数

取决于你在 C++ 中如何声明函数，调用方式有所不同：

1. 调用普通函数 (BlueprintCallable)

这是最常见的调用方式，类似于调用蓝图内置节点。

C++ 声明：UFUNCTION(BlueprintCallable, Category = "Movement")
void SyncToTarget(FTransform TargetTransform);

蓝图调用：在图表中右键搜索 Sync To Target。你会看到一个带有蓝色 [f] 标志的节点，连入执行线即可。

2. 调用带返回值的函数 (BlueprintPure)

如果你只想获取数据而不改变状态（如获取计算后的位置）。

C++ 声明：UFUNCTION(BlueprintPure, Category = "Stats")
float GetCurrentHealth() const;

蓝图调用：右键搜索并找到该节点。它没有执行引脚（白线），直接连入数据线即可。

第三步：重写或响应 C++ 事件

如果你希望在 C++ 中触发逻辑，但在蓝图中实现具体效果。

1. 响应事件 (BlueprintImplementableEvent)

C++ 声明：UFUNCTION(BlueprintImplementableEvent, Category = "Events")
void OnSyncCompleted();

蓝图实现：在蓝图图表中右键搜索 Event On Sync Completed。这会生成一个红色的事件节点，当 C++ 代码执行到该处时，蓝图中的连线会被触发。

2. 重写原生事件 (BlueprintNativeEvent)

C++ 声明：UFUNCTION(BlueprintNativeEvent, Category = "Events")
void ProcessDamage(float Amount);

蓝图实现：

在左侧 My Blueprint（我的蓝图） 面板的 Functions 栏目中，鼠标悬停在 Override（重写） 下拉菜单上。

找到 Process Damage 并点击。

蓝图会创建一个函数图表。如果你想保留 C++ 中的基础逻辑，请右键点击该函数入口节点，选择 Add Call to Parent Function（添加对父函数的调用）。

第四步：读写 C++ 变量

你在 C++ 中标记为 BlueprintReadWrite 的变量，在蓝图中可以像普通蓝图变量一样操作：

在左侧 My Blueprint 面板中，展开 Variables 栏目。

你会发现这些变量通常被归类在 C++ 定义的 Category 标签下。

直接将它们拖入图表，选择 Get 或 Set。

常见问题排查

找不到函数或变量？

检查 C++ 中是否使用了正确的宏：BlueprintReadWrite 或 BlueprintCallable。

检查函数是否声明在 public 或 protected 访问域下（private 对蓝图不可见）。

重启编辑器：如果使用了 Live Coding（小闪电图标），有时结构改动太大需要关闭并重新从 IDE 编译启动。

变量名冲突？

如果蓝图之前定义过同名变量，重父类化后会报错。你必须删除蓝图里的局部变量，转而使用 C++ 继承过来的那个变量。

避免逻辑“淘汰” (Elimination)：

在 C++ 中通过 SetActorTransform 实现移动时，如果蓝图里同时也用 Timeline 或 Tick 修改同一个位置，会导致抖动。确保同一时间只有一个系统在控制变换。

通过这种结构，你的 C++ 父类负责沉重的计算（如插值运算），而子蓝图则负责调用这些计算结果来触发特效或 UI 更新。

---

## 54. 编译完成后，重启编辑器时显示如下选项，该怎么解决：The following modules are missing o…

**问题：** 编译完成后，重启编辑器时显示如下选项，该怎么解决：The following modules are missing or built with a different engine version:

 WCWZ_1127

Would you like to rebuild them now?

**答案：** 这个错误通常是由于虚幻引擎检测到你的项目模块（WCWZ_1127）与当前引擎版本（5.2）之间的二进制文件（Binaries）不匹配，或者是编译后的缓存出现了损坏。

请按照以下步骤进行“深度清理并手动重建”，这比直接点击对话框中的“Yes”更稳妥：

1. 执行深度清理（消除旧缓存）

在手动重新编译之前，必须清除可能干扰编译的旧文件：

关闭虚幻编辑器和 Visual Studio。

进入你的项目根目录（包含 .uproject 文件的文件夹）。

删除以下文件夹（这些是自动生成的缓存，可以安全删除）：

Binaries

Intermediate

DerivedDataCache

.vs (隐藏文件夹)

如果你在 Plugins/Cosys-AirSim 目录下也看到了 Binaries 和 Intermediate 文件夹，请一并删除。

2. 重新生成项目文件

在项目根目录，右键点击 WCWZ_1127.uproject 文件。

选择 Generate Visual Studio project files。

如果你没有看到这个选项，说明你的引擎关联可能有问题。请右键并选择 “Switch Unreal Engine Version”，确保选择了 5.2。

3. 在 Visual Studio 中进行完整编译

不要直接打开 .uproject 文件，而是先通过 IDE 编译：

双击打开生成的 WCWZ_1127.sln 文件。

在 Visual Studio 顶部的工具栏中，确认配置为：Development Editor 和 Win64。

在右侧“解决方案资源管理器”中，右键点击你的项目名称（WCWZ_1127），选择 Rebuild（重新生成）。

观察输出窗口：

如果显示 Build: 1 succeeded（或更多成功），说明编译通过。

如果显示 Failed，请查看报错的具体代码行。

4. 处理编译失败的常见原因

如果在 Visual Studio 中重新生成失败，通常是以下原因：

插件路径问题：确保 Cosys-AirSim 放在 Plugins 文件夹下，且文件夹结构正确。

缺少依赖：检查 Source/WCWZ_1127/WCWZ_1127.Build.cs 文件。如果你的项目逻辑需要调用 AirSim 的代码，你必须在 PublicDependencyModuleNames 中添加 "AirSim"。

编译器版本：UE 5.2 必须配合 Visual Studio 2022。请确保你没有误用旧版 VS。

5. 再次尝试启动

当 Visual Studio 编译成功后：

不要点击刚才那个提示框的 “Yes”。

直接双击你的 .uproject 文件启动。

此时应该能跳过（eliminate）报错，直接进入编辑器界面。

核心提示： 那个对话框提示的 “Rebuild Now” 往往因为权限或环境路径问题失败。手动删除 Binaries/Intermediate 文件夹并重新生成 SLN 是解决此类“引擎版本不匹配”或“模块缺失”问题的行业标准做法。

---

## 55. 1>------ 已启动生成: 项目: WCWZ_1127, 配置: Development_Editor x64 --…

**问题：** 1>------ 已启动生成: 项目: WCWZ_1127, 配置: Development_Editor x64 ------
1>Using bundled DotNet SDK version: 6.0.302
1>Running UnrealBuildTool: dotnet "..\..\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll" WCWZ_1127Editor Win64 Development -Project="C:\WuCaiWan\WCWZ_1127.uproject" -WaitMutex -FromMsBuild
1>Log file: C:\Users\Administrator\AppData\Local\UnrealBuildTool\Log.txt
1>Creating makefile for WCWZ_1127Editor (no existing makefile)
1>Library 'Shell32.lib' was not resolvable to a file when used in Module 'AirSim', assuming it is a filename and will search library paths for it. This is slow and dependency checking will not work for it. Please update reference to be fully qualified alternatively use PublicSystemLibraryPaths if you do intended to use this slow path to suppress this warning.
1>Library 'dinput8.lib' was not resolvable to a file when used in Module 'AirSim', assuming it is a filename and will search library paths for it. This is slow and dependency checking will not work for it. Please update reference to be fully qualified alternatively use PublicSystemLibraryPaths if you do intended to use this slow path to suppress this warning.
1>Library 'dxguid.lib' was not resolvable to a file when used in Module 'AirSim', assuming it is a filename and will search library paths for it. This is slow and dependency checking will not work for it. Please update reference to be fully qualified alternatively use PublicSystemLibraryPaths if you do intended to use this slow path to suppress this warning.
1>Parsing headers for WCWZ_1127Editor
1> Running Internal UnrealHeaderTool C:\WuCaiWan\WCWZ_1127.uproject C:\WuCaiWan\Intermediate\Build\Win64\WCWZ_1127Editor\Development\WCWZ_1127Editor.uhtmanifest -WarningsAsErrors -installed
1>C:\WuCaiWan\Source\WCWZ_1127\Public\MyPawn.h(51): error : Member variable declaration: 'MouseMoveSpeed' cannot be defined in 'AMyPawn' as it is already defined in scope 'AMyPawn' (shadowing is not allowed)
1>Total of 0 written
1>C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VC\v170\Microsoft.MakeFile.Targets(44,5): error MSB3073: 命令“C:\app\UE\UE_5.2\Engine\Build\BatchFiles\Build.bat WCWZ_1127Editor Win64 Development -Project="C:\WuCaiWan\WCWZ_1127.uproject" -WaitMutex -FromMsBuild”已退出，代码为 6。
1>已完成生成项目“WCWZ_1127.vcxproj”的操作 - 失败。
========== 生成: 0 成功，1 失败，0 最新，0 已跳过 ==========
========== 生成 于 15:16 完成，耗时 03.527 秒 ==========

**答案：** 这是一个非常典型的 C++ 编译错误。报错信息 shadowing is not allowed 意味着你在 MyPawn.h 中重复定义了同名的变量，或者你的变量名与父类（如 APawn）中的变量名冲突了。

在虚幻引擎中，为了保证反射系统和内存管理的稳定性，严禁在同一个类中出现重名的变量定义（即“变量遮蔽/隐藏”）。

1. 核心错误分析

日志指出：
C:\WuCaiWan\Source\WCWZ_1127\Public\MyPawn.h(51): error : Member variable declaration: 'MouseMoveSpeed' cannot be defined in 'AMyPawn' as it is already defined in scope 'AMyPawn'

这说明在你的 MyPawn.h 文件中，变量 MouseMoveSpeed 被声明了两次。

2. 修复步骤

请打开 C:\WuCaiWan\Source\WCWZ_1127\Public\MyPawn.h，检查代码：

查找重复项：在文件中搜索 MouseMoveSpeed。

执行消除（Elimination）：你会发现类似下面的代码，请删掉其中多余的一个。

错误的示例代码：

// 假设这是你的代码
UPROPERTY(EditAnywhere)
float MouseMoveSpeed; // 第一次声明

// ... 隔了几行 ...

UPROPERTY(EditAnywhere)
float MouseMoveSpeed; // 第二次声明 -> 导致报错！
修复后的代码：
只需保留一个定义即可：

UPROPERTY(EditAnywhere, Category = "Input")
float MouseMoveSpeed;
3. 注意事项（变量命名建议）

如果你的变量名与虚幻引擎底层父类的变量名冲突（虽然 MouseMoveSpeed 不太可能是系统保留名），通常建议给变量加上前缀或换个更具体的名称，例如 CameraRotationSpeed 或 BaseLookUpRate。

4. 重新编译

完成上述修改并保存后：

回到 Visual Studio。

右键点击项目 WCWZ_1127，选择 Build (生成)。

一旦这个 shadowing 错误被消除，虚幻头文件工具 (UHT) 就能完成解析，随后就会进入正式的 C++ 代码编译阶段。

Epic Developer Assistant 提示： 修复完这个语法问题后，你的 AirSim 插件编译应该就能正式开始了。如果后续在链接阶段报错，请确保你已经按照之前的建议运行了插件目录下的 build.cmd。

---

## 56. WCWZ_1127 could not be compiled. Try rebuilding from source …

**问题：** WCWZ_1127 could not be compiled. Try rebuilding from source manually.

**答案：** 既然你收到了“Could not be compiled. Try rebuilding from source manually”的提示，说明虚幻引擎的启动器已经无法自动处理你的代码错误了。

这种提示通常出现在多次编译失败后，项目的 Intermediate 或 Binaries 文件夹中留下了损坏的中间文件。要解决这个问题，你必须执行一次“手动深度清理并重新编译”。

请严格按照以下 4 个步骤操作，这能彻底消除（Elimination）你目前遇到的环境和代码冲突。

第一步：深度清理项目文件夹

关闭 所有的 Visual Studio 和虚幻编辑器窗口。

进入你的项目根目录 C:\WuCaiWan\。

手动删除 以下三个文件夹（不要担心，这些是自动生成的缓存）：

Binaries

Intermediate

Saved

（可选但推荐）删除项目根目录下的 .sln 文件。

第二步：确保 .Target.cs 配置正确

由于你使用的是安装版引擎（Installed Engine），请再次确认 Source/ 文件夹下的 WCWZ_1127.Target.cs 和 WCWZ_1127Editor.Target.cs。

两个文件的构造函数内必须包含以下这两行：

bOverrideBuildEnvironment = true; 
CppStandard = CppStandardVersion.Cpp20;

第三步：修正 UnrealDistanceSensor.cpp 的最终代码

在重新编译前，请最后检查一次 Plugins/AirSim/Source/UnrealSensors/UnrealDistanceSensor.cpp 的第 19 行。为了彻底绕过 UE 5.2 的 LWC 类型检查，请使用以下最保险的写法：

// 彻底分解步骤，避免编译器在三元运算符中纠结类型
float distance;
if (is_hit)
{
 // 将 double 强转为 float，显式告诉编译器你接受精度损失
 double RawDistance = (double)dist_hit.Distance;
 distance = (float)(RawDistance / 100.0);
}
else
{
 distance = getParams().max_distance;
}

第四步：执行“手动重新编译”

右键点击项目根目录的 WCWZ_1127.uproject 文件。

选择 Generate Visual Studio project files（这会根据你的 .Target.cs 重新生成 .sln）。

双击打开生成的 WCWZ_1127.sln。

在 Visual Studio 顶部确认配置为 Development Editor 和 Win64。

在“解决方案资源管理器”中找到你的项目 WCWZ_1127，右键点击，选择 Build (生成)。

关键：如果再次报错，请看这里

如果右键 Build 依然报错，请不要看 Visual Studio 底部的“错误列表 (Error List)”，那个列表在虚幻开发中往往是不准确的。

请看“输出 (Output)”窗口：

找到 Output 窗口中的具体报错位置。

如果你看到了 ... is already defined in scope 'AMyPawn'，说明你之前的 MouseMoveSpeed 重复定义问题还没删干净，请回到 MyPawn.h 搜索并删除重复项。

如果你看到了新的 double 到 float 转换错误，请告诉我具体是哪个文件、哪一行。

执行完这四步后，你应该能顺利通过编译并正常打开虚幻引擎编辑器。

---

## 57. Running C:/app/UE/UE_5.2/Engine/Build/BatchFiles/Build.bat -…

**问题：** Running C:/app/UE/UE_5.2/Engine/Build/BatchFiles/Build.bat -projectfiles -project="C:/WuCaiWan/WCWZ_1127.uproject" -game -rocket -progress -log="C:\WuCaiWan/Saved/Logs/UnrealVersionSelector-2026.05.27-16.29.50.log"
Using bundled DotNet SDK version: 6.0.302
Running UnrealBuildTool: dotnet "..\..\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll" -projectfiles -project="C:/WuCaiWan/WCWZ_1127.uproject" -game -rocket -progress -log="C:\WuCaiWan/Saved/Logs/UnrealVersionSelector-2026.05.27-16.29.50.log"
Log file: C:\WuCaiWan\Saved\Logs\UnrealVersionSelector-2026.05.27-16.29.50.log
Log file: C:\Users\Administrator\AppData\Local\UnrealBuildTool\Log_GPF.txt

Some Platforms were skipped due to invalid SDK setup: IOS, Android, Linux, LinuxArm64.
See the log file for detailed information

Generating VisualStudio project files:
Discovering modules, targets and source code for project...
Errors generated while parsing 'C:\WuCaiWan\Source\WCWZ_1127\WCWZ_1127.Build.cs'
C:\WuCaiWan\Source\WCWZ_1127\WCWZ_1127.Build.cs(11,106): error CS1056: Unexpected character '??'
C:\WuCaiWan\Source\WCWZ_1127\WCWZ_1127.Build.cs(11,107): error CS1003: Syntax error, ',' expected
Unhandled exception: System.IO.DirectoryNotFoundException: Could not find a part of the path 'C:\WuCaiWan\Intermediate\Build\BuildRules\WCWZ_1127ModuleRulesManifest.json'.
 at Microsoft.Win32.SafeHandles.SafeFileHandle.CreateFile(String fullPath, FileMode mode, FileAccess access, FileShare share, FileOptions options)
 at Microsoft.Win32.SafeHandles.SafeFileHandle.Open(String fullPath, FileMode mode, FileAccess access, FileShare share, FileOptions options, Int64 preallocationSize)
 at System.IO.Strategies.OSFileStreamStrategy..ctor(String path, FileMode mode, FileAccess access, FileShare share, FileOptions options, Int64 preallocationSize)
 at System.IO.Strategies.FileStreamHelpers.ChooseStrategyCore(String path, FileMode mode, FileAccess access, FileShare share, FileOptions options, Int64 preallocationSize)
 at System.IO.Strategies.FileStreamHelpers.ChooseStrategy(FileStream fileStream, String path, FileMode mode, FileAccess access, FileShare share, Int32 bufferSize, FileOptions options, Int64 preallocationSize)
 at System.IO.StreamWriter.ValidateArgsAndOpenPath(String path, Boolean append, Encoding encoding, Int32 bufferSize)
 at System.IO.StreamWriter..ctor(String path)
 at EpicGames.Core.JsonWriter..ctor(FileReference fileName, JsonWriterStyle style) in D:\build\++UE5\Sync\Engine\Saved\CsTools\Engine\Source\Programs\Shared\EpicGames.Core\JsonWriter.cs:line 55
 at UnrealBuildTool.DynamicCompilation.CompileAndLoadAssembly(FileReference OutputAssemblyPath, HashSet`1 SourceFileNames, ILogger Logger, List`1 ReferencedAssembies, List`1 PreprocessorDefines, Boolean DoNotCompile, Boolean ForceCompile, Boolean TreatWarningsAsErrors) in D:\build\++UE5\Sync\Engine\Saved\CsTools\Engine\Source\Programs\UnrealBuildTool\System\DynamicCompilation.cs:line 349
 at UnrealBuildTool.RulesAssembly..ctor(RulesScope Scope, List`1 BaseDirs, IReadOnlyList`1 Plugins, Dictionary`2 ModuleFileToContext, List`1 TargetFiles, FileReference AssemblyFileName, Boolean bContainsEngineModules, Nullable`1 DefaultBuildSettings, Boolean bReadOnly, Boolean bSkipCompile, Boolean bForceCompile, RulesAssembly Parent, ILogger Logger) in D:\build\++UE5\Sync\Engine\Saved\CsTools\Engine\Source\Programs\UnrealBuildTool\System\RulesAssembly.cs:line 140
 at UnrealBuildTool.RulesCompiler.CreateProjectRulesAssembly(FileReference ProjectFileName, Boolean bUsePrecompiled, Boolean bSkipCompile, Boolean bForceCompile, ILogger Logger) in D:\build\++UE5\Sync\Engine\Saved\CsTools\Engine\Source\Programs\UnrealBuildTool\System\RulesCompiler.cs:line 319
 at UnrealBuildTool.ProjectFileGenerator.AddProjectsForAllTargets(PlatformProjectGeneratorCollection PlatformProjectGenerators, List`1 AllGames, List`1 AllTargetFiles, String[] Arguments, ProjectFile& EngineProject, List`1 GameProjects, Dictionary`2 ProjectFileToUProjectFile, Dictionary`2 ProgramProjects, Dictionary`2 RulesAssemblies, ILogger Logger) in D:\build\++UE5\Sync\Engine\Saved\CsTools\Engine\Source\Programs\UnrealBuildTool\ProjectFiles\ProjectFileGenerator.cs:line 2444
 at UnrealBuildTool.ProjectFileGenerator.GenerateProjectFiles(PlatformProjectGeneratorCollection PlatformProjectGenerators, String[] Arguments, ILogger Logger) in D:\build\++UE5\Sync\Engine\Saved\CsTools\Engine\Source\Programs\UnrealBuildTool\ProjectFiles\ProjectFileGenerator.cs:line 916
 at UnrealBuildTool.GenerateProjectFilesMode.Execute(CommandLineArguments Arguments, ILogger Logger) in D:\build\++UE5\Sync\Engine\Saved\CsTools\Engine\Source\Programs\UnrealBuildTool\Modes\GenerateProjectFilesMode.cs:line 67
 at UnrealBuildTool.UnrealBuildTool.Main(String[] ArgumentsArray) in D:\build\++UE5\Sync\Engine\Saved\CsTools\Engine\Source\Programs\UnrealBuildTool\UnrealBuildTool.cs:line 599

**答案：** 找到了导致错误的根源。根据日志显示，你的项目主配置文件 WCWZ_1127.Build.cs 存在语法错误。

错误分析

日志中的这两行是核心：

WCWZ_1127.Build.cs(11,106): error CS1056: Unexpected character '??'

WCWZ_1127.Build.cs(11,107): error CS1003: Syntax error, ',' expected

这说明在第 11 行，由于之前的编辑，代码中混入了非法的字符（可能是全角标点、多余的问号或是编码错误的不可见字符），导致 C# 编译器无法解析该文件。这会直接导致 Generate Project Files 失败，进而引发后续所有的编译代码 6。

修复步骤

打开文件：
使用记事本或 Visual Studio 打开以下路径的文件：
C:\WuCaiWan\Source\WCWZ_1127\WCWZ_1127.Build.cs

定位并修复第 11 行：
找到第 11 行，它通常是 PublicDependencyModuleNames.AddRange(...) 这一行。
请检查该行末尾是否有 ?? 字符或者缺失了引号/逗号。

完全替换该文件的内容：
为了确保彻底消除（Elimination）语法错误，请将 WCWZ_1127.Build.cs 的全部内容替换为以下标准代码：

using UnrealBuildTool;

public class WCWZ_1127 : ModuleRules
{
 public WCWZ_1127(ReadOnlyTargetRules Target) : base(Target)
 {
 PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
 
 // 确保模块名称之间有逗号，且都是半角英文字符
 PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "AirSim" });

 PrivateDependencyModuleNames.AddRange(new string[] { });
 }
}
验证与重新生成

保存文件。

清理临时目录：
手动创建（如果不存在）或清空 C:\WuCaiWan\Intermediate\ 文件夹。日志中提到的 DirectoryNotFoundException 是因为该目录被删除后，UBT 无法在语法错误的情况下自动重建它。

重新生成项目文件：
右键点击 C:\WuCaiWan\WCWZ_1127.uproject -> 选择 Generate Visual Studio project files。

此时应该不会再弹出红色的错误框了。

编译项目：
打开生成的 .sln，右键项目选择 Build。

专家提示：在编辑 .Build.cs 文件时，一定要确保使用英文输入法。日志中的 ?? 通常是由于意外输入了中文字符或全角逗号导致的编码冲突。修复此文件后，之前的环境报错将会被彻底消除。

---

## 58. 我新建了一个C++类的ue工程，将编译完成的AirSim文件夹下的Plugins文件复制到新建的ue工程根目录中，点击运…

**问题：** 我新建了一个C++类的ue工程，将编译完成的AirSim文件夹下的Plugins文件复制到新建的ue工程根目录中，点击运行后，启动引擎可以成功启用AirSim插件。现在我想把原有的工程项目中的AirSim插件删除使其可以正常启动，或是将工程文件的关卡、蓝图类等迁移到新建的C++类ue工程中。帮我分析可行性，告诉我具体的操作步骤。

**答案：** 这是一个非常明智的决定。由于 AirSim 插件与旧项目环境（依赖项、LWC 类型冲突、命名空间冲突）纠缠太深，手动清理往往会留下隐患。

以下是两种可行方案的详细分析与操作步骤，建议优先选择 方案 B（迁移到新项目），因为这样能获得一个最干净、最稳定的开发环境。

方案 A：在原有工程中彻底“切除” AirSim

可行性： 高。通过修改配置文件和物理删除，可以使项目恢复到纯净状态。

具体步骤：

关闭所有编辑器和 VS。

物理删除文件夹：

删除项目根目录下的 Plugins/AirSim 文件夹。

删除项目根目录下的 Binaries、Intermediate、.vs 和 DerivedDataCache 文件夹。

外科手术式修改 .uproject：

右键点击你的 .uproject 文件，用记事本打开。

在 Plugins 数组中，找到名为 "AirSim" 的项并将其整段删除。

重要：如果你的 Modules 数组中引用了 AirSim 相关的模块，也请一并删除。

清理 C++ 源代码：

进入 Source/[ProjectName]/，检查 [ProjectName].Build.cs。

消除（Elimination）：删除 PublicDependencyModuleNames 中引用的 "AirSim" 字符串。

删除所有代码中 #include "AirSim..." 或 #include "AirBlueprintLib.h" 的行。

重新生成：右键 .uproject -> Generate Visual Studio project files。此时项目应能成功生成且不含 AirSim 引用。

方案 B：将关卡和蓝图迁移到新项目（推荐）

可行性： 极高。这是虚幻引擎官方推荐的工作流，能够自动处理资源依赖关系，防止由于手动拷贝导致的引脚丢失。

具体步骤：

准备环境：确保你的新建 C++ 工程已经成功启用了 AirSim 插件，且能够正常编译。

启动旧项目：打开那个包含你想要资源的旧工程（即使它 C++ 报错，只要能进入编辑器即可；如果进不去，请先执行方案 A 使其能启动）。

使用 Migrate 工具：

在 Content Browser（内容浏览器） 中，找到你最重要的资源（通常是 Level 关卡文件）。

右键点击 关卡文件 -> 选择 Asset Actions（资源操作） -> Migrate…（迁移…）。

此时会弹出一个列表，显示该关卡引用的所有模型、材质、蓝图和贴图。点击 OK。

选择目标路径：

在弹出的文件夹选择框中，定位到你新建 C++ 工程的 Content 文件夹。

注意：必须选中 Content 文件夹本身，不要选择其子文件夹。

处理重名资源：如果提示有重名文件（如 StarterContent），通常选择 “No to All” 或跳过。

在新项目中验证：

打开新建项目。

你会发现资源已按原样同步过来。

消除（Elimination）冲突：如果迁移过来的蓝图原本引用了 AirSim 的类（如 AirSimVehicle），你可能需要重新右键该蓝图 -> Class Settings -> 重新指定其父类。

方案对比与建议

特性
方案 A (清理旧项目)
方案 B (迁移至新项目)

风险
可能残留无效引用导致打包失败
几乎无风险，依赖关系自动处理

工作量
较大，需反复修改 C++ 代码
较小，主要是 UI 操作

稳定性
一般
极佳

最终建议：
执行 方案 B。先在新项目中创建好基础环境，然后利用虚幻的 Migrate（迁移） 工具将旧项目的资产搬过去。这能确保所有引用的模型和贴图路径不会丢失，同时彻底 消除（Elimination） 之前旧项目里那些难以追踪的 C++ 编译环境配置错误。

---

## 59. 清理完插件后依然有以下报错：The following modules are missing or built wit…

**问题：** 清理完插件后依然有以下报错：The following modules are missing or built with a different engine version:

 WCWZ_1127

Would you like to rebuild them now?

**答案：** 出现这个提示是因为你虽然删除了插件，但你的项目主模块 (WCWZ_1127) 的二进制文件（DLL）中仍然残留着对 AirSim 的“链接记录”。虚幻引擎发现当前的 DLL 与你修改后的源代码（删除了 AirSim 引用后）不匹配。

由于你已经手动清理了代码，千万不要直接点 “Yes”（通常会因为缓存冲突再次失败并报 Exit Code 6）。请按照以下“深度清理”流程强制引擎重新识别：

1. 物理清理（最关键的一步）

必须手动删除编译缓存，否则引擎会一直尝试加载旧的依赖记录。

进入项目根目录 C:\WuCaiWan\。

手动删除以下文件夹：

Binaries （这里存的是旧的、带有 AirSim 依赖的 DLL）

Intermediate （存的是旧的编译中间件）

Saved

.vs （隐藏文件夹，存储 VS 索引）

WCWZ_1127.sln （旧的解决方案文件）

2. 检查项目构建脚本

确保你的 Build.cs 已经彻底消除（Elimination）了 AirSim 的痕迹：

打开 Source/WCWZ_1127/WCWZ_1127.Build.cs。

检查 PublicDependencyModuleNames：

错误写法：AddRange(new string[] { "Core", "Engine", "AirSim" });

正确写法：AddRange(new string[] { "Core", "Engine" }); （必须删掉 “AirSim”）。

3. 检查代码中的头文件残留

如果你的 C++ 类（比如 MyPawn）还在引用 AirSim 的头文件，编译会报错。

打开 Source/WCWZ_1127/Private/MyPawn.cpp。

删除所有类似 #include "AirBlueprintLib.h" 或 #include "common/..." 的行。

如果有使用了 AirSim 特有函数（如 UAirBlueprintLib::...）的代码，请先将其注释掉。

4. 重新生成并编译

右键点击 WCWZ_1127.uproject，选择 Generate Visual Studio project files。

生成成功后，双击打开新的 WCWZ_1127.sln。

在 Visual Studio 顶部的工具栏，确认配置是 Development Editor + Win64。

在右侧解决方案管理器，右键点击项目名称 WCWZ_1127，选择 Build (生成)。

为什么还会报错？

如果执行完上述操作，VS 编译时报错：

报错 C2065/C2039：说明你的 .cpp 源码里还有没删干净的 AirSim 变量或函数调用。

报错 C1083：说明还有 #include 没删干净。

总结：
只要你删除 Binaries 文件夹并确保 Build.cs 中没有 “AirSim”，再次编译时，虚幻就会生成一个全新的、完全不依赖 AirSim 的模块，那个“Modules are missing”的提示就会彻底 消除（Elimination）。

---

## 60. 我将MyPawn设置为了项目中蓝图类的父类项，现在我想直接删除MyPawn，是否会影响蓝图类

**问题：** 我将MyPawn设置为了项目中蓝图类的父类项，现在我想直接删除MyPawn，是否会影响蓝图类

**答案：** 直接删除 MyPawn 会严重影响以它为父类的蓝图类。

在 Unreal Engine 中，如果一个蓝图类的父类（C++ 类）被删除，该蓝图会变成“孤儿蓝图”。具体后果如下：

无法打开：当你尝试打开该蓝图时，编辑器会报错或直接崩溃。

属性丢失：所有在 C++ 中定义的变量和函数节点在蓝图中都会失效。

功能失效：由于失去了底层逻辑支撑，该蓝图无法在场景中正常工作。

为了安全地 消除（Elimination） MyPawn 并保留你的蓝图类，请务必按照以下步骤操作：

核心操作步骤：先重载父类，再删除代码

第一步：在编辑器中更改蓝图父类

启动虚幻编辑器，打开受影响的蓝图类。

在顶部菜单栏点击 Class Settings（类设置）。

在右侧的 Details（详情） 面板中，找到 Parent Class（父类） 选项。

将父类由 MyPawn 改为引擎通用的 Pawn 或 DefaultPawn。

编译（Compile） 并 保存（Save） 蓝图。此时蓝图已不再依赖你的 C++ 类。

第二步：清理 C++ 代码

关闭虚幻编辑器。

在 Visual Studio 中，右键点击 MyPawn.h 和 MyPawn.cpp，选择 Remove（移除），并在弹出的对话框中选择 Delete（删除）。

打开 WCWZ_1127.Build.cs，确保没有多余的依赖。

第三步：清理二进制文件与重新生成

进入项目文件夹，删除 Binaries 和 Intermediate 文件夹。

右键点击 .uproject 文件，选择 Generate Visual Studio project files。

打开新的 .sln 文件并点击 Build。

进阶技巧：使用 Core Redirects（如果项目已上线或资源极多）

如果你有大量的蓝图引用了 MyPawn，手动一个个修改非常麻烦。你可以通过修改 DefaultEngine.ini 来实现自动重定向：

打开 Config/DefaultEngine.ini。

在 [CoreRedirects] 下添加如下代码：+ClassRedirects=(OldName="/Script/WCWZ_1127.MyPawn",NewName="/Script/Engine.Pawn")注：这会告诉引擎，如果找不到 MyPawn，就自动将其替换为基础的 Pawn。

总结建议

不要直接在文件管理器中删除 .h/.cpp 文件。 必须先在编辑器里解除蓝图与该类的继承关系，然后再清理代码。这样做可以确保你的蓝图资产不被损坏，并彻底 消除（Elimination） 由于架构变动导致的潜在崩溃风险。

---

