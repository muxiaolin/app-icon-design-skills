# Web / PWA 图标规范

> 来源：W3C Web App Manifest、MDN、web.dev（maskable-icon / add-manifest）、Apple Safari 配置文档；汇总参考 2026 年 modern favicon complete spec。核实日期：2026-09-11。

## 双事实源结构

Web 图标不是一个文件，是一条管线，两个事实源并存：

1. **Web App Manifest**：Chromium 系可安装 PWA + Android WebAPK。
2. **`<link rel="apple-touch-icon">`**：iOS Safari 至今不读 manifest 的主屏图标，必须单独给。
3. 另有 `/favicon.ico`：所有浏览器无条件探测，RSS 阅读器等抓取器直接打这个 URL。

只出 manifest 图标 → iOS 安装体验破损 + 老浏览器标签页图标模糊。

## 完整文件清单

| 文件 | 尺寸 | 格式 | 用途 |
| --- | --- | --- | --- |
| favicon.ico | 16/32/48 多尺寸合一 | ICO | 老浏览器标签页、书签、抓取器兜底 |
| favicon.svg | 矢量 | SVG | 现代浏览器标签页；可内嵌暗色模式 |
| icon-192.png | 192×192 | PNG | manifest 必备 |
| icon-512.png | 512×512 | PNG | manifest 必备（安装/启动画面） |
| icon-maskable-512.png | 512×512 | PNG | manifest maskable 变体，单独制作 |
| apple-touch-icon.png | **180×180** | PNG | iOS 主屏图标；不透明、方形不预切圆角 |

## Maskable 图标（Android 启动器蒙版）

- `"purpose": "any"` 与 `"purpose": "maskable"` 必须**两份独立图标**。
- maskable 不是把普通图标换个标记：内容要落在**画布 80% 的内切圆**内（外圈约 10% 边界只放纯背景色），否则在 circle / squircle / teardrop 等启动器蒙版下被裁。
- 用 maskable.app 或 icon.kitchen 预览各真实启动器蒙版下的表现。

```json
// manifest.json
{
  "icons": [
    { "src": "/icon-192.png",  "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "/icon-512.png",  "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

## HTML 头部

```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#RRGGBB">
```

- `theme-color` 影响移动浏览器地址栏 / PWA 标题栏着色，与图标背景色对齐。

## 暗色模式

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <style>
    @media (prefers-color-scheme: dark) { .bg { fill: #1a1a1a } .fg { fill: #eee } }
  </style>
  <rect class="bg" width="100" height="100" fill="#fff"/>
  <path class="fg" d="…" fill="#222"/>
</svg>
```

已知限制（截至 2026-04 核实）：
- **Safari（含 17/18/19 全系）忽略 SVG favicon 内的 `prefers-color-scheme`**，WebKit 长期限制，永远渲染默认（浅色）路径。要在 Safari 上实现自适应 favicon，只能用 JS 切换 `<link href>`。
- media query 读的是**操作系统主题**，不是站点主题。
- 改动需刷新页面；浏览器对 favicon 缓存激进。
- `xmlns` 属性必填，否则 Firefox 不渲染为 favicon。
- 用 SVGO 优化时保留 `<style>`（默认 preset 会删；`--disable=removeStyleElement`）。

## apple-touch-icon 细节

- 精确 180×180；**输出 PNG 无 alpha 通道**（不透明）；**直角不预切圆角**（iOS 自己加圆角与高光）。
- iOS 上不用 manifest 图标；可提供多尺寸 link 标签，但 180×180 单张已覆盖绝大多数场景。

## 生产建议

- 从单个 SVG 母版出全套（sharp / ImageMagick / pwa-asset-generator 均可），保证视觉一致。
- 工具参考：RealFaviconGenerator（全平台最全，含 Favicon Checker）、pwa-asset-generator（含 iOS 启动图矩阵）、maskable.app（maskable 安全区校验）、icon.kitchen（启动器蒙版预览）。
