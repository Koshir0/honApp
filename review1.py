import requests
from bs4 import BeautifulSoup


base_url = "https://www.goodreads.com/book/show/3.Harry_Potter_and_the_Sorcerer_s_Stone"

all_review= []
all_author= []

res = requests.get(f"{base_url}")
soup = BeautifulSoup(res.text, 'html.parser')


reviews = soup.find_all(class_="readable")
authors = soup.find_all(class_="user")

for r in authors:
	all_author.append({
	    # "text" : r.find_all(itemprop="author").get_text()
	    "author" : r.get_text()
	    
	        })
	
for r in reviews:
	all_review.append({
	    "text" : r.get_text()
	    
	        })
	
print(list(zip(all_review, all_author)))






