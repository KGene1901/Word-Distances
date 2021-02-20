'''
Versions:
- python 3.8.0
- beautifulsoup 4.9.3
- seaborn 0.11.1
- openpyxl 3.0.6
'''
from bs4 import BeautifulSoup
import seaborn as sns
from openpyxl import Workbook, load_workbook
import requests

## Problem 1
# to search https://www.bbc.co.uk/search?q={keyword}&page={number}
# url should be like https://www.bbc.co.uk/news/* (need to try if focusing on technology only is better)
# need 100 articles for each keyword
# {'targeted threat', 'Advanced Persistent Threat', 'phishing', 'DoS attack', 'malware', 'computer virus', 'spyware', 'malicious bot', 'ransomware', 'encryption']

def extractNewsInfo(article): # gets type and url link of news article from HTML
	soup2 = BeautifulSoup(str(article), 'lxml')
	article_type = (soup2.find_all('span', 'ssrcss-1hizfh0-MetadataSnippet ecn1o5v0'))[1].find('span').text
	article_link = (soup2.find('a', 'ssrcss-vh7bxp-PromoLink e1f5wbog6', href=True))['href']
	
	if article_type == 'News':
		return True, article_link
	
	return False, None

def getArticles(keywords):
	for keyword in keywords:
		print(keywords)
		page_count = 1

		while len(keywords[keyword]) <= 100:
			params = {'q' : keyword, 'page' : page_count}
			url = 'https://www.bbc.co.uk/search'
			resp = requests.get(url, params=params)
			page_count += 1
			soup = BeautifulSoup(resp.text, 'html.parser')
			articles = soup.find('ul', 'ssrcss-1a1yp44-Stack e1y4nx260').find_all('li')
			
			for article in articles:
				isNews, article_link = extractNewsInfo(article)
				if isNews:
					keywords[keyword].append(article_link)

## Problem 2
# process each individual article
def processArticle():
	pass

## Problem 3
def createDistanceSpreadsheet(keywords_workbook, active_sheet, keyword_count):
	for col_num in range(2, keyword_count+2):
		active_sheet.cell(row=1, column=col_num).value = active_sheet.cell(row=col_num, column=1).value

	keywords_workbook.save('distance.xlsx')


## Problem 4
def visusalizeDistance():
	pass

if __name__ == '__main__':
	keywords_workbook = load_workbook('./keywords.xlsx')
	active_sheet = keywords_workbook.active
	keywords = {}

	for x in range(2, active_sheet.max_row + 1):
		keywords[active_sheet.cell(row=x, column=1).value] = []

	# getArticles(keywords)
	createDistanceSpreadsheet(keywords_workbook, active_sheet, len(keywords))