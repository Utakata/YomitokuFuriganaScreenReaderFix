"""
Test script for improved yomitoku searchable_pdf with furigana filtering
"""
import sys
sys.path.insert(0, 'yomitoku_repo/src')

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from yomitoku.utils.searchable_pdf import create_searchable_pdf
from yomitoku.schemas import OCRSchema, WordPrediction


def create_test_image():
    """Create a test image with Japanese text and furigana"""
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some sample text (representing original document)
    draw.rectangle([50, 50, 750, 350], outline='lightgray', width=2)
    draw.text((100, 100), "完璧", fill='black')
    draw.text((100, 80), "かんぺき", fill='black')  # Furigana above
    draw.text((100, 200), "本文テキスト", fill='black')
    draw.text((100, 180), "ほんぶん", fill='black')  # Furigana above
    
    # Convert to numpy array (BGR format like cv2)
    return np.array(img)[:, :, ::-1]


def create_mock_ocr_results():
    """Create mock OCR results with both furigana and base text"""
    
    # Furigana: small font, kana-only, small bounding box
    furigana1 = WordPrediction(
        points=[[100, 80], [180, 80], [180, 95], [100, 95]],
        content="かんぺき",
        direction="horizontal",
        det_score=0.99,
        rec_score=0.98
    )
    
    # Base text: larger font, contains kanji
    base_text1 = WordPrediction(
        points=[[100, 100], [180, 100], [180, 130], [100, 130]],
        content="完璧",
        direction="horizontal",
        det_score=0.99,
        rec_score=0.98
    )
    
    # Another furigana
    furigana2 = WordPrediction(
        points=[[100, 180], [160, 180], [160, 195], [100, 195]],
        content="ほんぶん",
        direction="horizontal",
        det_score=0.99,
        rec_score=0.98
    )
    
    # Another base text
    base_text2 = WordPrediction(
        points=[[100, 200], [220, 200], [220, 230], [100, 230]],
        content="本文テキスト",
        direction="horizontal",
        det_score=0.99,
        rec_score=0.98
    )
    
    words = [furigana1, base_text1, furigana2, base_text2]
    return OCRSchema(words=words)


def main():
    print("🧪 Testing improved yomitoku searchable_pdf with furigana filtering...\n")
    
    # Create test image and OCR results
    print("Creating test image...")
    test_image = create_test_image()
    
    print("Creating mock OCR results...")
    ocr_result = create_mock_ocr_results()
    
    print(f"  Total OCR words: {len(ocr_result.words)}")
    for i, word in enumerate(ocr_result.words):
        bbox = word.points
        height = abs(bbox[2][1] - bbox[0][1])
        width = abs(bbox[1][0] - bbox[0][0])
        print(f"    Word {i+1}: '{word.content}' (bbox: {width}x{height}px)")
    
    # Generate PDF
    output_path = "output/test_furigana_filtered.pdf"
    print(f"\n📄 Generating searchable PDF: {output_path}")
    
    create_searchable_pdf(
        images=[test_image],
        ocr_results=[ocr_result],
        output_path=output_path
    )
    
    print("\n✅ PDF generation complete!")
    print("\n📋 Expected behavior:")
    print("  ✓ Visual layer: All text visible (furigana + base text)")
    print("  ✓ Screen reader layer: Only base text ('完璧', '本文テキスト')")
    print("  ✗ Screen reader layer: Furigana excluded ('かんぺき', 'ほんぶん')")
    print(f"\n💾 Test PDF saved to: {output_path}")
    print("\n🔍 To test with a screen reader:")
    print("  1. Download the PDF")
    print("  2. Open with a PDF reader")
    print("  3. Use a screen reader (NVDA, JAWS, VoiceOver, etc.)")
    print("  4. Verify it reads only base text, not furigana")


if __name__ == "__main__":
    main()
