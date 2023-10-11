import logging
import os

OUTPUT_DIRECTORY = "./output"


def create_output_directory() -> None:
    """Create output directory if it does not exist"""
    if not os.path.exists(OUTPUT_DIRECTORY):
        logging.info(f"Creating path {OUTPUT_DIRECTORY}...")
        os.makedirs(OUTPUT_DIRECTORY)
    else:
        logging.info(f"{OUTPUT_DIRECTORY} already exists.")
