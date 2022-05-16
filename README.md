## Google Scholar Scraper

Unfortunately, Google Scholar does not support exporting results... I needed the most cited papers for a university research project, and after trying [a imperfect script](https://github.com/WittmannF/sort-google-scholar) I decided to write my own. Therefore, perfectionist is the philosophy of the project :see_no_evil:

<b>Important note</b>: The average time to scrape all the 100 pages of results is around 2 minutes. The reason is that we don't like to solve the captcha, so we have to act like a human!

![A baby is looking at the book curiously!](https://media.giphy.com/media/8dYmJ6Buo3lYY/giphy.gif)

### Features

- [x] Supports multiple languages
- [x] Searches for articles and case law
- [x] Customizable date range
- [ ] Graphical interface

### Usage

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the scraper just by typing the keyword:

```bash
python core.py "cryptography"
```

Customize the date range:

```bash
python core.py "metaverse" -s 1997 -e 2018
```

Limit the languages:

```bash
python core.py "metaverse" -l en es zh-tw
```

Search for case law:

```bash
python core.py "privacy" -c
```

Set the output file:

```bash
python core.py "machine learning" -s 2002 -o exports/ml_most_cited_papers_since_2002.csv
```

### License

This project is licensed under the MIT license found in the [LICENSE](LICENSE) file in the root directory of this repository.
