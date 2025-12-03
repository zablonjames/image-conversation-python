import os
import logging
from PIL import Image
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_filename = os.path.join(log_dir, f"png_conversion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger(__name__)

class ImageToPNGConverter:
    def __init__(self, raw_folder="raw", converted_folder="converted"):
        """
        Initialize the Image to PNG Converter
        
        Args:
            raw_folder: Source folder containing raw images
            converted_folder: Destination folder for converted PNG images
        """
        self.raw_folder = raw_folder
        self.converted_folder = converted_folder
        self.supported_formats = {'.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp', '.gif', '.ico', '.png'}
        
        # Create folders if they don't exist
        os.makedirs(self.raw_folder, exist_ok=True)
        os.makedirs(self.converted_folder, exist_ok=True)
        
        logger.info(f"ImageToPNGConverter initialized")
        logger.info(f"Raw folder: {self.raw_folder}")
        logger.info(f"Converted folder: {self.converted_folder}")
    
    def get_file_size(self, filepath):
        """Get file size in MB"""
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
    
    def convert_to_png(self, input_path, output_path):
        """
        Convert a single image to PNG format
        
        Args:
            input_path: Path to the input image
            output_path: Path to save the PNG image
        """
        try:
            # Get original file info
            original_size = self.get_file_size(input_path)
            original_format = Path(input_path).suffix.lower()
            
            logger.info(f"Processing: {os.path.basename(input_path)}")
            logger.info(f"Original format: {original_format}")
            logger.info(f"Original size: {original_size:.2f} MB")
            
            # Open and process image
            with Image.open(input_path) as img:
                # Get image info
                width, height = img.size
                mode = img.mode
                logger.info(f"Dimensions: {width}x{height}")
                logger.info(f"Color mode: {mode}")
                
                # Convert palette mode to RGBA to preserve transparency
                if mode == 'P':
                    logger.info("Converting palette mode to RGBA")
                    img = img.convert('RGBA')
                
                # For images without alpha channel, convert to RGBA for consistency
                elif mode in ('RGB', 'L', '1'):
                    logger.info(f"Converting {mode} to RGBA")
                    img = img.convert('RGBA')
                
                # Save as PNG with optimization
                img.save(
                    output_path,
                    'PNG',
                    optimize=True,
                    compress_level=9  # Maximum compression (0-9)
                )
            
            # Get converted file size
            converted_size = self.get_file_size(output_path)
            size_change = converted_size - original_size
            
            logger.info(f"Converted size: {converted_size:.2f} MB")
            if size_change > 0:
                logger.info(f"Size increase: +{size_change:.2f} MB ({((size_change/original_size)*100):.1f}%)")
            else:
                logger.info(f"Size decrease: {size_change:.2f} MB ({((abs(size_change)/original_size)*100):.1f}%)")
            
            logger.info(f"Successfully saved to: {output_path}")
            logger.info("-" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {input_path}: {str(e)}")
            logger.info("-" * 60)
            return False
    
    def convert_all(self):
        """
        Convert all images in the raw folder to PNG
        """
        logger.info("=" * 60)
        logger.info("Starting batch PNG conversion")
        logger.info("=" * 60)
        
        # Get all image files
        image_files = []
        png_files = []
        
        for file in os.listdir(self.raw_folder):
            file_ext = Path(file).suffix.lower()
            if file_ext in self.supported_formats:
                if file_ext == '.png':
                    png_files.append(file)
                else:
                    image_files.append(file)
        
        total_files = len(image_files) + len(png_files)
        
        if total_files == 0:
            logger.warning(f"No images found in {self.raw_folder}")
            return
        
        logger.info(f"Found {total_files} image(s)")
        logger.info(f"- Already PNG: {len(png_files)}")
        logger.info(f"- To convert: {len(image_files)}")
        
        successful = 0
        failed = 0
        skipped = 0
        
        # Handle files that are already PNG
        if png_files:
            logger.info("\nHandling PNG files:")
            for filename in png_files:
                input_path = os.path.join(self.raw_folder, filename)
                output_path = os.path.join(self.converted_folder, filename)
                
                try:
                    # Copy PNG as-is or re-optimize it
                    original_size = self.get_file_size(input_path)
                    logger.info(f"Copying (already PNG): {filename}")
                    logger.info(f"Original size: {original_size:.2f} MB")
                    
                    with Image.open(input_path) as img:
                        width, height = img.size
                        logger.info(f"Dimensions: {width}x{height}")
                        # Re-save with optimization
                        img.save(output_path, 'PNG', optimize=True, compress_level=9)
                    
                    converted_size = self.get_file_size(output_path)
                    logger.info(f"Optimized size: {converted_size:.2f} MB")
                    logger.info(f"Successfully saved to: {output_path}")
                    logger.info("-" * 60)
                    skipped += 1
                except Exception as e:
                    logger.error(f"Error handling {filename}: {str(e)}")
                    logger.info("-" * 60)
                    failed += 1
        
        # Convert non-PNG files
        if image_files:
            logger.info("\nConverting non-PNG files:")
            for filename in image_files:
                input_path = os.path.join(self.raw_folder, filename)
                # Change extension to .png
                output_filename = Path(filename).stem + '.png'
                output_path = os.path.join(self.converted_folder, output_filename)
                
                if self.convert_to_png(input_path, output_path):
                    successful += 1
                else:
                    failed += 1
        
        logger.info("=" * 60)
        logger.info("Batch PNG conversion completed")
        logger.info(f"Successfully converted: {successful}")
        logger.info(f"Already PNG (optimized): {skipped}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total processed: {successful + skipped + failed}")
        logger.info("=" * 60)

def main():
    # Create converter instance
    converter = ImageToPNGConverter(
        raw_folder="raw",
        converted_folder="converted"
    )
    
    # Convert all images to PNG
    converter.convert_all()

if __name__ == "__main__":
    main()
