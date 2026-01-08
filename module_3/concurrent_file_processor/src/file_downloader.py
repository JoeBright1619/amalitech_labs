"""
File downloader module - handles downloading files from URLs.
"""

import requests
from pathlib import Path
from typing import Optional, List
from .utils import setup_logger

logger = setup_logger(__name__)


def download_file(url: str, save_path: Path, timeout: int = 30) -> Optional[Path]:
    """
    Download a file from a URL to a local path.

    Args:
        url: URL to download from
        save_path: Local path to save the file
        timeout: Request timeout in seconds

    Returns:
        Path to downloaded file, or None if download failed
    """
    try:
        logger.info(f"Downloading {url}")

        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Ensure parent directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file in chunks
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info(f"Downloaded {url} to {save_path}")
        return save_path

    except requests.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        return None
    except IOError as e:
        logger.error(f"Failed to save file {save_path}: {e}")
        return None


def download_files_sequential(urls: List[str], download_dir: Path) -> List[Path]:
    """
    Download multiple files sequentially.

    Args:
        urls: List of URLs to download
        download_dir: Directory to save downloaded files

    Returns:
        List of successfully downloaded file paths
    """
    downloaded_files = []

    for i, url in enumerate(urls):
        # Generate filename from URL or use index
        filename = url.split("/")[-1] or f"file_{i}.dat"
        save_path = download_dir / filename

        result = download_file(url, save_path)
        if result:
            downloaded_files.append(result)

    return downloaded_files
