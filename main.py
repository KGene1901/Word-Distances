"""
Versions:
- python 3.8.0
- beautifulsoup 4.9.3
- seaborn 0.11.1
- openpyxl 3.0.6
- pandas 1.2.2
- matplotlib 3.3.4
"""
from bs4 import BeautifulSoup
import seaborn as sns
from matplotlib import pyplot as plt
from openpyxl import Workbook, load_workbook
import pandas as pd
import requests
import re
import os
import json

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
def saveArticle(contentList, keyword, counter):
	"""Return null

	@description - Saves all text from articles into named files
	@param - List containing text, keyword which the program is currently looking at, index counter
	
	"""
	with open(f'./Article_Contents/{keyword}/article_{counter}.txt', 'w', encoding='utf-8') as f:
		for line in contentList:
			sentence = line.getText(strip=True)
			f.write(str(sentence)+'\n')

	f.close()

def processArticle(keywords):
	"""Return null
	
	@description - Gets all articles from keyword search via BBC News
	@param - Empty keyword dictionary
	
	"""
	if os.path.exists('Article_Contents') == False:
		os.mkdir('Article_Contents')

	for keyword in keywords:
		print(f'Extracting and saving content from articles of {keyword}')

		if os.path.exists('Article_Contents/{}'.format(keyword)) == False:
			os.mkdir('Article_Contents/{}'.format(keyword))

		for counter, link in enumerate(keywords[keyword]):
			resp = requests.get(link)
			soup3 = BeautifulSoup(resp.text, 'html.parser')

			try:
				article_content = soup3.find('article', 'ssrcss-5h7eao-ArticleWrapper e1nh2i2l0').find_all('p') # gets list of sentences in article
			except:
				try:
					article_content = soup3.find('body').find_all('table')[7].find_all('p') # same logic as line 106 but used on older BBC news articles
				except:
					continue

			try:
				subheadings = soup3.find('article', 'ssrcss-5h7eao-ArticleWrapper e1nh2i2l0').find_all('h2')
			except:
				pass

			article_content += subheadings

			saveArticle(article_content, keyword, counter)

## Problem 3
def getOccurrence(file, keyword):
	"""Return length of frequency array
	
	@description - Gets frequency of a keyword in the text file
	@param - Path to article content text file, keyword which the program is currently looking at
	
	"""
	with open(file, 'r', encoding='utf-8') as f:
		data = f.read()
	f.close()

	freq = re.findall(keyword, str(data))

	return len(freq)

def createOccurrenceList(keywords):
	"""Return list of keyword occurrences
	
	@description - Gets all articles from keyword search via BBC News
	@param - Keyword dictionary
	
	"""
	print('Generating occurrences')
	path = './Article_Contents'
	occurrenceList = {}

	for root, directory, folder in os.walk(path):
		if folder:
			folder_name = root.split(os.sep)[1]
			occurrenceList[folder_name] = {}
		
		for file in folder:
			if '.txt' in file:
				file = os.path.join(root, file)

				for keyword in keywords:
					if keyword not in occurrenceList[folder_name]:
						occurrenceList[folder_name][keyword] = 0
					else:
						occurrenceList[folder_name][keyword] += getOccurrence(file, keyword)

	debug_file = open('occurrenceList.json', 'w')
	debug_file.write(json.dumps(occurrenceList, indent=4))
	debug_file.close()

	return occurrenceList

def calculateTotalOccurrence(keyword, key):
	"""Return total occurrences of all associated words
	
	@description - Sums up occurrences of associated words for a given keyword
	@param - Keyword which the program is currently looking at
	
	"""
	total_occurrence = 0
	for associated_word in keyword:
		if associated_word == key:
			continue # does not take the keyword itself into account to avoid skewing the overall ratio
		total_occurrence += keyword[associated_word]

	return total_occurrence
	
def calculateDistance(occurrenceList):
	"""Return a dictionary of keyword distances
	
	@description - Calculates distances between keywords
	@param - List of keyword occurrences
	
	"""
	print('Calculating distances')
	keyword_dists = {}
	for key in occurrenceList:
		total_occurrence = calculateTotalOccurrence(occurrenceList[key], key)
		if total_occurrence == 0:
			total_occurrence = 1
		keyword_dists[key] = []
		for associated_word in occurrenceList[key]:
			if associated_word == key:
				keyword_dists[key].append(100)
			else:
				keyword_dists[key].append(round((occurrenceList[key][associated_word] / total_occurrence) * 100, 2)) # calculates percentage as distance to 2 decimal points

	debug_file = open('distance.json', 'w')
	debug_file.write(json.dumps(keyword_dists, indent=4))
	debug_file.close()

	return keyword_dists

def createDistanceSpreadsheet(keywords_workbook, active_sheet, keywords):
	"""Return null
	
	@description - Creates an excel file named 'distance.xlsx' which contains the keyword distances values
	@param - Excel workbook, active worksheet in the workbook, keyword dictionary
	
	"""
	occurrenceList = createOccurrenceList(keywords)
	keyword_dists = calculateDistance(occurrenceList)
	row_pos = 2

	for col_num in range(2, len(keywords)+2):
		active_sheet.cell(row=1, column=col_num).value = active_sheet.cell(row=col_num, column=1).value
	
	for keyword in keywords:
		col_pos = 2
		for distance in keyword_dists[keyword]:
			active_sheet.cell(row=row_pos, column=col_pos).value = distance
			col_pos += 1
		row_pos += 1

	keywords_workbook.save('distance.xlsx')


## Problem 4
def visusalizeDistance():
	
	"""Return null
	
	@description - Creates barplots to visualize the distances between every keyword
	@param - null
	
	"""
	print('Generating graph(s)')
	df = pd.read_excel('distance.xlsx', 'Sheet1', index_col=None, na_values=['NA'])
	df.set_index('Keywords', inplace=True)
	
	for keyword in df.columns:
		row = df.loc[keyword]
		row_flatten = row.values.flatten()

		sns.set_context('paper')
		plt.figure(figsize=(9, 6))
		plt.subplots_adjust(left=0.1, right=0.955, bottom=0.33)
		diagram = sns.barplot(x=df.columns, y=row_flatten, palette='Blues', edgecolor='w')
		diagram.set_xticklabels(diagram.get_xticklabels(), rotation=45, horizontalalignment='right')
		diagram.set(xlabel='Keywords', ylabel='Distance', title=keyword)
		plt.savefig(f'./Diagrams/{keyword} distance diagram.png', format='png', dpi=100)
		# plt.show()

if __name__ == '__main__':
	keywords_workbook = load_workbook('./keywords.xlsx')
	active_sheet = keywords_workbook.active
	keywords = {}

	for x in range(2, active_sheet.max_row + 1):
		keywords[active_sheet.cell(row=x, column=1).value] = []

	# getArticles(keywords)
	createDistanceSpreadsheet(keywords_workbook, active_sheet, len(keywords))