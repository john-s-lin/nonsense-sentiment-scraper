import os

from scrapy.http.response.html import HtmlResponse
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

CRAWL_LIMIT = os.getenv("CRAWL_LIMIT", 100)
OVERRIDE_SETTINGS = {
    "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    "CLOSESPIDER_PAGECOUNT": 100000,
    "ROBOTSTXT_OBEY": True,
    "LOG_FILE": "logs/output.log",
    "LOG_FILE_APPEND": False,
}


class GinaCodySpider(CrawlSpider):
    name = "ginacody"
    start_urls = ["https://www.concordia.ca/ginacody.html/"]
    visited_urls = set()
    rules = [
        Rule(
            LinkExtractor(
                allow="ginacody",
                deny=(
                    r"^(?!https://www.concordia.ca).+",
                    r"(https://www.concordia.ca/fr).+",
                ),
            ),
            callback="parse_item",
            follow=True,
        )
    ]
    crawl_limit = int(CRAWL_LIMIT)

    def parse_item(self, response: HtmlResponse) -> None:
        """Parse urls and stores in a set

        Args:
            response (HtmlResponse): Response

        Raises:
            CloseSpider: Closes crawler
        """
        if len(self.visited_urls) < self.crawl_limit:
            if self.check_robot_metatag(response):
                self.visited_urls.add(response.url)
            yield
        else:
            raise CloseSpider(f"Crawl limit reached: {self.crawl_limit}")

    def check_robot_metatag(self, response: HtmlResponse) -> bool:
        """Returns false if robots metatag in page is noindex or nofollow

        Args:
            response (HtmlResponse): Response

        Returns:
            bool: False if robots have noindex or nofollow
        """
        meta_robots_tag_content = response.xpath(
            "//meta[@name='robots']/@content"
        ).extract_first()
        if meta_robots_tag_content and (
            "noindex" in meta_robots_tag_content or "nofollow" in meta_robots_tag_content
        ):
            return False
        return True
