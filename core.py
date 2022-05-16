#!/usr/bin/env python

from time import sleep

import pandas as pd
from requests_html import HTMLSession


class GoogleScholarScraper:
    """Scrapes Google Scholar for articles and case law."""

    def _search_by_params(self, **kwargs) -> list:
        """Searches and returns all the articles."""
        keywords = f'q={kwargs.get("keywords").replace(" ", "+")}'
        year_range = f'as_ylo={kwargs.get("start_year")}&as_yhi={kwargs.get("end_year")}'
        languages = f'lr={"|".join([f"lang_{l}" for l in kwargs.get("languages")])}'
        query = f'hl=en&{keywords}&{year_range}&{languages}&{kwargs.get("extra", "")}'

        session = HTMLSession()
        all_results = []

        for i in range(100):  # Each page has 10 results and there are 100 pages
            print(f'Scraping page {i+1}...')
            response = session.get(f'https://scholar.google.com/scholar?{query}&start={i*10}')
            page_results = response.html.find('div.gs_r.gs_or.gs_scl')
            if len(page_results) < 10:  # It's the last page of results
                print('No more results.')
                break
            all_results.extend(page_results)
            sleep(.38)  # Act like a human to make sure we don't get blocked

        return all_results

    def get_articles(self, **kwargs) -> pd.DataFrame:
        """Gets the articles and sorts them by citation count."""
        all_results = self._search_by_params(**kwargs, extra='as_sdt=0,5')
        articles = []

        for result in all_results:
            title = result.find('h3.gs_rt', first=True).text
            authors = result.find('div.gs_a', first=True).text.split('\xa0')[0]
            source = result.find('h3.gs_rt a', first=True)
            source = source.attrs['href'] if source is not None else 'N/A'
            paper = result.find('div.gs_or_ggsm a', first=True)
            paper = paper.attrs['href'] if paper is not None else 'N/A'
            citations = result.find('div.gs_ri div.gs_fl a')
            citations = int(citations[2].text.replace('Cited by ', '')) if citations[2].text.startswith('Cited by ') else 0
            articles.append({
                'title': title,
                'authors': authors,
                'source': source,
                'paper': paper,
                'citations': citations,
            })

        return pd.DataFrame(articles).sort_values(by='citations', ascending=False) if articles else pd.DataFrame()

    def get_case_law(self, **kwargs) -> pd.DataFrame:
        """Gets the case law and sorts them by citation count."""
        all_results = self._search_by_params(**kwargs, extra='as_sdt=2006')
        case_law = []

        for result in all_results:
            title = result.find('h3.gs_rt', first=True).text
            court = ' - '.join(result.find('div.gs_a', first=True).text.replace('\xa0', ' ').split(' - ')[:2])
            source = result.find('h3.gs_rt a', first=True)
            source = f'https://scholar.google.com{source.attrs["href"]}' if source is not None else 'N/A'
            citations = result.find('div.gs_ri div.gs_fl a')
            citations = int(citations[2].text.replace('Cited by ', '')) if citations[2].text.startswith('Cited by ') else 0
            case_law.append({
                'title': title,
                'court': court,
                'source': source,
                'citations': citations,
            })

        return pd.DataFrame(case_law).sort_values(by='citations', ascending=False) if case_law else pd.DataFrame()


if __name__ == '__main__':
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Scrape Google Scholar for articles and case law.')
    parser.add_argument('keywords', type=str, help='The keywords to search for')
    parser.add_argument('-c', '--case-law', action='store_true', help='Search for case law')
    parser.add_argument('-s', '--start-year', type=int, help='The start year')
    parser.add_argument('-e', '--end-year', type=int, help='The end year')
    parser.add_argument('-l', '--languages', nargs='+', default=['en'], help='Allowed languages (default: en)')
    parser.add_argument('-o', '--output', type=str, default='output.csv', help='The output file (default: output.csv)')
    args = parser.parse_args()

    gs_scraper = GoogleScholarScraper()
    params = dict(keywords=args.keywords, start_year=args.start_year, end_year=args.end_year, languages=args.languages)
    results = gs_scraper.get_articles(**params) if not args.case_law else gs_scraper.get_case_law(**params)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)
    print(f'\nAll done! {len(results)} results found and successfully saved to `{args.output}` file.')
