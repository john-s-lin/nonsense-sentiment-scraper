import json
import logging
import os
import re
import sys

from clustering.clustering import TextClusterer
from scrapy.crawler import CrawlerProcess
from scraper.spider import ModifiedSpider, OVERRIDE_SETTINGS
from scraper.extractor import TextExtractor, RAW_TEXT_OUTPUT_FILE
from sentiment.sentiment_analysis import SentimentAnalyzer
from utils.utils import (
    create_output_directory,
    get_user_input_starting_url,
    get_user_input_crawl_limit,
    OUTPUT_DIRECTORY,
)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


VISITED_URLS_OUTPUT_FILE = "./output/urls.json"
N_CLUSTERS = os.getenv("CLUSTERS", "3")


def crawler() -> None:
    """Crawls using GinaCodySpider and stores visited URLS in json format"""
    process = CrawlerProcess(settings=OVERRIDE_SETTINGS)
    spider = ModifiedSpider

    start_url = get_user_input_starting_url()
    spider.set_start_urls(start_url)

    crawl_limit = get_user_input_crawl_limit()
    spider.set_crawl_limit(crawl_limit)

    process.crawl(spider)
    process.start()

    def store_visited_urls(visited_urls: set) -> None:
        """Stores visited URLs in JSON

        Args:
            visited_urls (set): Visited URLs
        """
        create_output_directory()
        with open(VISITED_URLS_OUTPUT_FILE, "w") as file:
            output_json = json.dumps({"visited_urls": list(visited_urls)})
            file.write(output_json)
            logging.info(f"URLs written to {VISITED_URLS_OUTPUT_FILE}.")

    store_visited_urls(spider.visited_urls)


def extract() -> None:
    """Extracts raw text after parsing list of URLS"""
    extractor = TextExtractor()
    url_list = extractor.get_url_list(VISITED_URLS_OUTPUT_FILE)
    raw_text = extractor.get_requests_from_urls(url_list)
    extractor.store_page_text(raw_text)


def cluster(n_clusters: int) -> None:
    """Clusters text by provided number of clusters

    Args:
        n_clusters (int): Number of clusters
    """
    clusterer = TextClusterer(n_clusters)
    raw = clusterer.get_raw_text(RAW_TEXT_OUTPUT_FILE)
    tf_idf_vectors = clusterer.vectorize_text(raw)
    lsa_tfidf = clusterer.reduce_dimensions(tf_idf_vectors)
    clusterer.generate_kmeans(lsa_tfidf)
    clusterer.generate_stats(f"./output/kmeans_{n_clusters}_clusters.json")
    labeled_docs = clusterer.classify_documents_by_cluster(raw)
    clusterer.save_to_output_file(
        f"./output/labeled_text_{n_clusters}_clusters.json", labeled_docs
    )


def sentiment() -> None:
    """Generates sentimental analysis of text and stores data in output files"""
    analyzer = SentimentAnalyzer()
    labeled_json_list = [
        (OUTPUT_DIRECTORY + "/" + filename)
        for filename in os.listdir(OUTPUT_DIRECTORY)
        if filename.startswith("labeled_text") and filename.endswith(".json")
    ]

    def _get_n_clusters_from_filename(filename: str) -> str:
        """Gets n_clusters from filename

        Args:
            filename (str): filename

        Returns:
            str: n_clusters
        """
        return re.findall(r"\d+", filename)[0]

    for filename in sorted(labeled_json_list):
        n_clusters = _get_n_clusters_from_filename(filename)
        labeled_text_ = analyzer.get_labeled_text_json(filename)
        afinn_text = analyzer.generate_afinn_scores_per_doc(labeled_text_)
        clustered_afinn_scores = analyzer.generate_average_afinn_scores_per_cluster(
            afinn_text, n_clusters
        )
        analyzer.save_to_output_file(
            f"./output/afinn_text_{n_clusters}_clusters.json", afinn_text
        )
        analyzer.save_to_output_file(
            f"./output/avg_afinn_{n_clusters}_clusters.json", clustered_afinn_scores
        )


def raise_argument_error():
    raise ValueError(
        "Argument must be [ --scraper CRAWL_LIMIT=<int> | --extract | --cluster CLUSTERS=<int> | --sentiment ]"
    )


def main():
    args = sys.argv[1:]

    if len(args) > 0:
        if args[0] == "--scraper":
            crawler()
        elif args[0] == "--extract":
            extract()
        elif args[0] == "--cluster":
            cluster(int(N_CLUSTERS))
        elif args[0] == "--sentiment":
            sentiment()
        else:
            raise_argument_error()
    else:
        raise_argument_error()


if __name__ == "__main__":
    main()
