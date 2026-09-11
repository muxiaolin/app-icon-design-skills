#!/usr/bin/env python3
"""icon_qa.py — 多端应用图标产物 QA 校验。

用法:
  python3 icon_qa.py <png文件或目录> [--platform android-fg|ios|harmonyos|web-maskable|generic]

检查项:
  - 画布为正方形, 尺寸符合平台期望
  - 透明通道:
      ios           → 必须完全不透明 (平铺交付, 无 alpha)
      harmonyos     → 背景层必须不透明 (整图作为背景层检查时)
      android-fg    → 前景层必须含透明区域 (徽标以外为透明)
      generic       → 仅报告
  - 安全区:
      android-fg    → 非透明像素须落在 66dp/108dp 比例 (0.6111) 的中心区域内
      web-maskable  → 非透明"重要内容"(非背景色像素)须落在 80% 内切圆内

仅支持 PNG。依赖: Pillow (PIL)。

退出码: 0 = 全部 PASS; 1 = 存在 FAIL; 2 = 运行错误。
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("错误: 需要 Pillow。安装: pip install pillow", file=sys.stderr)
    sys.exit(2)

# 各平台期望的画布边长 (px)。None = 不校验尺寸, 只校验正方形。
EXPECTED_SIZE = {
    "ios": 1024,          # iOS/iPadOS 母版 (watchOS 1088 需人工确认)
    "harmonyos": 1024,
    "web-maskable": 512,
    "android-fg": None,  # 前景图层尺寸随密度桶变化, 只查安全区比例
    "generic": None,
}


def load_png(path: Path) -> Image.Image:
    img = Image.open(path)
    if img.format != "PNG":
        raise ValueError(f"非 PNG 文件: {path} (实际 {img.format})")
    return img


def check_square_and_size(img: Image.Image, platform: str) -> list[tuple[str, str, str]]:
    """返回 [(结果, 检查项, 说明)]"""
    results = []
    w, h = img.size
    if w == h:
        results.append(("PASS", "正方形", f"{w}x{h}"))
    else:
        results.append(("FAIL", "正方形", f"{w}x{h} 不是正方形"))
    expected = EXPECTED_SIZE.get(platform)
    if expected is not None:
        if w == expected:
            results.append(("PASS", "尺寸", f"{w}px 符合 {platform} 期望 {expected}px"))
        else:
            results.append(("FAIL", "尺寸", f"{w}px 不符合 {platform} 期望 {expected}px"))
    return results


def alpha_extrema(img: Image.Image) -> tuple[int, int]:
    a = img.getchannel("A")
    return a.getextrema()


def check_opacity(img: Image.Image, platform: str) -> list[tuple[str, str, str]]:
    results = []
    if "A" not in img.getbands():
        # 无 alpha 通道 → 天然完全不透明
        results.append(("PASS", "透明通道", "无 alpha 通道 (完全不透明)"))
        return results
    lo, hi = alpha_extrema(img)
    if platform == "ios":
        if lo == 255:
            results.append(("PASS", "透明通道", "iOS 平铺图标完全不透明 (无 alpha)"))
        else:
            results.append(("FAIL", "透明通道", "iOS 平铺图标含透明像素 (min alpha=%d); iOS 不支持 alpha, 需平铺背景" % lo))
    elif platform == "harmonyos":
        if lo == 255:
            results.append(("PASS", "透明通道", "背景层完全不透明 (无透明像素)"))
        else:
            results.append(("FAIL", "透明通道", "HarmonyOS 背景层含透明像素 (min alpha=%d); 圆角/内部透明 padding 均违规" % lo))
    elif platform == "android-fg":
        if hi == 255 and lo < 255:
            results.append(("PASS", "透明通道", "前景层含透明背景 (min alpha=%d)" % lo))
        elif lo == 255:
            results.append(("FAIL", "透明通道", "前景层无透明区域: 整层不透明, 蒙版后无意义; 徽标外必须透明"))
        else:
            results.append(("FAIL", "透明通道", "前景层无完全不透明像素 (max alpha=%d)" % hi))
    else:
        results.append(("INFO", "透明通道", f"alpha 范围 {lo}-{hi} (generic 不判定)"))
    return results


def check_safe_zone(img: Image.Image, platform: str) -> list[tuple[str, str, str]]:
    """安全区检查: 非透明(或非背景色)像素到中心的距离比例。"""
    results = []
    if platform not in ("android-fg", "web-maskable"):
        return results

    if platform == "android-fg":
        # 安全区 = 66/108 ≈ 0.6111 (以较短边为 108dp 基准)
        limit = 66.0 / 108.0
        zone_name = "Android 安全区 (66dp/108dp)"
        # 检查对象: 非透明像素 (alpha > 8)
        mask = img.getchannel("A").point(lambda a: 255 if a > 8 else 0) \
            if "A" in img.getbands() else Image.new("L", img.size, 255)
        max_ratio, worst = _max_radius_ratio(mask, 255)
    else:
        # web maskable: 重要内容须在 80% 内切圆内。背景色像素不算"重要内容"。
        limit = 0.80
        zone_name = "Web maskable 安全区 (80% 内切圆)"
        mask = _content_mask(img)
        max_ratio, worst = _max_radius_ratio(mask, 255)

    if max_ratio is None:
        results.append(("WARN", zone_name,
                        "未检出与四角背景色的差异内容: 若整图为纯背景色则合规, 若内容满幅出血到边角则无法自动判定, 需人工确认"))
        return results
    if max_ratio <= limit:
        results.append(("PASS", zone_name,
                        "内容最远点为画布半边的 %.1f%% (限 %.1f%%)" % (max_ratio * 100, limit * 100)))
    else:
        # 超限 2% 以内给 WARN, 其余 FAIL
        verdict = "WARN" if max_ratio <= limit + 0.02 else "FAIL"
        results.append((verdict, zone_name,
                        "内容最远点为画布半边的 %.1f%% (限 %.1f%%), 超出点约在 (%d, %d)"
                        % (max_ratio * 100, limit * 100, worst[0], worst[1])))
    return results


def _max_radius_ratio(mask: Image.Image, on_value: int) -> tuple[float | None, tuple[int, int] | None]:
    """返回 mask 中开启像素到中心的最大距离 / 半边长, 以及该像素坐标。"""
    w, h = mask.size
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    half = min(w, h) / 2.0
    # 降采样加速: 大图采样到最长边 512
    scale = 1.0
    if max(w, h) > 512:
        scale = 512.0 / max(w, h)
        mask = mask.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.NEAREST)
        w2, h2 = mask.size
        cx, cy = (w2 - 1) / 2.0, (h2 - 1) / 2.0
        half = min(w2, h2) / 2.0
    px = mask.load()
    best, best_xy = 0.0, (0, 0)
    for y in range(mask.size[1]):
        for x in range(mask.size[0]):
            if px[x, y] == on_value:
                d = math.hypot(x - cx, y - cy) / half
                if d > best:
                    best, best_xy = d, (x, y)
    if best == 0.0:
        return None, None
    return best, best_xy


def _content_mask(img: Image.Image) -> Image.Image:
    """把'重要内容'从背景色中分离: 与四角背景色差异 > 24 的像素视为内容。"""
    rgb = img.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    mask = Image.new("L", (w, h), 0)
    mpx = mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > 72:
                mpx[x, y] = 255
    # 叠加 alpha: 透明像素不算内容
    if "A" in img.getbands():
        ap = img.getchannel("A").load()
        for y in range(h):
            for x in range(w):
                if ap[x, y] < 8:
                    mpx[x, y] = 0
    return mask


def check_file(path: Path, platform: str) -> int:
    print(f"\n=== {path.name} [platform={platform}] ===")
    try:
        img = load_png(path)
    except Exception as e:  # noqa: BLE001
        print(f"FAIL 读取: {e}")
        return 1
    results = []
    results += check_square_and_size(img, platform)
    results += check_opacity(img, platform)
    results += check_safe_zone(img, platform)
    fails = 0
    for verdict, item, detail in results:
        print(f"{verdict:<5} {item}: {detail}")
        if verdict == "FAIL":
            fails += 1
    print("=> " + ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="多端应用图标 QA 校验")
    ap.add_argument("target", help="PNG 文件或包含 PNG 的目录")
    ap.add_argument("--platform", default="generic",
                    choices=["android-fg", "ios", "harmonyos", "web-maskable", "generic"],
                    help="校验的平台规范 (default: generic)")
    args = ap.parse_args()

    p = Path(args.target)
    if p.is_dir():
        files = sorted(p.rglob("*.png"))
        if not files:
            print(f"目录中无 PNG: {p}")
            return 2
    elif p.is_file():
        files = [p]
    else:
        print(f"目标不存在: {p}")
        return 2

    total_fail = 0
    for f in files:
        total_fail += check_file(f, args.platform)
    print(f"\n共 {len(files)} 个文件, {total_fail} 个 FAIL")
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
