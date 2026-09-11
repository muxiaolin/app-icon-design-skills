# iOS / Apple 平台图标规范

> 来源：Apple Human Interface Guidelines — App Icons（Change log 最新条目 2026-06-08，Liquid Glass 细化版）。核实日期：2026-09-11。

## 核心变化：分层图标 + Liquid Glass（2025 WWDC 起）

- iOS / iPadOS / macOS / watchOS 图标由**背景层 + 一个或多个前景层**组成，系统叠加 Liquid Glass 属性（镜面高光、折射、半透明）。
- 用 Icon Composer（Xcode 内置 / developer.apple.com/icon-composer）导入前景层、定义背景（纯色/渐变即可，多数情况无需导入背景图）、配置高光与折射、标注变体、跨系统版本预览，导出给 Xcode。
- 前景层**边缘清晰**（不要羽化/软边），系统画的高光阴影才好看。
- 前景层可变透明度增加纵深与生命感（Photos 图标即把核心件拆成多层半透明）。
- 背景若用渐变，须对系统光照效果表现良好；导入背景图必须 full-bleed 且不透明。
- 图层导入首选矢量（SVG/PDF），文字转曲；网格渐变与位图用 PNG（无损）。

## 形状与蒙版（不要自己切圆角）

| 平台 | 布局形状 | 蒙版后形状 | 尺寸 |
| --- | --- | --- | --- |
| iOS / iPadOS / macOS | 方形 | 圆角矩形（曲率匹配系统元素与设备边框） | 1024×1024 px |
| tvOS | 横向矩形 | 圆角矩形 | 800×480 px，2~5 层视差 |
| visionOS | 方形 | 圆形 | 1024×1024 px，背景+1~2 层 3D |
| watchOS | 方形 | 圆形 | 1088×1088 px |

- 提供未蒙版的方形/矩形图层，预切圆角会让镜面高光受损、边缘锯齿。
- 主内容居中，避免系统调角/蒙版时被裁（visionOS、watchOS 尤其注意）。用 Apple Design Resources 的网格模板定位。
- visionOS：背景层不要做"洞/凹陷"形状（系统阴影会让它凸出来）。watchOS：避免纯黑背景（与表盘背景融化）。
- tvOS：安全区随尺寸/层深/动效变化，系统对前景层裁切多于背景层；文字层放最上层。

## 外观变体（iOS 18+ 主屏幕）

用户可选 Default / Dark / Clear / Tinted。可自备变体，未提供的由系统自动生成。

- 各变体保持核心视觉特征一致，不要换元素（用户换外观后要能认出 app）。
- 深色变体以浅色图标为基础选互补色，避免过亮；彩色背景在深色下对比最好。
- Clear / Tinted 更收敛，设计要可见、可读、可辨。
- 备选图标（alternate icons）也需要自备 dark/clear/tinted 变体，全部过 App Review。

## 视觉效果与设计原则

- 系统动态处理模糊等效果——不要自加镜面高光、层间投影、倒角、发光；自定义效果须有意为之并在 Icon Composer / 真机验证。
- 简洁至上：小尺寸下细节丢失，用最少的形状表达核心概念；纯色/渐变背景，不必填满画布。
- 跨平台视觉一致，避免被当成多个 app。
- 前景可用填充的叠压形状 + 透明度/模糊制造纵深。
- 文字仅在品牌必需时使用；不复制 UI 组件、不用截图、不仿 Apple 硬件。
- 偏插画不偏照片；避免极细线宽与尖锐转角（小尺寸低分辨率下失真）。
- 多个图层可编组，Icon Composer 支持组级 Liquid Glass 定制。

## 色彩空间

支持 sRGB（彩色）、Gray Gamma 2.2（灰度）、Display P3（广色域，iOS/iPadOS/macOS/tvOS/watchOS）。

## 交付

- Xcode asset catalog（`AppIcon.appiconset`）；分层图标经 Icon Composer 导出 `.icon` 文件。
- 平铺单图（旧方式）仍可用，但失去分层效果控制。
- 系统自动缩放出 Settings、通知等小尺寸变体。
