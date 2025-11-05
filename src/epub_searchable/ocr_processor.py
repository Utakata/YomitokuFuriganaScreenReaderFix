"""
OCR processing module using yomitoku DocumentAnalyzer.
"""

from PIL import Image
from pathlib import Path


class OCRProcessor:
    """Handles OCR processing using yomitoku."""
    
    def __init__(self, font_path=None):
        """
        Initialize OCR processor with yomitoku DocumentAnalyzer.
        
        Args:
            font_path: Path to font file for font size calculations (optional)
        """
        try:
            from yomitoku import DocumentAnalyzer
        except ImportError:
            raise ImportError(
                "yomitoku is not installed. Install it with: pip install yomitoku"
            )
        
        # Initialize DocumentAnalyzer
        # Note: yomitoku will use CPU by default if CUDA is not available
        self.analyzer = DocumentAnalyzer()
        self.font_path = font_path
        
        # Register font if provided
        if font_path:
            from .utils import register_font
            register_font(font_path)
    
    def process_image(self, image_path):
        """
        Process image with OCR and return text elements with coordinates.
        
        Args:
            image_path: Path to image file
        
        Returns:
            OCR results object with .words attribute
            Each word has: .content (text), .points (coordinates), .direction (vertical/horizontal)
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        image = Image.open(image_path)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Run OCR with yomitoku
        results = self.analyzer(image)
        
        return results
    
    def get_image_dimensions(self, image_path):
        """
        Get image dimensions.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Tuple of (width, height)
        """
        image = Image.open(image_path)
        return image.size
