"""
HTML processing module for adding transparent text layers.
"""

from lxml import etree, html
from pathlib import Path
import re
from .utils import _poly2rect, to_full_width, _calc_font_size, _is_furigana


class HTMLProcessor:
    """Processes HTML files to add transparent text layers from OCR results."""
    
    # XML namespaces commonly used in EPUB
    NAMESPACES = {
        'xhtml': 'http://www.w3.org/1999/xhtml',
        'svg': 'http://www.w3.org/2000/svg',
        'xlink': 'http://www.w3.org/1999/xlink',
        'epub': 'http://www.idpf.org/2007/ops'
    }
    
    def __init__(self, base_dir):
        """
        Initialize HTML processor.
        
        Args:
            base_dir: Base directory for resolving relative image paths
        """
        self.base_dir = Path(base_dir)
    
    def parse_html(self, html_path):
        """
        Parse HTML/XHTML file with namespace support.
        
        Args:
            html_path: Path to HTML file
        
        Returns:
            lxml ElementTree
        """
        html_path = Path(html_path)
        
        try:
            # Try parsing as XML first (for XHTML)
            parser = etree.XMLParser(remove_blank_text=False, recover=True)
            tree = etree.parse(str(html_path), parser)
            return tree
        except etree.XMLSyntaxError:
            # Fall back to HTML parser
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = html.fromstring(content)
            return tree
    
    def find_image_reference(self, tree):
        """
        Find image reference in HTML/XHTML content.
        Supports both <img> tags and <svg><image> tags.
        
        Args:
            tree: lxml ElementTree
        
        Returns:
            Tuple of (image_path_relative, image_width, image_height) or (None, None, None)
        """
        # Try finding <img> tag
        img_elements = tree.xpath('//img | //xhtml:img', namespaces=self.NAMESPACES)
        if img_elements:
            img = img_elements[0]
            src = img.get('src')
            width = img.get('width')
            height = img.get('height')
            return (src, width, height)
        
        # Try finding <svg><image> tag
        image_elements = tree.xpath(
            '//svg:image | //image',
            namespaces=self.NAMESPACES
        )
        if image_elements:
            image = image_elements[0]
            # SVG uses xlink:href or href
            href = image.get('{http://www.w3.org/1999/xlink}href') or image.get('href')
            width = image.get('width')
            height = image.get('height')
            return (href, width, height)
        
        return (None, None, None)
    
    def resolve_image_path(self, html_path, image_ref):
        """
        Resolve relative image path to absolute path.
        
        Args:
            html_path: Path to HTML file
            image_ref: Relative image reference (e.g., "../images/00002.jpeg")
        
        Returns:
            Absolute path to image file
        """
        if image_ref is None:
            return None
        
        html_path = Path(html_path)
        # Resolve relative to HTML file's directory
        image_path = (html_path.parent / image_ref).resolve()
        
        return image_path
    
    def generate_text_layer_html(self, ocr_results, image_width, image_height, image_ref):
        """
        Generate HTML with transparent text layer overlaid on image.
        
        Args:
            ocr_results: OCR results from yomitoku with .words attribute
            image_width: Image width in pixels
            image_height: Image height in pixels
            image_ref: Relative path to image (e.g., "../images/00002.jpeg")
        
        Returns:
            HTML string with layered structure
        """
        # Build HTML structure
        html_parts = []
        html_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html xmlns="http://www.w3.org/1999/xhtml">')
        html_parts.append('<head>')
        html_parts.append('  <meta charset="UTF-8"/>')
        html_parts.append('  <title>Page</title>')
        html_parts.append('  <style>')
        html_parts.append('    body { margin: 0; padding: 0; position: relative; }')
        html_parts.append('    .background-layer { position: absolute; top: 0; left: 0; z-index: 1; }')
        html_parts.append('    .text-layer { position: relative; color: transparent; z-index: 2; }')
        html_parts.append('    .text-layer span { position: absolute; }')
        html_parts.append('  </style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        
        # Background layer: original image
        html_parts.append(f'  <div class="background-layer">')
        html_parts.append(f'    <img src="{image_ref}" width="{image_width}" height="{image_height}" alt="Page image"/>')
        html_parts.append(f'  </div>')
        
        # Text layer: transparent OCR text
        html_parts.append(f'  <div class="text-layer" style="width: {image_width}px; height: {image_height}px;">')
        
        # Add each word as a positioned span
        for word in ocr_results.words:
            text = word.content
            bbox = _poly2rect(word.points)
            direction = word.direction
            
            x1, y1, x2, y2 = bbox
            bbox_height = y2 - y1
            bbox_width = x2 - x1
            
            # Calculate font size
            if direction == "horizontal":
                font_size = _calc_font_size(text, bbox_height, bbox_width)
            else:
                font_size = _calc_font_size(text, bbox_width, bbox_height)
            
            # Skip furigana from accessible text layer
            if _is_furigana(text, font_size, bbox_height, bbox_width):
                continue
            
            # Convert to full-width for vertical text
            if direction == "vertical":
                text = to_full_width(text)
            
            # Build span styles
            styles = [
                f'left: {x1}px',
                f'top: {y1}px',
                f'font-size: {font_size:.2f}px',
                'font-family: sans-serif'
            ]
            
            if direction == "vertical":
                styles.append('writing-mode: vertical-rl')
                styles.append('text-orientation: upright')
            
            style_str = '; '.join(styles)
            
            # Escape HTML entities
            text_escaped = html.escape(text)
            
            html_parts.append(f'    <span style="{style_str}">{text_escaped}</span>')
        
        html_parts.append('  </div>')
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return '\n'.join(html_parts)
    
    def process_html_file(self, html_path, ocr_processor, output_path):
        """
        Process a single HTML file: extract image, run OCR, generate text layer.
        
        Args:
            html_path: Path to input HTML file
            ocr_processor: OCRProcessor instance
            output_path: Path for output HTML file
        
        Returns:
            True if processed successfully, False if skipped
        """
        # Parse HTML
        tree = self.parse_html(html_path)
        
        # Find image reference
        image_ref, width_attr, height_attr = self.find_image_reference(tree)
        
        if image_ref is None:
            # No image found, copy file as-is
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return False
        
        # Resolve image path
        image_path = self.resolve_image_path(html_path, image_ref)
        
        if not image_path or not image_path.exists():
            # Image not found, copy file as-is
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return False
        
        # Get image dimensions
        image_width, image_height = ocr_processor.get_image_dimensions(image_path)
        
        # Run OCR
        ocr_results = ocr_processor.process_image(image_path)
        
        # Generate new HTML with text layer
        new_html = self.generate_text_layer_html(
            ocr_results,
            image_width,
            image_height,
            image_ref
        )
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        
        return True
