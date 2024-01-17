
# Finviz Screener Scraper

## Overview
This project is a scraper for the Screener section of the finviz.com website. Written in Python, the scraper allows extracting stock data using filters set on the Finviz website. It is useful for market analysts, investors, and financial application developers to obtain up-to-date stock information.

## Requirements
- Python 3.9.13 (compatibility with other Python versions is not guaranteed).
- Required libraries:
  ```
  requests
  pandas
  beautifulsoup4
  ```
  To install all libraries at once, run the command: `pip install -r requirements.txt`.

## Installation
1. Install Python 3.9.13 and the required libraries.
2. Clone the scraper's repository or download its files to your computer:
   ```
   git clone https://github.com/Ceslavas/scrap_finviz.git
   ```

## Configuration
Before using the scraper, you need to set up the `config.yaml` file:
1. Open https://finviz.com/screener.ashx in your browser.
2. Set up the filters on the site so that the Screener displays a list of stocks of your interest.
3. Copy the URL from your browser's address bar.
4. Insert the copied URL as the value for the `initial_url` parameter in the `config.yaml` file.

Example `config.yaml` file:
```yaml
initial_url: 'https://finviz.com/screener.ashx?v=111&f=...'
```

## Running the Scraper
To run the scraper, follow these steps:
1. Open a command line or terminal.
2. Navigate to the directory where the `scrap_finviz.py` script is located.
3. Enter the command `python scrap_finviz.py`.

## Results
The scraper will create a CSV file (screen.csv) with stock data. The file will contain information such as company name, stock price, volume, and other parameters.

## FAQ
**Q:** Can the scraper be used for other websites?
**A:** No, this scraper is specifically designed to work with the Finviz site.

## Contributions
If you would like to contribute to the project, please submit a pull request or create an issue with your suggestions.

## License
This project is distributed under the MIT license. See the LICENSE.txt file for details.
