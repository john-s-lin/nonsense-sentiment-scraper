import json
import logging
import re
import requests

from bs4 import BeautifulSoup

RAW_TEXT_OUTPUT_FILE = "./output/raw_text.json"


class TextExtractor:
    """Extracts and cleans raw text"""

    def __init__(self) -> None:
        pass

    def get_url_list(self, target_file: str) -> list:
        """Gets URL list from json file

        Args:
            target_file (str): Filename

        Returns:
            list: list of urls
        """
        data = {}
        try:
            with open(target_file, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            logging.error(f"Invalid filename: {target_file}")
        return data["visited_urls"]

    def get_requests_from_urls(self, url_list: list) -> dict:
        """Gets requests from urls and selects raw text with BeautifulSoup

        Args:
            url_list (list): list of urls

        Returns:
            dict: map of url to raw text from url
        """
        output = {}
        for url in url_list:
            logging.info(f"Extracting text from: {url}")
            request = requests.get(url=url)
            soup = BeautifulSoup(request.text, "lxml")

            title_exists = soup.find("title")
            title = title_exists.text if title_exists else ""

            body_list = self._clean_body(soup)
            body_str = " ".join(body_list)
            full_page = title + " " + body_str
            output[url] = full_page
        return output

    def store_page_text(self, responses: dict) -> None:
        """Stores raw text in json file

        Args:
            responses (dict): Raw text
        """
        with open(RAW_TEXT_OUTPUT_FILE, "w") as file:
            output_json = json.dumps(responses)
            file.write(output_json)
            logging.info(f"Raw text written to {RAW_TEXT_OUTPUT_FILE}.")

    def _clean_body(self, soup: BeautifulSoup) -> list:
        """Cleans raws text

        Args:
            soup (BeautifulSoup): BeautifulSoup of raw text from page

        Returns:
            list: List of strings from raw text
        """
        body_list = []
        for p in soup.find_all("p"):
            text = p.text
            stripped_text = text.strip()
            removed_newlines = stripped_text.replace("\n", " ")
            removed_tabs = removed_newlines.replace("\t", " ")
            replaced_unicode = re.sub(r"[^\x00-\x7F]+", " ", removed_tabs)
            cleaned_links = self._clean_links(replaced_unicode)
            body_list.append(cleaned_links)
        return body_list

    def _clean_links(self, text: str) -> str:
        """Removes links from raw text

        Args:
            text (str): raw text

        Returns:
            str: cleaned raw text
        """
        https_target = "https://"
        if https_target in text:
            end_index = text.find(https_target)
            return text[:end_index]
        return text
