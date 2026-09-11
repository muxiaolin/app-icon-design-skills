# Android 图标规范

> 来源：developer.android.com 自适应图标设计指南（最后更新 2026-08-09）与 Google Codelabs "Design and preview your app icons"（2026-04-24）。核实日期：2026-09-11。

## 自适应图标（Adaptive Icon，API 26+）

三层结构，每层均为 **108×108 dp**：

| 图层 | 内容 | 要求 |
| --- | --- | --- |
| `<background>` | 背景（纯色 / 纹理 / 图形） | 覆盖整个 108dp，允许出血 |
| `<foreground>` | 前景徽标 | 主体落在安全区内 |
| `<monochrome>` | 单色层（可选但强烈建议） | 透明背景 + 单色徽标剪影 |

关键数值：
- 系统蒙版视口：72×72 dp（108dp 中央区域）。
- **安全区：66×66 dp**——任何 OEM 形状蒙版都不会裁到的区域；徽标至少 48×48 dp、不超过 66×66 dp。
- 四边各 18dp 外圈预留给蒙版裁切和视差/脉动等启动器视觉效果。
- 使用边缘清晰的图形；图层不得自带轮廓蒙版或投影阴影（与系统阴影混淆）。

## 主题图标（Material You / Themed Icons）

- Android 13（API 33）起用户可开启主题图标：系统用壁纸取色为图标着色，前提是提供了 `monochrome` 图层。
- Android 16 QPR 2 起，系统会为未提供 monochrome 的应用自动生成主题图标，但自动版是色块剪影，品牌辨识度差——主动提供 monochrome 层仍为最佳实践。
- monochrome 制作要点：必须是透明背景；不能拿前景 PNG 直接复用（不透明白底着色后变成实心色块）。可用亮度阈值从前景反推 alpha：`alpha = min(原alpha, clip((220-luma)×8, 0, 255))`，RGB 值随意（系统运行时重新着色）。
- 同一 monochrome 可复用作通知图标，但多应用建议用不同形状区分（仅靠颜色区分不可及）。

## 资源落盘

```xml
<!-- res/mipmap-anydpi-v26/ic_launcher.xml -->
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
  <background android:drawable="@drawable/ic_launcher_background" />
  <foreground android:drawable="@drawable/ic_launcher_foreground" />
  <monochrome android:drawable="@drawable/ic_launcher_monochrome" />
</adaptive-icon>
```

- 清单：`android:icon="@mipmap/ic_launcher"`；圆形背景为主的图标可加 `android:roundIcon`。
- 位图密度桶：mdpi(1x) / hdpi(1.5x) / xhdpi(2x) / xxhdpi(3x) / xxxhdpi(4x)，以 mdpi 为基线。
- 首选矢量（VectorDrawable / SVG 源），位图仅作降级。

## Google Play 商店

- 商店列表图：**512×512 px PNG**，32 位 PNG（含 alpha），不满 bleed 圆角——方形。

## 设计要点（官方最佳实践）

- 保持简单：避免多层、复杂效果、文字；小尺寸下全部丢失。
- 复杂 logo 做简化版；用用户可联想的符号。
- 前景与背景保持可读对比；避免厚重投影（与系统阴影混淆）。
- 用 keyline 网格控制前景裁切表现。
- 官方 Figma 模板：Android App Icons Figma template（Codelabs 内链接）。
