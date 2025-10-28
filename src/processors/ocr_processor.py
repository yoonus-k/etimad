"""
OCR Processor Module
Handles optical character recognition for scanned documents and images
"""

import os
from pathlib import Path
from typing import List, Optional
import logging
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRProcessor:
    """Process scanned documents and images with OCR"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR processor
        
        Args:
            tesseract_cmd: Path to tesseract executable (optional)
        """
        self.tesseract_available = self._check_tesseract(tesseract_cmd)
        
        if not self.tesseract_available:
            logger.warning("⚠️ Tesseract OCR not available. Scanned documents cannot be processed.")
    
    def _check_tesseract(self, tesseract_cmd: Optional[str] = None) -> bool:
        """Check if Tesseract OCR is available"""
        try:
            import pytesseract
            
            # Set custom tesseract command if provided
            if tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            elif os.name == 'nt':  # Windows
                # Common Windows installation paths
                possible_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                    r'C:\Tesseract-OCR\tesseract.exe'
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
            
            # Test if tesseract works
            pytesseract.get_tesseract_version()
            logger.info("✅ Tesseract OCR is available")
            return True
        
        except ImportError:
            logger.warning("pytesseract not installed. Install with: pip install pytesseract")
            return False
        except Exception as e:
            logger.warning(f"Tesseract check failed: {e}")
            return False
    
    def process_image(self, image_path: Path, language: str = 'ara+eng') -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file
            language: OCR language(s) - 'ara' for Arabic, 'eng' for English, 'ara+eng' for both
            
        Returns:
            Extracted text
        """
        if not self.tesseract_available:
            logger.error("Tesseract not available")
            return ""
        
        try:
            import pytesseract
            
            # Open image
            image = Image.open(image_path)
            
            # Perform OCR
            logger.info(f"🔍 Running OCR on: {image_path.name}")
            text = pytesseract.image_to_string(image, lang=language)
            
            logger.info(f"✅ Extracted {len(text)} characters from {image_path.name}")
            return text
        
        except Exception as e:
            logger.error(f"❌ OCR failed for {image_path.name}: {e}")
            return ""
    
    def process_scanned_pdf(self, pdf_path: Path, language: str = 'ara+eng') -> str:
        """
        Extract text from scanned PDF using OCR
        
        Args:
            pdf_path: Path to PDF file
            language: OCR language(s)
            
        Returns:
            Extracted text from all pages
        """
        if not self.tesseract_available:
            logger.error("Tesseract not available")
            return ""
        
        try:
            import pytesseract
            from pdf2image import convert_from_path
            
            logger.info(f"🔍 Processing scanned PDF: {pdf_path.name}")
            
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)
            
            text_parts = []
            for page_num, image in enumerate(images, 1):
                logger.info(f"  Processing page {page_num}/{len(images)}")
                page_text = pytesseract.image_to_string(image, lang=language)
                
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")
            
            result = "\n\n".join(text_parts)
            logger.info(f"✅ Extracted {len(result)} characters from {len(images)} pages")
            return result
        
        except ImportError:
            logger.error("pdf2image not installed. Install with: pip install pdf2image")
            logger.error("Also requires poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
            return ""
        
        except Exception as e:
            logger.error(f"❌ OCR failed for PDF {pdf_path.name}: {e}")
            return ""
    
    def process_images_in_folder(self, folder_path: Path, language: str = 'ara+eng') -> List[dict]:
        """
        Process all images in a folder
        
        Args:
            folder_path: Path to folder containing images
            language: OCR language(s)
            
        Returns:
            List of dicts with filename and extracted text
        """
        if not self.tesseract_available:
            logger.error("Tesseract not available")
            return []
        
        results = []
        image_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        
        for ext in image_extensions:
            for image_path in folder_path.glob(f'*{ext}'):
                text = self.process_image(image_path, language)
                if text:
                    results.append({
                        'filename': image_path.name,
                        'content': text,
                        'length': len(text)
                    })
        
        return results
    
    def is_pdf_scanned(self, pdf_path: Path) -> bool:
        """
        Check if PDF is scanned (image-based) or text-based
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if PDF appears to be scanned
        """
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                # Check first few pages
                for page in pdf.pages[:3]:
                    text = page.extract_text()
                    if text and len(text.strip()) > 100:
                        # Has significant text, likely not scanned
                        return False
            
            # Little or no text found, likely scanned
            return True
        
        except Exception as e:
            logger.warning(f"Could not determine if PDF is scanned: {e}")
            # Assume not scanned to avoid unnecessary OCR
            return False
    
    def get_installation_guide(self) -> str:
        """Get installation instructions for Tesseract OCR"""
        if os.name == 'nt':  # Windows
            return """
Tesseract OCR Installation Guide (Windows):

1. Download Tesseract installer:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Run the installer (tesseract-ocr-w64-setup-v5.x.x.exe)

3. During installation, select additional languages:
   - Arabic (ara)
   - English (eng)

4. Default installation path: C:\\Program Files\\Tesseract-OCR\\

5. Verify installation:
   - Open Command Prompt
   - Run: tesseract --version

6. For PDF processing, also install Poppler:
   https://github.com/oschwartz10612/poppler-windows/releases/
   - Download poppler-xx.xx.x-0.zip
   - Extract to C:\\poppler
   - Add C:\\poppler\\Library\\bin to PATH

7. Install Python packages:
   pip install pytesseract pillow pdf2image
"""
        else:  # Linux/Mac
            return """
Tesseract OCR Installation Guide (Linux/Mac):

Linux (Ubuntu/Debian):
  sudo apt-get update
  sudo apt-get install tesseract-ocr
  sudo apt-get install tesseract-ocr-ara  # Arabic
  sudo apt-get install tesseract-ocr-eng  # English
  sudo apt-get install poppler-utils      # For PDF processing

Mac (using Homebrew):
  brew install tesseract
  brew install tesseract-lang  # Includes Arabic
  brew install poppler         # For PDF processing

Install Python packages:
  pip install pytesseract pillow pdf2image

Verify installation:
  tesseract --version
  tesseract --list-langs
"""


if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("OCR Processor Test")
    print("=" * 60)
    
    ocr = OCRProcessor()
    
    if not ocr.tesseract_available:
        print("\n⚠️ Tesseract OCR is not installed\n")
        print(ocr.get_installation_guide())
    else:
        print("\n✅ Tesseract OCR is ready!")
        
        # Test with sample images if any exist
        downloads_path = Path(__file__).parent.parent / 'downloads'
        
        if downloads_path.exists():
            tender_folders = [f for f in downloads_path.iterdir() if f.is_dir()]
            
            if tender_folders:
                test_folder = tender_folders[0]
                print(f"\n📁 Testing with: {test_folder.name}\n")
                
                results = ocr.process_images_in_folder(test_folder)
                
                print(f"📊 Processed {len(results)} images")
                for result in results:
                    print(f"  - {result['filename']}: {result['length']} characters")
                
                if results:
                    print(f"\n📄 Sample OCR text (first 300 chars):")
                    print("-" * 60)
                    print(results[0]['content'][:300])
                    print("-" * 60)
