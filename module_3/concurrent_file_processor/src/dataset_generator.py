"""
Dataset generator - creates test files for benchmarking.
"""

from pathlib import Path
from PIL import Image
import random
import string
from .utils import setup_logger, ensure_dir

logger = setup_logger(__name__)


def generate_random_text(num_words: int = 1000) -> str:
    """
    Generate random text with specified number of words.

    Args:
        num_words: Number of random words to generate

    Returns:
        Random text string
    """
    words = []
    for _ in range(num_words):
        word_length = random.randint(3, 12)
        word = "".join(random.choices(string.ascii_lowercase, k=word_length))
        words.append(word)

    # Add some punctuation and newlines
    text = " ".join(words)
    text = text.replace(" ", "\n", text.count(" ") // 20)  # Add newlines
    text = text.replace(" ", ". ", text.count(" ") // 50)  # Add periods

    return text


def generate_random_image(width: int = 1920, height: int = 1080) -> Image.Image:
    """
    Generate a random RGB image.

    Args:
        width: Image width
        height: Image height

    Returns:
        PIL Image object
    """
    # Create random RGB image
    pixels = []
    for _ in range(width * height):
        pixels.append(
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )

    img = Image.new("RGB", (width, height))
    img.putdata(pixels)
    return img


def create_test_dataset(output_dir: Path, num_images: int = 10, num_texts: int = 10):
    """
    Create a test dataset with random images and text files.

    Args:
        output_dir: Directory to save test files
        num_images: Number of images to generate
        num_texts: Number of text files to generate
    """
    ensure_dir(output_dir)

    logger.info(f"Generating {num_images} images and {num_texts} text files...")

    # Generate images
    for i in range(num_images):
        img = generate_random_image(
            width=random.randint(800, 2000), height=random.randint(600, 1500)
        )
        img_path = output_dir / f"test_image_{i:03d}.jpg"
        img.save(img_path, quality=85)
        logger.info(f"Created {img_path}")

    # Generate text files
    for i in range(num_texts):
        text = generate_random_text(num_words=random.randint(500, 2000))
        text_path = output_dir / f"test_text_{i:03d}.txt"

        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text)

        logger.info(f"Created {text_path}")

    logger.info(f"Test dataset created in {output_dir}")


if __name__ == "__main__":
    # Generate test dataset
    dataset_dir = Path(__file__).parent.parent / "data" / "test_dataset"
    create_test_dataset(dataset_dir, num_images=10, num_texts=10)
