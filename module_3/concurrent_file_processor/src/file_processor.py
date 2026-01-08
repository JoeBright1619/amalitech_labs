"""
File processor module - handles CPU-bound processing tasks.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image
from .utils import setup_logger

logger = setup_logger(__name__)


def process_image(
    file_path: Path, output_dir: Path, target_size: Tuple[int, int] = (800, 600)
) -> Optional[Path]:
    """
    Process an image: resize and convert to grayscale.

    Args:
        file_path: Path to input image
        output_dir: Directory to save processed image
        target_size: Target dimensions (width, height)

    Returns:
        Path to processed image, or None if processing failed
    """
    try:
        logger.info(f"Processing image {file_path}")

        # Open and process image
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize
            img_resized = img.resize(target_size, Image.Resampling.LANCZOS)

            # Convert to grayscale
            img_gray = img_resized.convert("L")

            # Save processed image
            output_path = output_dir / f"processed_{file_path.name}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img_gray.save(output_path)

            logger.info(f"Processed image saved to {output_path}")
            return output_path

    except Exception as e:
        logger.error(f"Failed to process image {file_path}: {e}")
        return None


def process_text(file_path: Path, output_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Process a text file: perform basic analysis.

    Args:
        file_path: Path to input text file
        output_dir: Directory to save analysis results

    Returns:
        Dictionary with analysis results, or None if processing failed
    """
    try:
        logger.info(f"Processing text file {file_path}")

        # Read file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Perform analysis
        words = content.split()
        lines = content.split("\n")

        analysis = {
            "file": file_path.name,
            "total_chars": len(content),
            "total_words": len(words),
            "total_lines": len(lines),
            "unique_words": len(set(word.lower() for word in words)),
            "avg_word_length": (
                sum(len(word) for word in words) / len(words) if words else 0
            ),
        }

        # Save analysis
        output_path = output_dir / f"analysis_{file_path.stem}.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for key, value in analysis.items():
                f.write(f"{key}: {value}\n")

        logger.info(f"Text analysis saved to {output_path}")
        return analysis

    except Exception as e:
        logger.error(f"Failed to process text file {file_path}: {e}")
        return None


def process_files_sequential(files: List[Path], output_dir: Path) -> Dict[str, List]:
    """
    Process multiple files sequentially.

    Args:
        files: List of file paths to process
        output_dir: Directory to save processed files

    Returns:
        Dictionary with lists of processed images and text analyses
    """
    processed_images = []
    text_analyses = []

    for file_path in files:
        # Determine file type and process accordingly
        suffix = file_path.suffix.lower()

        if suffix in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
            result = process_image(file_path, output_dir)
            if result:
                processed_images.append(result)

        elif suffix in [".txt", ".log", ".md"]:
            result = process_text(file_path, output_dir)
            if result:
                text_analyses.append(result)
        else:
            logger.warning(f"Unsupported file type: {file_path}")

    return {"images": processed_images, "texts": text_analyses}
