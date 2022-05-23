from time import sleep
from typing import Optional, Generator, Any

from requests_html import HTMLSession


class Spider:
    """Base class for all web spiders.

    Attributes:
        name: The name of the spider.
        start_urls: The list of URLs to start scraping from.
        extra_urls: The URLs that added after the start URLs.
        requests_delay: The delay between requests.
    """

    name: Optional[str] = None
    start_urls: Optional[list[str]] = None
    extra_urls: Optional[list[str]] = None
    requests_delay: Optional[float] = None

    def __init__(self) -> None:
        self.name = self.name
        self.start_urls = self.start_urls if self.start_urls is not None else []
        self.extra_urls = self.extra_urls if self.extra_urls is not None else []
        self.requests_delay = self.requests_delay if self.requests_delay is not None else 0
        self.session = HTMLSession()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name}, start_urls={self.start_urls}, extra_urls={self.extra_urls})'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return self.start_urls == other.start_urls and self.extra_urls == other.extra_urls

    def setup(self, *args, **kwargs) -> None:
        """Setups the scraper before scraping."""
        if kwargs.get('start_urls') is not None:
            self.start_urls = kwargs.get('start_urls')
        if kwargs.get('extra_urls') is not None:
            self.extra_urls = kwargs.get('extra_urls')

    def scrape(self) -> Generator[list[dict], None, None]:
        """Scrapes between all the specified URLs."""
        print(f'Scraping started for {self.name}...')
        requests_count = 0

        for url in self.start_urls:
            requests_count += 1
            print(f'\nFetching request #{requests_count} from {url}')
            response = self.session.get(url)
            for item in self.parse(response):
                yield item
            sleep(self.requests_delay)

        for url in self.extra_urls:
            requests_count += 1
            print(f'\nFetching request #{requests_count} from {url}')
            response = self.session.get(url)
            for item in self.parse(response):
                yield item
            sleep(self.requests_delay)

        print('Scraping finished!')

    def parse(self, response: HTMLSession) -> Generator[Any, None, None]:
        """Parses the response and yields items."""
        raise NotImplementedError