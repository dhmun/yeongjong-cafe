#!/usr/bin/env python3
"""당근 카페 '영종도 알뜰생활' 마스코트 썸네일 생성기.

베이스 이미지(mascot-base.jpg)에 주제 텍스트를 오버레이해서 1080x1080 PNG 썸네일을 만든다.

사용법:
    python3 make_thumb.py "주제 제목" [부제목] [출력경로]

예:
    python3 make_thumb.py "난임시술비 지원 비교" "국가 110만원 + 인천형 추가" ./thumb.png
"""
import sys
import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_IMG = os.path.join(BASE_DIR, "mascot-base.jpg")
FONT_BOLD = "/home/hatch/.fonts/NotoSansKR-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

SIZE = 1080

# 브랜드 컬러
NAVY = (26, 43, 95)
YELLOW = (255, 200, 40)
WHITE = (255, 255, 255)


def draw_text_with_outline(draw, xy, text, font, fill, outline_fill, outline_width=3):
    x, y = xy
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx * dx + dy * dy <= outline_width * outline_width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_fill)
    draw.text((x, y), text, font=font, fill=fill)


def make_thumbnail(title, subtitle="", output_path="thumb.png"):
    base = Image.open(BASE_IMG).convert("RGB")
    # 비율 유지: 중앙 크롭 후 리사이즈 (늘어나지 않게)
    w, h = base.size
    if w != h:
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        base = base.crop((left, top, left + side, top + side))
    if base.size != (SIZE, SIZE):
        base = base.resize((SIZE, SIZE), Image.LANCZOS)

    # 하단 그라데이션 (텍스트 가독성용)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    grad_h = 420
    for i in range(grad_h):
        alpha = int(190 * (i / grad_h) ** 1.5)
        y = SIZE - grad_h + i
        odraw.line([(0, y), (SIZE, y)], fill=(10, 15, 40, alpha))
    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(base)

    # 상단 브랜드 뱃지
    font_brand = ImageFont.truetype(FONT_BOLD, 44)
    brand = "영종 알뜰정보"
    bb = draw.textbbox((0, 0), brand, font=font_brand)
    bw = bb[2] - bb[0] + 60
    bh = 84
    bx, by = 48, 48
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=42, fill=NAVY)
    draw.text((bx + 30, by + 14), brand, font=font_brand, fill=YELLOW)

    # 하단 주제 텍스트
    font_title = ImageFont.truetype(FONT_BOLD, 88)
    font_sub = ImageFont.truetype(FONT_REGULAR, 48)

    # 제목 자동 줄바꿈 (한 줄 최대 12자)
    lines = []
    cur = ""
    for ch in title:
        cur += ch
        if len(cur) >= 12:
            lines.append(cur)
            cur = ""
    if cur:
        lines.append(cur)
    lines = lines[:2]  # 최대 2줄

    y_cursor = SIZE - 120 - len(lines) * 110
    if subtitle:
        y_cursor -= 80
    # backing band behind title+subtitle for contrast
    band_top = y_cursor - 28
    band_bottom = SIZE - 40
    band = Image.new("RGBA", base.size, (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(band)
    bdraw.rounded_rectangle([48, band_top, SIZE - 48, band_bottom], radius=28, fill=(10, 15, 40, 140))
    base = Image.alpha_composite(base.convert("RGBA"), band).convert("RGB")
    draw = ImageDraw.Draw(base)

    for line in lines:
        tb = draw.textbbox((0, 0), line, font=font_title)
        tw = tb[2] - tb[0]
        x = (SIZE - tw) // 2
        draw_text_with_outline(draw, (x, y_cursor), line, font_title, WHITE, NAVY, 6)
        y_cursor += 110

    if subtitle:
        sb = draw.textbbox((0, 0), subtitle, font=font_sub)
        sw = sb[2] - sb[0]
        x = (SIZE - sw) // 2
        draw_text_with_outline(draw, (x, y_cursor + 10), subtitle, font_sub, YELLOW, NAVY, 4)

    base.save(output_path, "PNG")
    print(f"saved: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    title = sys.argv[1]
    subtitle = sys.argv[2] if len(sys.argv) > 2 else ""
    out = sys.argv[3] if len(sys.argv) > 3 else "thumb.png"
    make_thumbnail(title, subtitle, out)
