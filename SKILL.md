---
name: app-icon-design
label: 多端应用图标设计
description: 移动端应用图标多端设计规范与产出流程，覆盖 Android 自适应图标（Adaptive Icon / Material You 主题图标）、iOS/iPadOS/watchOS 分层图标（Liquid Glass / Icon Composer / 深色与染色变体）、HarmonyOS NEXT 分层新拟态图标、Web/PWA 图标（favicon / maskable / apple-touch-icon）。当用户要求设计或评审应用图标、App Icon、启动图标、桌面图标、PWA 图标、favicon，或要求把一个图标适配到 Android、iOS、鸿蒙、Web 多端，或排查图标被裁切/透明通道/圆角/主题化等问题时使用。包含各端尺寸、安全区、图层结构、外观变体的硬性规范和交付前 QA 脚本。
---

# 多端应用图标设计

一套核心设计 → 四端规范适配 → 产物 QA。所有规范数据以 `references/` 各端文件为准（2026 年一手来源核验过），不要凭记忆改写数值。

## 工作流程

### 第 1 步：锁定设计基础（跨端共用）

- 先确认目标端（Android / iOS / HarmonyOS / Web 的哪些组合）、品牌色板、核心隐喻。单一主导元素 + 简洁背景，四端通用原则。
- 在 1024×1024 画布上设计核心视觉：前景图形 + 背景层，两层分离交付（这是 Android 自适应、iOS 分层、HarmonyOS 分层三种机制的共同基础）。
- 前景图形必须落在最小安全区内：以 Android 66dp 安全区（108dp 画布的 61%）为最紧约束，一处设计即可四端复用。
- 禁止事项（四端共性）：不预切圆角（由系统蒙版处理）、不用文字（无法本地化/过小难读）、不重投影、避免照片和超细线条。

### 第 2 步：按端适配

按用户需要的端，读取对应参考文件后再动手：

- **Android**：读 [references/android.md](references/android.md)。自适应图标三层（前景/背景/单色）、108dp 画布与 66dp 安全区、monochrome 主题图标、Play 商店 512×512。
- **iOS**：读 [references/ios.md](references/ios.md)。Liquid Glass 分层图标、Icon Composer、外观变体（默认/深色/染色）、各平台尺寸与色彩空间。
- **HarmonyOS**：读 [references/harmonyos.md](references/harmonyos.md)。新拟态双层图标、移动端平面 / PC 与 Vision 轻量 3D、穿戴设备单层圆形 152×152。
- **Web**：读 [references/web.md](references/web.md)。manifest 图标（any + maskable 双份）、apple-touch-icon 180×180、favicon 全套与暗色模式。

只做单端时也建议按第 1 步的安全区约束设计，未来扩端零返工。

### 第 3 步：产出与命名

- 产物统一从 1024×1024 母版（SVG 或 PSD/Figma 分层源）缩放导出，不逐尺寸重画。
- 使用 [assets/adaptive-icon.xml](assets/adaptive-icon.xml) 模板快速生成 Android 自适应图标 XML。
- 交付物建议目录结构：

```
icons/
├── android/          # mipmap-anydpi-v26/ic_launcher.xml + 各密度 PNG + 512 商店图
├── ios/              # AppIcon.appiconset（1024 母版 + 变体）/ .icon 文件
├── harmonyos/        # foreground.png + background.png（1024 双层）
└── web/              # favicon.ico / favicon.svg / icon-192.png / icon-512.png / icon-maskable-512.png / apple-touch-icon.png + HTML 头部代码
```

### 第 4 步：QA（交付前必须执行）

运行校验脚本，对所有 PNG 产物做规范性检查：

```bash
python3 scripts/icon_qa.py <文件或目录> [--platform android-fg|ios|harmonyos|web-maskable]
```

检查项：画布尺寸、正方形、透明通道（iOS 平铺图与 HarmonyOS 背景层必须完全不透明）、安全区（Android 前景 66dp 比例、Web maskable 80% 内切圆内不得有被裁切的重要内容）。脚本输出逐项 PASS/FAIL。有 FAIL 不得宣称"已适配"。

## 数值速查（详见各端参考文件）

| 端 | 画布 | 图层 | 交付格式 | 系统蒙版 |
| --- | --- | --- | --- | --- |
| Android 自适应 | 108×108 dp | 前景+背景+单色 | XML + 矢量优先 | OEM 圆形/方圆等 |
| iOS/iPadOS/macOS | 1024×1024 px | 背景层+前景层 | 分层（Icon Composer） | 方形→圆角矩形 |
| watchOS | 1088×1088 px | 分层 | 分层 | 圆形 |
| visionOS | 1024×1024 px | 背景+1~2 前景 | 分层 3D | 圆形 |
| tvOS | 800×480 px | 2~5 层视差 | 分层 | 圆角矩形 |
| HarmonyOS | 1024×1024 px | 双层（穿戴单层 152×152） | PNG | 系统按场景裁切 |
| Web manifest | 192/512 px | 单层平铺 | PNG + maskable 变体 | 浏览器/启动器 |

## 来源与时效

各端参考文件中的规范均标注来源 URL 与核实日期（2026 年）。规范会随系统版本演进，若用户报告与现网行为不符，先用 web_search 复核官方文档，再更新对应参考文件。
