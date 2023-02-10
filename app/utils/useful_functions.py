from .base_logger import logger

from pathlib import Path


def get_image_iterator(folder_path: str):
    """
    This function returns an iterator of all images in a folder.

    :param folder_path: the path to the folder containing the images
    :return: an iterator of Path objects representing the image files
    :raises FileNotFoundError: if the folder path does not exist
    """

    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    image_types = [".jpg", ".jpeg", ".png"]
    for file_path in folder.glob("*"):
        if file_path.is_file() and file_path.suffix in image_types:
            logger.debug(f"Found image: {file_path}")
            yield file_path
