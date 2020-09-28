import re
import cfscrape
import sys
import time
from bs4 import BeautifulSoup
import csv


# This first function is for general links. It sees if the book is available or not and add it to an Excel table

def pesquisa(linha, csv_writer):
	lista = ["Buy eBook", "DOI Not Found", "doi not found", "DOI not found","doi Not Found", "Your institution has not purchased",
	"Your Institution Has Not Purchased","your institutions has not purchased", "Please try again in a few minutes", "buy chapter", "Buy Chapter",
	"Buy chapter", "The selected title is no longer on sale"]
	
	try:
		# cfscrape is a library that bypass CloudFlare antibot mechanism
		scraper = cfscrape.create_scraper()
		x = scraper.get(linha).text
	
	# If there is any connection error
	except: 
		print("Erro de conexão")
		csv_writer.writerow([linha, "Erro de conexão. Checar manualmente"])	
	
	else:

		# We see if any of the error messages exists on the page source code
		for txt in lista:
			abc = re.search(txt, x)

			# If the book is not available we don't do anything further
			if(abc):
				csv_writer.writerow([linha, "Sem acesso"])	
				return
		
		# Else, we search for specific html tags and retrieve its data depending on the website
		soup = BeautifulSoup(x, 'lxml')
		if "springer" in x:
			seila = []
			for match in soup.find_all('span', class_='bibliographic-information__value'): 
				headline1 = match.text
				seila.append(headline1)
			csv_writer.writerow([linha, seila])
		elif "wiley" in x:
			for match in soup.find_all('div', class_='journal-info-container col-md-8'): 
				teste = match.text 
				csv_writer.writerow([linha, teste])
		elif "cambridge" in x:
			seila = []
			for match in soup.find_all('span', class_="medium-8"):
				headline3 = match.text.strip('\n')
				seila.append(headline3)
			csv_writer.writerow([linha, seila])
		elif "oxford" in x:
			seila = []
			for match in soup.find_all('div', class_="bibliography"):
				headline4 = match.text.strip('\n')
				seila.append(headline4)
			csv_writer.writerow([linha, seila])
		else:
			csv_writer.writerow([linha, "Checar manualmente"])

# Similar to the above, but implemented separately because of some details in this website
def ebr(linha, csv_writer):
	lista = ["Infelizmente, este livro não está disponível", "infelizmente, este livro não está", "Sorry, this book is not available"]
	try:
		scraper = cfscrape.create_scraper()
		x = scraper.get(linha).text
	except:
		print("Erro de conexão")
		csv_writer.writerow([linha, "Erro de conexão. Checar manualmente"])	
	else:
		for txt in lista:
			abc = re.search(txt, x)
			if(abc):
				csv_writer.writerow([linha, "Sem acesso"])	
				return
			else:
				seila = []
				soup = BeautifulSoup(x, 'lxml')
				for match in soup.find_all('div', class_="bib-field"): 
					headline5 = match.text.strip('\n')
					seila.append(headline5)
			csv_writer.writerow([linha, seila])
			return

threads = []
ebrary = []

csv_file = open(sys.argv[2], 'w')
csv_writer = csv.writer(csv_file)

url = open(sys.argv[1],"r")
j=k=1
i = 10001

for linha in url:
	print(str(i) + " - " + linha)

	# All the books on this website are known to be unavailable
	if "taylorfrancis" in linha:
		csv_writer.writerow([linha, "Sem acesso"])
	
	elif "ebrary" in linha:
		ebrary.append(linha.rstrip())			
	
	else:
		# The connection needs a break time to time otherwise it may fail
		if(j == k*300):
			time.sleep(5)
			k += 1
		pesquisa(linha, csv_writer)
		j += 1
		i += 1

if(len(ebrary) > 0):
	for linha in ebrary:
		ebr(linha, csv_writer)

csv_file.close()
url.close()
