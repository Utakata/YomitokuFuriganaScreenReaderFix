import os
import re

from PIL import Image
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth

import numpy as np
import jaconv

from ..constants import ROOT_DIR

FONT_PATH = ROOT_DIR + "/resource/MPLUS1p-Medium.ttf"


def _poly2rect(points):
    """
    Convert a polygon defined by its corner points to a rectangle.
    The points should be in the format [[x1, y1], [x2, y2], [x3, y3], [x4, y4]].
    """
    points = np.array(points, dtype=int)
    x_min = points[:, 0].min()
    x_max = points[:, 0].max()
    y_min = points[:, 1].min()
    y_max = points[:, 1].max()

    return [x_min, y_min, x_max, y_max]


def _calc_font_size(content, bbox_height, bbox_width):
    rates = np.arange(0.5, 1.0, 0.01)

    min_diff = np.inf
    best_font_size = None
    for rate in rates:
        font_size = bbox_height * rate
        text_w = stringWidth(content, "MPLUS1p-Medium", font_size)
        diff = abs(text_w - bbox_width)
        if diff < min_diff:
            min_diff = diff
            best_font_size = font_size

    return best_font_size


def to_full_width(text):
    fw_map = {
        "\u00a5": "\uffe5",  # ¥ → ￥
        "\u00b7": "\u30fb",  # · → ・
        " ": "\u3000",  # 半角スペース→全角スペース
    }

    TO_FULLWIDTH = str.maketrans(fw_map)

    jaconv_text = jaconv.h2z(text, kana=True, ascii=True, digit=True)
    jaconv_text = jaconv_text.translate(TO_FULLWIDTH)

    return jaconv_text


def _is_kana_only(text):
    """
    Check if text contains only hiragana, katakana, and Japanese punctuation.
    Returns True if the text is likely furigana.
    """
    # Pattern: hiragana, katakana, small kana, Japanese punctuation, whitespace
    kana_pattern = re.compile(r'^[\u3040-\u309F\u30A0-\u30FF\u3001-\u303F\s]+$')
    return bool(kana_pattern.match(text))


def _is_furigana(text, font_size, bbox_height, bbox_width):
    """
    Determine if a text element is furigana based on multiple criteria:
    1. Font size is small (< 8pt)
    2. Text contains only kana characters
    3. Bounding box is small relative to typical text
    
    Args:
        text: The text content
        font_size: Calculated font size
        bbox_height: Height of bounding box
        bbox_width: Width of bounding box
    
    Returns:
        bool: True if the text is likely furigana
    """
    # Criterion 1: Small font size (typical furigana is < 8pt)
    if font_size >= 8:
        return False
    
    # Criterion 2: Must be kana-only
    if not _is_kana_only(text):
        return False
    
    # Criterion 3: Small bounding box (furigana is typically small)
    # For horizontal text, height < 12px; for vertical, width < 12px
    if bbox_height < 12 or bbox_width < 12:
        return True
    
    return False


def create_searchable_pdf(images, ocr_results, output_path, font_path=None):
    if font_path is None:
        font_path = FONT_PATH

    pdfmetrics.registerFont(TTFont("MPLUS1p-Medium", font_path))

    packet = BytesIO()
    c = canvas.Canvas(packet)

    for i, (image, ocr_result) in enumerate(zip(images, ocr_results)):
        image = Image.fromarray(image[:, :, ::-1])  # Convert BGR to RGB
        image_path = f"tmp_{i}.png"
        image.save(image_path)
        w, h = image.size

        c.setPageSize((w, h))
        c.drawImage(image_path, 0, 0, width=w, height=h)
        os.remove(image_path)  # Clean up temporary image file

        for word in ocr_result.words:
            text = word.content
            bbox = _poly2rect(word.points)
            direction = word.direction

            x1, y1, x2, y2 = bbox
            bbox_height = y2 - y1
            bbox_width = x2 - x1

            if direction == "vertical":
                text = to_full_width(text)

            if direction == "horizontal":
                font_size = _calc_font_size(text, bbox_height, bbox_width)
            else:
                font_size = _calc_font_size(text, bbox_width, bbox_height)

            # Skip furigana from the accessible text layer
            # Furigana will remain visible in the image layer but won't be read by screen readers
            if _is_furigana(text, font_size, bbox_height, bbox_width):
                continue

            c.setFont("MPLUS1p-Medium", font_size)
            c.setFillColorRGB(1, 1, 1, alpha=0)  # 透明
            if direction == "vertical":
                base_y = h - y2 + (bbox_height - font_size)
                for j, ch in enumerate(text):
                    c.saveState()
                    c.translate(x1 + font_size * 0.5, base_y - (j - 1) * font_size)
                    c.rotate(-90)
                    c.drawString(0, 0, ch)
                    c.restoreState()
            else:
                base_y = h - y2 + (bbox_height - font_size) * 0.5
                c.drawString(x1, base_y, text)
        c.showPage()
    c.save()

    with open(output_path, "wb") as f:
        f.write(packet.getvalue())
