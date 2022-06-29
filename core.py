#!/usr/bin/env python

from time import sleep
from typing import Optional, Union, Generator, Any

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
    start_urls: Optional[list[str]] = []
    extra_urls: Optional[list[str]] = []
    requests_delay: Optional[Union[int, float]] = .0

    def __init__(self) -> None:
        self.name = self.name if self.name is not None else self.__class__.__name__
        self.session = HTMLSession()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name={repr(self.name)}, start_urls={self.start_urls}, extra_urls={self.extra_urls})'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return self.start_urls == other.start_urls and self.extra_urls == other.extra_urls

    def setup(self, *args, **kwargs) -> None:
        """Setups the spiders before starting."""
        if kwargs.get('start_urls') is not None:
            self.start_urls = kwargs.get('start_urls')
        if kwargs.get('extra_urls') is not None:
            self.extra_urls = kwargs.get('extra_urls')

    def fetch(self) -> Generator[Any, None, None]:
        """Goes between all the specified URLs."""
        print(f'{self.name} started...')
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

        print('Done!')

    def parse(self, response: HTMLSession) -> Generator[Any, None, None]:
        """Parses the response and yields items."""
        raise NotImplementedError


def _build_articles_query(**kwargs) -> str:
    """Builds the articles and case law query from the given arguments."""
    keywords = f'q={kwargs.get("keywords").replace(" ", "+")}'
    year_range = f'as_ylo={kwargs.get("start_year")}&as_yhi={kwargs.get("end_year")}'
    languages = f'lr={"|".join([f"lang_{l}" for l in kwargs.get("languages")])}'
    return f'hl=en&{keywords}&{year_range}&{languages}&{kwargs.get("extra", "")}'


class GSArticlesSpider(Spider):
    """Google Scholar articles category spider."""

    # name = 'Google Scholar articles spider'
    requests_delay = .5

    def setup(self, *args, **kwargs):
        query = _build_articles_query(**kwargs, extra='as_sdt=0,5')
        self.start_urls.append(f'https://scholar.google.com/scholar?{query}')

    def parse(self, response: HTMLSession) -> Generator[dict, None, None]:
        articles = response.html.xpath('//div[@class="gs_r gs_or gs_scl"]')
        for article in articles:
            title = article.xpath('//h3[@class="gs_rt"]/a | .//h3[@class="gs_rt"]/span[2]', first=True).text
            metadata = article.xpath('//div[@class="gs_a"]', first=True).text
            metadata = list(map(lambda x: x.strip(), metadata.replace('\xa0', '').split('- ')))
            authors = metadata[0]
            year = metadata[1][-4:]
            year = int(year) if len(year) == 4 and year.isnumeric() else None
            source = article.xpath('//h3[@class="gs_rt"]/a/@href', first=True)
            paper = article.xpath('//div[@class="gs_or_ggsm"]/a/@href', first=True)
            citations_no = article.xpath('//div[@class="gs_ri"]/div[@class="gs_fl"]/a[3][contains(., "Cited by")]', first=True)
            citations_no = int(citations_no.text.replace('Cited by ', '')) if citations_no is not None else 0
            yield {
                'title': title,
                'authors': authors,
                'year': year,
                'source': source,
                'paper': paper,
                'citations no.': citations_no,
            }

        next_page = response.html.xpath('//div[@id="gs_res_ccl_bot"]//td[@align="left"]/a/@href', first=True)
        if next_page is not None:
            next_page_url = f'https://scholar.google.com{next_page}'
            print(f'Next page found at {next_page_url}')
            self.extra_urls.append(next_page_url)


class GSCaseLawSpider(Spider):
    """Google Scholar case law category spider."""

    # name = 'Google Scholar case law spider'
    requests_delay = .5

    def setup(self, *args, **kwargs):
        query = _build_articles_query(**kwargs, extra='as_sdt=2006')
        self.start_urls.append(f'https://scholar.google.com/scholar?{query}')

    def parse(self, response: HTMLSession) -> Generator[dict, None, None]:
        articles = response.html.xpath('//div[@class="gs_r gs_or gs_scl"]')
        for article in articles:
            title = article.xpath('//h3[@class="gs_rt"]/a | .//h3[@class="gs_rt"]/span[2]', first=True).text
            metadata = article.xpath('//div[@class="gs_a"]', first=True).text
            metadata = list(map(lambda x: x.strip(), metadata.replace('\xa0', '').split('- ')))
            year = metadata[1][-4:]
            year = int(year) if len(year) == 4 and year.isnumeric() else None
            case = ' - '.join(metadata[:2]) if len(metadata) > 1 else metadata[0]
            case = case[:-6] if year is not None else case
            source = article.xpath('//h3[@class="gs_rt"]/a/@href', first=True)
            source = f'https://scholar.google.com{source}' if source is not None else None
            citations_no = article.xpath('//div[@class="gs_ri"]/div[@class="gs_fl"]/a[3][contains(., "Cited by")]', first=True)
            citations_no = int(citations_no.text.replace('Cited by ', '')) if citations_no is not None else 0
            yield {
                'title': title,
                'case': case,
                'year': year,
                'source': source,
                'citations no.': citations_no,
            }

        next_page = response.html.xpath('//div[@id="gs_res_ccl_bot"]//td[@align="left"]/a/@href', first=True)
        if next_page is not None:
            next_page_url = f'https://scholar.google.com{next_page}'
            print(f'Next page found at {next_page_url}')
            self.extra_urls.append(next_page_url)


class GSProfilesSpider(Spider):
    """Google Scholar profiles category spider."""

    # name = 'Google Scholar profiles spider'
    requests_delay = .5

    def setup(self, *args, **kwargs):
        query = f'hl=en&user={kwargs.get("keywords")}&cstart=0&pagesize=100'
        self.start_urls.append(f'https://scholar.google.com/citations?{query}')
        self.cstart = 0

    def parse(self, response: HTMLSession) -> Generator[dict, None, None]:
        articles = response.html.xpath('//tr[@class="gsc_a_tr"]')
        for article in articles:
            title = article.xpath('//a[@class="gsc_a_at"]', first=True).text
            authors = article.xpath('//div[@class="gs_gray"][1]', first=True).text
            source = article.xpath('//a[@class="gsc_a_at"]/@href', first=True)
            source = f'https://scholar.google.com{source}' if source is not None else None
            year = article.xpath('//span[@class="gsc_a_h gsc_a_hc gs_ibl"]/text()', first=True)
            citations_no = article.xpath('//a[@class="gsc_a_ac gs_ibl"]', first=True)
            citations_no = int(citations_no.text) if citations_no is not None and citations_no.text else 0
            yield {
                'title': title,
                'authors': authors,
                'source': source,
                'year': year,
                'citations no.': citations_no,
            }

        next_page = response.html.xpath('//button[@class="gs_btnPD gs_in_ib gs_btn_flat gs_btn_lrge gs_btn_lsu"]', first=True)
        if next_page.attrs.get('disabled') is None:
            current_page_url = response.url
            next_page_url = current_page_url.replace(f'cstart={self.cstart}', f'cstart={self.cstart+100}')
            self.cstart += 100
            print(f'Next articles found at {next_page_url}')
            self.extra_urls.append(next_page_url)


if __name__ == '__main__':
    import os
    import sys
    import argparse
    from pathlib import Path

    import pandas as pd

    parser = argparse.ArgumentParser(description='Scrapes Google Scholar for articles, case law, and profiles.')
    parser.add_argument('keywords', type=str, help='The keywords to search for')
    parser.add_argument('-c', '--case-law', action='store_true', help='Search for case law')
    parser.add_argument('-p', '--profiles', action='store_true', help='Search for a profile articles')
    parser.add_argument('-s', '--start-year', type=int, help='The start year')
    parser.add_argument('-e', '--end-year', type=int, help='The end year')
    parser.add_argument('-l', '--languages', nargs='+', default=['en'], help='Allowed languages (default: en)')
    parser.add_argument('-o', '--output', type=str, default='output.csv', help='The output file (default: output.csv)')
    parser.add_argument('-y', '--year', action='store_true', help='Sort by year')
    parser.add_argument('-q', '--quiet', action='store_true', help='Do not print progress')
    args = parser.parse_args()

    if args.quiet:
        sys.stdout = open(os.devnull, 'w')
    params = {
        'keywords': args.keywords,
        'start_year': args.start_year,
        'end_year': args.end_year,
        'languages': args.languages,
    }

    if args.case_law:
        gs_spider = GSCaseLawSpider()
    elif args.profiles:
        gs_spider = GSProfilesSpider()
    else:
        gs_spider = GSArticlesSpider()

    gs_spider.setup(**params)
    results = pd.DataFrame(gs_spider.fetch())
    if results.empty:
        print('No results found. Try again later or change your IP address.')
        sys.exit(1)

    if args.year:
        results.sort_values('year', ascending=False, inplace=True)
    else:
        results.sort_values('citations no.', ascending=False, inplace=True)
    # results[['year', 'citations no.']] = results[['year', 'citations no.']].fillna('n/a')

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)
