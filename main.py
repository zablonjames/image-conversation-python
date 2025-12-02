import os
import logging
from PIL import Image
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_filename = os.path.join(log_dir, f"compression_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger(__name__)

class ImageCompressor:
    def __init__(self, raw_folder="raw", converted_folder="converted", quality=85):
        """
        Initialize the Image Compressor
        
        Args:
            raw_folder: Source folder containing raw images
            converted_folder: Destination folder for compressed images
            quality: JPEG quality (1-100), 85 is a good balance
        """
        self.raw_folder = raw_folder
        self.converted_folder = converted_folder
        self.quality = quality
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        # Create folders if they don't exist
        os.makedirs(self.raw_folder, exist_ok=True)
        os.makedirs(self.converted_folder, exist_ok=True)
        
        logger.info(f"ImageCompressor initialized")
        logger.info(f"Raw folder: {self.raw_folder}")
        logger.info(f"Converted folder: {self.converted_folder}")
        logger.info(f"Quality setting: {self.quality}")
    
    def get_file_size(self, filepath):
        """Get file size in MB"""
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
    
    def compress_image(self, input_path, output_path):
        """
        Compress a single image
        
        Args:
            input_path: Path to the input image
            output_path: Path to save the compressed image
        """
        try:
            # Get original file size
            original_size = self.get_file_size(input_path)
            
            logger.info(f"Processing: {os.path.basename(input_path)}")
            logger.info(f"Original size: {original_size:.2f} MB")
            
            # Open and process image
            with Image.open(input_path) as img:
                # Convert RGBA to RGB if necessary (for JPEG)
                if img.mode in ('RGBA', 'LA', 'P'):
                    logger.info(f"Converting {img.mode} mode to RGB")
                    # Create a white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Get image dimensions
                width, height = img.size
                logger.info(f"Dimensions: {width}x{height}")
                
                # Save with optimization
                img.save(
                    output_path,
                    'JPEG',
                    quality=self.quality,
                    optimize=True,
                    progressive=True
                )
            
            # Get compressed file size
            compressed_size = self.get_file_size(output_path)
            reduction = ((original_size - compressed_size) / original_size) * 100
            
            logger.info(f"Compressed size: {compressed_size:.2f} MB")
            logger.info(f"Size reduction: {reduction:.1f}%")
            logger.info(f"Successfully saved to: {output_path}")
            logger.info("-" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {input_path}: {str(e)}")
            logger.info("-" * 60)
            return False
    
    def compress_all(self):
        """
        Compress all images in the raw folder
        """
        logger.info("=" * 60)
        logger.info("Starting batch compression")
        logger.info("=" * 60)
        
        # Get all image files
        image_files = []
        for file in os.listdir(self.raw_folder):
            if Path(file).suffix.lower() in self.supported_formats:
                image_files.append(file)
        
        if not image_files:
            logger.warning(f"No images found in {self.raw_folder}")
            return
        
        logger.info(f"Found {len(image_files)} images to process")
        
        successful = 0
        failed = 0
        
        for filename in image_files:
            input_path = os.path.join(self.raw_folder, filename)
            # Change extension to .jpg for output
            output_filename = Path(filename).stem + '.jpg'
            output_path = os.path.join(self.converted_folder, output_filename)
            
            if self.compress_image(input_path, output_path):
                successful += 1
            else:
                failed += 1
        
        logger.info("=" * 60)
        logger.info("Batch compression completed")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info("=" * 60)

def main():
    # Create compressor instance
    # You can adjust quality (1-100): 85 is recommended for good balance
    # Higher = better quality but larger file size
    compressor = ImageCompressor(
        raw_folder="raw",
        converted_folder="converted",
        quality=85
    )
    
    # Compress all images
    compressor.compress_all()

if __name__ == "__main__":
    main()
