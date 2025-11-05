"""
Main script for converting image-based EPUB to searchable EPUB.
"""

import sys
from pathlib import Path
from .epub_handler import EPUBHandler
from .ocr_processor import OCRProcessor
from .html_processor import HTMLProcessor


def convert_epub_to_searchable(input_epub, output_epub, font_path=None):
    """
    Convert image-based EPUB to searchable EPUB with transparent text layer.
    
    Args:
        input_epub: Path to input EPUB file
        output_epub: Path to output EPUB file
        font_path: Path to font file for font size calculations (optional)
    
    Returns:
        Path to output EPUB file
    """
    print(f"Converting EPUB: {input_epub} → {output_epub}")
    
    # Initialize handlers
    epub_handler = EPUBHandler(input_epub)
    ocr_processor = OCRProcessor(font_path=font_path)
    
    try:
        # Step 1: Extract EPUB
        print("Extracting EPUB...")
        extract_dir = epub_handler.extract()
        print(f"  Extracted to: {extract_dir}")
        
        # Step 2: Prepare output directory
        print("Preparing output directory...")
        output_dir = epub_handler.prepare_output_dir()
        
        # Step 3: Find HTML files
        print("Finding HTML files...")
        html_files = epub_handler.find_html_files()
        print(f"  Found {len(html_files)} HTML files")
        
        # Step 4: Process each HTML file
        html_processor = HTMLProcessor(extract_dir)
        processed_count = 0
        
        for i, html_file in enumerate(html_files, 1):
            print(f"\nProcessing [{i}/{len(html_files)}]: {html_file.name}")
            
            # Get relative path
            rel_path = html_file.relative_to(extract_dir)
            output_path = epub_handler.get_output_path(rel_path)
            
            # Process HTML file
            success = html_processor.process_html_file(
                html_file,
                ocr_processor,
                output_path
            )
            
            if success:
                print(f"  ✓ Added text layer")
                processed_count += 1
            else:
                print(f"  - Skipped (no image found)")
        
        print(f"\nProcessed {processed_count}/{len(html_files)} files with OCR")
        
        # Step 5: Compress back to EPUB
        print("\nCompressing to EPUB...")
        output_path = epub_handler.compress(output_epub)
        print(f"  Created: {output_path}")
        
        return output_path
    
    finally:
        # Step 6: Cleanup temporary directories
        print("\nCleaning up...")
        epub_handler.cleanup()
        print("Done!")


def main():
    """Command-line interface."""
    if len(sys.argv) < 3:
        print("Usage: python -m src.epub_searchable.main <input.epub> <output.epub> [font.ttf]")
        sys.exit(1)
    
    input_epub = sys.argv[1]
    output_epub = sys.argv[2]
    font_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    convert_epub_to_searchable(input_epub, output_epub, font_path)


if __name__ == "__main__":
    main()
