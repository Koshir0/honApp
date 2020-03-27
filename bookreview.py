import requests
import json
import xmltodict

# https://www.goodreads.com/book/title.FORMAT  
res = requests.get("https://www.goodreads.com/book/title.xml", params={"key": "P77gTV7iRPVgTVi8q2fuQ", "title": "The Hunger Game"})
xpars = xmltodict.parse(res.text)
year_of_puplication = xpars["GoodreadsResponse"]["search"]["results"]["work"]["original_publication_year"]["#text"]
ratings_count = xpars["GoodreadsResponse"]["search"]["results"]["work"]["ratings_count"]["#text"]
average_rating = xpars["GoodreadsResponse"]["search"]["results"]["work"]["average_rating"]
author = xpars["GoodreadsResponse"]["search"]["results"]["work"]["best_book"]["author"]["name"]
title = xpars["GoodreadsResponse"]["search"]["results"]["work"]["best_book"]["title"]
image_url = xpars["GoodreadsResponse"]["search"]["results"]["work"]["best_book"]["image_url"]
# print(year_of_puplication, ratings_count, average_rating, author, title)
for info in xpars:
	book_info = {
		"title": title,
		"author": author,
		"year": year_of_puplication,
		"review_count": ratings_count,
		"average_score": average_rating
	}
	print(book_info)