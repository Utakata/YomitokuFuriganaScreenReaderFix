import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont
import io
from typing import List, Dict
import os


class ScreenReaderPDFGenerator:
    def __init__(self):
        self.page_width = A4[0]
        self.page_height = A4[1]
        
    def generate_searchable_pdf(self, image_path: str, text_structure: List[Dict], output_path: str) -> str:
        doc = fitz.open()
        
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        aspect_ratio = img_width / img_height
        page_aspect_ratio = self.page_width / self.page_height
        
        if aspect_ratio > page_aspect_ratio:
            scaled_width = self.page_width
            scaled_height = self.page_width / aspect_ratio
        else:
            scaled_height = self.page_height
            scaled_width = self.page_height * aspect_ratio
        
        page = doc.new_page(width=self.page_width, height=self.page_height)
        
        x_offset = (self.page_width - scaled_width) / 2
        y_offset = (self.page_height - scaled_height) / 2
        
        rect = fitz.Rect(x_offset, y_offset, x_offset + scaled_width, y_offset + scaled_height)
        page.insert_image(rect, filename=image_path)
        
        scale_x = scaled_width / img_width
        scale_y = scaled_height / img_height
        
        for block in text_structure:
            text = block.get('text', '')
            if not text:
                continue
            
            x = x_offset + block.get('x', 0) * scale_x
            y = y_offset + block.get('y', 0) * scale_y
            width = block.get('width', 0) * scale_x
            height = block.get('height', 0) * scale_y
            
            has_furigana = block.get('has_furigana', False)
            
            text_to_render = text
            
            text_rect = fitz.Rect(x, y, x + width, y + height)
            
            font_size = max(1, block.get('font_size', 12) * min(scale_x, scale_y))
            
            try:
                page.insert_textbox(
                    text_rect,
                    text_to_render,
                    fontsize=font_size,
                    color=(0, 0, 0),
                    fill_opacity=0,
                    stroke_opacity=0,
                    render_mode=3
                )
            except Exception as e:
                print(f"テキスト挿入エラー: {e}")
                continue
        
        doc.save(output_path)
        doc.close()
        
        return output_path
    
    def create_test_pdf_with_demo(self, output_path: str) -> str:
        doc = fitz.open()
        page = doc.new_page(width=A4[0], height=A4[1])
        
        demo_structures = [
            {
                'text': '完璧',
                'reading': 'かんぺき',
                'x': 100,
                'y': 100,
                'has_furigana': True
            },
            {
                'text': 'この文書はスクリーンリーダー最適化PDFです',
                'reading': None,
                'x': 100,
                'y': 150,
                'has_furigana': False
            },
            {
                'text': '素晴',
                'reading': 'すば',
                'x': 100,
                'y': 200,
                'has_furigana': True
            },
            {
                'text': 'らしい',
                'reading': None,
                'x': 150,
                'y': 200,
                'has_furigana': False
            }
        ]
        
        for block in demo_structures:
            text = block['text']
            reading = block.get('reading')
            x = block['x']
            y = block['y']
            has_furigana = block.get('has_furigana', False)
            
            if has_furigana and reading:
                img_width = 150
                img_height = 30
                img = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)
                
                try:
                    import subprocess
                    result = subprocess.run(['fc-match', '-f', '%{file}', 'Noto Sans CJK JP'], 
                                          capture_output=True, text=True, timeout=5)
                    font_path = result.stdout.strip()
                    font_small = ImageFont.truetype(font_path, 8, index=0)
                    font_base = ImageFont.truetype(font_path, 16, index=0)
                except:
                    try:
                        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
                        font_base = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                    except:
                        font_small = ImageFont.load_default()
                        font_base = ImageFont.load_default()
                
                draw.text((5, 0), reading, fill=(0, 0, 0, 255), font=font_small)
                draw.text((5, 12), text, fill=(0, 0, 0, 255), font=font_base)
                
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                img_rect = fitz.Rect(x, y - 10, x + img_width, y + img_height - 10)
                page.insert_image(img_rect, stream=img_bytes.getvalue())
                
                invisible_rect = fitz.Rect(x, y, x + 100, y + 20)
                page.insert_textbox(
                    invisible_rect,
                    text,
                    fontsize=12,
                    color=(0, 0, 0),
                    fill_opacity=0,
                    stroke_opacity=0,
                    render_mode=3
                )
            else:
                img_width = 400
                img_height = 20
                img = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)
                
                try:
                    import subprocess
                    result = subprocess.run(['fc-match', '-f', '%{file}', 'Noto Sans CJK JP'], 
                                          capture_output=True, text=True, timeout=5)
                    font_path = result.stdout.strip()
                    font_base = ImageFont.truetype(font_path, 16, index=0)
                except:
                    try:
                        font_base = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                    except:
                        font_base = ImageFont.load_default()
                
                draw.text((5, 0), text, fill=(0, 0, 0, 255), font=font_base)
                
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                img_rect = fitz.Rect(x, y, x + img_width, y + img_height)
                page.insert_image(img_rect, stream=img_bytes.getvalue())
                
                invisible_rect = fitz.Rect(x, y, x + 400, y + 20)
                page.insert_textbox(
                    invisible_rect,
                    text,
                    fontsize=12,
                    color=(0, 0, 0),
                    fill_opacity=0,
                    stroke_opacity=0,
                    render_mode=3
                )
        
        doc.save(output_path)
        doc.close()
        
        return output_path
