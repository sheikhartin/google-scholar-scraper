## Google Scholar Scraper

![GitHub repo status](https://img.shields.io/badge/status-active-green?style=flat)
![GitHub license](https://img.shields.io/github/license/sheikhartin/google-scholar-scraper)
![GitHub contributors](https://img.shields.io/github/contributors/sheikhartin/google-scholar-scraper)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/sheikhartin/google-scholar-scraper)
![GitHub repo size](https://img.shields.io/github/repo-size/sheikhartin/google-scholar-scraper)

Unfortunately, Google Scholar does not support exporting results... I needed the most cited papers for a research project, and after trying [an imperfect script](https://github.com/wittmannf/sort-google-scholar) I decided to write my own. <!-- Therefore, perfectionist is the philosophy of the project :see_no_evil: -->

_Important note: The spiders don't send more than 2 requests per second to Google Scholar. The reason is that we don't like to solve the CAPTCHA, so it's better to wait a little and acting like a human. Changing IP address sometimes is a good idea..._ :weary:

### Features

- [x] Supports multiple languages
- [x] Customizable date range
- [x] Sorts by number of citations
- [x] Sorts by year
- [x] Searches for articles
- [x] Searches for case law
- [x] Searches in a profile by ID
- [ ] Graphical interface

![A shocked skeleton](https://media.giphy.com/media/MuTenSRsJ7TQQ/giphy.gif)

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

Limit the languages to one or more:

```bash
python core.py "medical" -l en es zh-tw fr
```

Set the output file path:

```bash
python core.py "machine learning" -s 2002 -o exports/most_cited_ml_articles_since_2002.csv
```

Sort the output by year:

```bash
python core.py "oceanography" -y
```

Search for case law:

```bash
python core.py "privacy" -c
```

Get a specific profile articles by the user ID:

```bash
python core.py "nms69lqaaaaj" -p -o jeff_dean_articles.csv
```

Make the program quiet:

```bash
python core.py "philosophy" -e 1234 -q
```

[Here](exports) is some example exports to see if the scraper meets your needs or not!

### License

This project is licensed under the MIT license found in the [LICENSE](LICENSE) file in the root directory of this repository.
