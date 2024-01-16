Finviz Screener Scraper
========================

Overview:
	This project is a scraper for the Screener section of the finviz.com website. It's written in Python and allows for extracting stock data using filters set on the Finviz website.

Requirements:
	To run this scraper, you need to have Python 3 installed on your computer.
	Additionally, the following libraries are required:
		yaml
		requests
		BeautifulSoup from bs4
		pandas
		parse_qs and urlparse from urllib.parse
		StringIO
		time
		datetime from datetime
		random
		parser from dateutil

Installation:
	Ensure you have Python 3 and the above-listed libraries installed.
	Clone the scraper's repository or download its files to your computer.

Configuration:
	Before using the scraper, you need to set up the config.yaml file:
		Open finviz.com/screener.ashx.
		Set up the filters on the website so that the Screener displays a list of stocks of your interest.
		Copy the URL from your browser's address bar.
		Paste the copied URL as the value for the initial_url parameter in the config.yaml file.

Running the Scraper:
	To run the scraper, follow these steps:
		Open a command line or terminal.
		Navigate to the directory where the scrap_finviz.py script is located.
		Enter the command "python scrap_finviz.py" to run the script.