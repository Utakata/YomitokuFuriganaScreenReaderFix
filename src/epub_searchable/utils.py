"""
Utility functions for searchable EPUB generation.
Adapted from yomitoku's searchable_pdf.py logic.
"""

import re
import numpy as np
import jaconv
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth


def _poly2rect(points):
    """
    Convert a polygon defined by its corner points to a rectangle.
    The points should be in the format [[x1, y1], [x2, y2], [x3, y3], [x4, y4]].
    
    Returns:
        [x_min, y_min, x_max, y_max]
    """
    points = np.array(points, dtype=int)
    x_min = points[:, 0].min()
    x_max = points[:, 0].max()
    y_min = points[:, 1].min()
    y_max = points[:, 1].max()

    return [x_min, y_min, x_max, y_max]


def _calc_font_size(content, bbox_height, bbox_width, font_name="MPLUS1p-Medium"):
    """
    Calculate optimal font size to fit text within bounding box.
    Uses reportlab's stringWidth for accurate calculation.
    
    Args:
        content: Text content
        bbox_height: Height of bounding box
        bbox_width: Width of bounding box
        font_name: Font family name (must be registered with reportlab)
    
    Returns:
        Best fitting font size in points
    """
    rates = np.arange(0.5, 1.0, 0.01)

    min_diff = np.inf
    best_font_size = None
    for rate in rates:
        font_size = bbox_height * rate
        text_w = stringWidth(content, font_name, font_size)
        diff = abs(text_w - bbox_width)
        if diff < min_diff:
            min_diff = diff
            best_font_size = font_size

    return best_font_size


def to_full_width(text):
    """
    Convert half-width characters to full-width for vertical text.
    Essential for proper vertical Japanese text rendering.
    
    Args:
        text: Input text
    
    Returns:
        Full-width converted text
    """
    fw_map = {
        "\u00a5": "\uffe5",  # ¥ → ￥
        "\u00b7": "\u30fb",  # · → ・
        " ": "\u3000",  # half-width space → full-width space
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


def register_font(font_path):
    """
    Register a TrueType font with reportlab for font size calculations.
    
    Args:
        font_path: Path to .ttf font file
    
    Returns:
        Font name that was registered
    """
    font_name = "MPLUS1p-Medium"
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        return font_name
    except Exception as e:
        raise RuntimeError(f"Failed to register font {font_path}: {e}")
