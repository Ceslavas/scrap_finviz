import yaml
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import parse_qs, urlparse
from io import StringIO
import time
from datetime import datetime
import random
from dateutil import parser


def to_date(date_input) -> str:
    """
    Convert date and time from various formats to "YYYY-MM-DD HH24:MI:SS" string format.

    :param date_input: date in various formats (str, pandas.Timestamp, datetime, etc.).
    :return: Date and time string in "YYYY-MM-DD HH24:MI:SS" format.
    """
    # If the input type is already datetime, no additional parsing is required
    if isinstance(date_input, datetime):
        return date_input.strftime("%Y-%m-%d %H:%M:%S")

    # Parsing and converting a string or other formats to datetime
    parsed_date = parser.parse(str(date_input))
    return parsed_date.strftime("%Y-%m-%d %H:%M:%S")


def to_price(price_input) -> float:
    """
    Convert price from various formats to float.

    :param price_input: Price in various formats (str, float, int, etc.). (such as 97.01B or 97.01M)
    :return: Floating point number.
    """
    try:
        price: float = None
    
        # If the input type is already float, no additional parsing is required
        if isinstance(price_input, float):
            price = price_input

        # if the input string ends with 'B' or 'M', then multiply by 1_000_000_000 or 1_000_000
        # otherwise just convert to float
        if price_input[-1] == 'B':
            price = float(price_input[:-1]) * 1_000_000_000
    
        if price_input[-1] == 'M':
            price = float(price_input[:-1]) * 1_000_000
    
        if price_input[-1] == 'K':
            price = float(price_input[:-1]) * 1_000
        
        if price is None:
            return None
    except:
        print(type(price_input))
        print(price_input)
        return price_input
    
    return round(price, 2)


def generate_random_number(min_value, max_value, step):
    """
    Generate a random number in the range [min_value, max_value] with the given step.

    :param min_value: Minimal value of the range.
    :param max_value: Maximal value of the range.
    :param step: Step of the random number.
    :return: random number in the range [min_value, max_value] with the given step.
    """
    random_number = random.uniform(min_value, max_value)
    return round(random_number / step) * step


class FinvizScraper:
    def __init__(self, config):
        self.pages_nr   = 0
        self.headers_list   = config['finviz_scraper']['user_agent']
        self.initial_url    = config['finviz_scraper']['initial_url']
        
        if self.initial_url != '':
            parts = self.get_initial_url_parts(self.initial_url)
            self.base_url   = parts['base_url']
            self.sort       = parts['sort']
            self.filters    = parts['filters']
            self.columns    = parts['columns']
        else:
            self.base_url   = config['finviz_scraper']['base_url']
            self.sort       = config['finviz_scraper']['sort']
            self.filters    = config['finviz_scraper']['filters']
            self.columns    = config['finviz_scraper']['columns']
            self.initial_url = self.base_url + f"?v=151&f={self.filters}&ft=4&o={self.sort}&ar=180&c={self.columns}"
            
    def get_initial_url_parts(self, url):
        """
        Parses the provided Finviz URL and extracts its components.

        :param url: The Finviz URL to be parsed.
        :return: A dictionary containing the base URL, view, filters, sort, and columns.
        """

        # Parse the URL
        parsed_url = urlparse(url)

        # Extract the base URL
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        # Extract the query parameters
        query_params = parse_qs(parsed_url.query)

        # Extract specific parts
        result = {
            "base_url": base_url,
            "view": query_params.get("v", [""])[0],
            "filters": query_params.get("f", [""])[0],
            "sort": query_params.get("o", [""])[0],
            "columns": query_params.get("c", [""])[0]
        }
        return result

    def get_pages_soup(self, url: str) -> BeautifulSoup:
        header = random.choice(self.headers_list)
        response = requests.get(url, headers=header)
        n = generate_random_number(0.5, 10.0, 0.5)
        time.sleep(n)
        print(f'whait: {n}s', end=';\t')
        print(f'header: {header};')
        soup = BeautifulSoup(response.text, 'lxml')
        return soup
    
    def get_next_pages_url(self, soup: BeautifulSoup) -> str:
        pagination_container = soup.find('td', attrs={'id': 'screener_pagination'})
        if pagination_container:
            link = pagination_container.find_all('a', class_='screener-pages is-next')	
            if not link:
                return None
            query = urlparse(link[0].attrs['href']).query
            params = parse_qs(query)
            v = params.get('v', [None])[0]
            page_start_row = params.get('r', [None])[0]
            if page_start_row is None:
                return None
            else:
                url = self.base_url + f"?v={v}&f={self.filters}&ft=4&o={self.sort}&r={page_start_row}&c={self.columns}"
                return url
        return None

    def table_to_dataframe(self, soup_table) -> pd.DataFrame:
        if soup_table:
            table_html = StringIO(str(soup_table))
            return pd.read_html(table_html)[0]
        else:
            return pd.DataFrame()

    def scrape_page(self, url: str):
        self.pages_nr += 1
        print(f'Scrape page: {self.pages_nr}', end=';\t')
        soup = self.get_pages_soup(url)
        table_screen_data = soup.select_one('.screener_table')
        if table_screen_data:
            return soup, self.table_to_dataframe(table_screen_data)
        return soup, pd.DataFrame()

    def scrape_all_pages(self) -> pd.DataFrame:
        all_dataframes = []
        soup, df = self.scrape_page(self.initial_url)
        all_dataframes.append(df)
        
        next_url = self.get_next_pages_url(soup)
        while next_url:
            soup, df = self.scrape_page(next_url)
            all_dataframes.append(df)
            next_url = self.get_next_pages_url(soup)
        return pd.concat(all_dataframes, ignore_index=True)

    def df_postprocess(self, df: pd.DataFrame) -> pd.DataFrame: 
        df['Market Cap']        = df['Market Cap'].apply(lambda x: to_price(x))
        df['Sales']             = df['Sales'].apply(lambda x: to_price(x))
        df['Income']            = df['Income'].apply(lambda x: to_price(x))
        df['Outstanding']       = df['Outstanding'].apply(lambda x: to_price(x))
        df['Float']             = df['Float'].apply(lambda x: to_price(x))
        df['Short Interest']    = df['Short Interest'].apply(lambda x: to_price(x))
        df['Avg Volume']        = df['Avg Volume'].apply(lambda x: to_price(x))
        df['IPO Date']          = df['IPO Date'].apply(lambda x: to_date(x))
        return df


# load config
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)


# create scraper
scraper = FinvizScraper(config)


# scrape all pages
df = scraper.scrape_all_pages()


# postprocess dataframe columns
df = scraper.df_postprocess(df)


# save dataframe to csv
df.to_csv('screen.csv')
