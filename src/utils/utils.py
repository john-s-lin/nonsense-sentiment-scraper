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


def get_user_input_starting_url() -> str:
    """Sanitize raw input to starting URL

    Returns:
        str: starting URL
    """
    raw_input = input("Input a starting URL: ")

    if raw_input.startswith("https://") or raw_input.startswith("http://"):
        return raw_input

    return f"http://{raw_input}"


def get_user_input_crawl_limit() -> int:
    raw_input = input("Set the number of pages to crawl (1-10000): ")

    if raw_input.isdigit():
        output = int(raw_input)

        if output < 1 or output > 10000:
            raise ValueError("Ensure input is between 1 and 10000.")

        return output

    raise ValueError("Did not enter a positive integer.")
