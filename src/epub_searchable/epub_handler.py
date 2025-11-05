"""
EPUB extraction and re-compression module.
Handles ZIP-based EPUB file structure with proper mimetype handling.
"""

import os
import zipfile
import shutil
from pathlib import Path


class EPUBHandler:
    """Handles EPUB file extraction and re-compression."""
    
    def __init__(self, input_epub_path):
        """
        Initialize EPUB handler.
        
        Args:
            input_epub_path: Path to input EPUB file
        """
        self.input_path = Path(input_epub_path)
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input EPUB not found: {input_epub_path}")
        
        self.extract_dir = None
        self.output_dir = None
    
    def extract(self, extract_dir=None):
        """
        Extract EPUB to temporary directory.
        
        Args:
            extract_dir: Directory to extract to (default: creates temp dir)
        
        Returns:
            Path to extraction directory
        """
        if extract_dir is None:
            extract_dir = Path(f"temp_epub_extract_{self.input_path.stem}")
        else:
            extract_dir = Path(extract_dir)
        
        self.extract_dir = extract_dir
        
        # Clean up if exists
        if self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)
        
        self.extract_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract EPUB (it's a ZIP file)
        with zipfile.ZipFile(self.input_path, 'r') as zip_ref:
            zip_ref.extractall(self.extract_dir)
        
        return self.extract_dir
    
    def prepare_output_dir(self, output_dir=None):
        """
        Prepare output directory by copying extracted content.
        
        Args:
            output_dir: Directory for processed files (default: creates temp dir)
        
        Returns:
            Path to output directory
        """
        if self.extract_dir is None:
            raise RuntimeError("Must extract EPUB first")
        
        if output_dir is None:
            output_dir = Path(f"temp_epub_output_{self.input_path.stem}")
        else:
            output_dir = Path(output_dir)
        
        self.output_dir = output_dir
        
        # Clean up if exists
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        
        # Copy all files from extract to output
        shutil.copytree(self.extract_dir, self.output_dir)
        
        return self.output_dir
    
    def compress(self, output_epub_path):
        """
        Compress output directory back to EPUB file.
        
        EPUB specification requires:
        - mimetype file MUST be first and UNCOMPRESSED
        - All other files can be compressed
        
        Args:
            output_epub_path: Path for output EPUB file
        
        Returns:
            Path to created EPUB file
        """
        if self.output_dir is None:
            raise RuntimeError("Must prepare output directory first")
        
        output_path = Path(output_epub_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing file
        if output_path.exists():
            output_path.unlink()
        
        with zipfile.ZipFile(output_path, 'w') as zip_file:
            # Step 1: Add mimetype FIRST and UNCOMPRESSED (EPUB spec requirement)
            mimetype_path = self.output_dir / 'mimetype'
            if mimetype_path.exists():
                zip_file.write(
                    mimetype_path,
                    arcname='mimetype',
                    compress_type=zipfile.ZIP_STORED  # No compression
                )
            
            # Step 2: Add all other files with compression
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if file == 'mimetype':
                        continue  # Already added
                    
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.output_dir)
                    
                    zip_file.write(
                        file_path,
                        arcname=arcname,
                        compress_type=zipfile.ZIP_DEFLATED  # Compressed
                    )
        
        return output_path
    
    def cleanup(self):
        """Remove temporary directories."""
        if self.extract_dir and self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)
        if self.output_dir and self.output_dir.exists():
            shutil.rmtree(self.output_dir)
    
    def find_html_files(self):
        """
        Find all HTML/XHTML files in extracted EPUB.
        
        Returns:
            List of Path objects for .html and .xhtml files
        """
        if self.extract_dir is None:
            raise RuntimeError("Must extract EPUB first")
        
        html_files = []
        for ext in ['*.html', '*.xhtml']:
            html_files.extend(self.extract_dir.rglob(ext))
        
        return sorted(html_files)
    
    def get_output_path(self, relative_path):
        """
        Get corresponding output path for a file.
        
        Args:
            relative_path: Path relative to extract_dir
        
        Returns:
            Absolute path in output_dir
        """
        if self.output_dir is None:
            raise RuntimeError("Must prepare output directory first")
        
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)
        
        # Make relative to extract_dir if absolute
        if relative_path.is_absolute():
            relative_path = relative_path.relative_to(self.extract_dir)
        
        return self.output_dir / relative_path
