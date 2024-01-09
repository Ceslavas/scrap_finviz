import yaml
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import parse_qs, urlparse
from io import StringIO
import sys
import os
import time
sys.path.append(os.path.abspath('../'))
from InteractiveBrokers.utils import to_date, to_price, try_except


class FinvizScraper:
    def __init__(self, config):
        self.pages_nr = 0
        self.base_url = config['finviz_scraper']['base_url']
        self.sort = config['finviz_scraper']['sort']
        self.filters = config['finviz_scraper']['filters']
        self.columns = config['finviz_scraper']['columns']
        self.headers = {
            'User-Agent': config['finviz_scraper']['user_agent']
        }

    def get_pages_soup(self, url: str) -> BeautifulSoup:
        response = requests.get(url, headers=self.headers)
        time.sleep(1)
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
        print(f'Page {self.pages_nr}')
        soup = self.get_pages_soup(url)
        table_screen_data = soup.select_one('.screener_table')
        if table_screen_data:
            return soup, self.table_to_dataframe(table_screen_data)
        return soup, pd.DataFrame()

    def scrape_all_pages(self, initial_url: str) -> pd.DataFrame:
        all_dataframes = []
        soup, df = self.scrape_page(initial_url)
        all_dataframes.append(df)
        
        next_url = self.get_next_pages_url(soup)
        while next_url:
            soup, df = self.scrape_page(next_url)
            all_dataframes.append(df)
            next_url = self.get_next_pages_url(soup)
        return pd.concat(all_dataframes, ignore_index=True)

    def df_postprocess(self, df: pd.DataFrame) -> pd.DataFrame: 
        df['Market Cap'] = df['Market Cap'].apply(lambda x: to_price(x))
        df['Sales'] = df['Sales'].apply(lambda x: to_price(x))
        df['Income'] = df['Income'].apply(lambda x: to_price(x))
        df['Outstanding'] = df['Outstanding'].apply(lambda x: to_price(x))
        df['Float'] = df['Float'].apply(lambda x: to_price(x))
        df['Short Interest'] = df['Short Interest'].apply(lambda x: to_price(x))
        df['Avg Volume'] = df['Avg Volume'].apply(lambda x: to_price(x))
        df['IPO Date'] = df['IPO Date'].apply(lambda x: to_date(x))
        return df


# load config
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# create scraper
scraper = FinvizScraper(config)

# set initial url
initial_url = scraper.base_url + f"?v=151&f={scraper.filters}&ft=4&o={scraper.sort}&ar=180&c={scraper.columns}"

# scrape all pages
df = scraper.scrape_all_pages(initial_url)

# postprocess dataframe columns
df = scraper.df_postprocess(df)

# save dataframe to csv
df.to_csv('screen.csv')
