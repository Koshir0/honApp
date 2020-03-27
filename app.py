import os
from flask import Flask, session, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps
import json
from bs4 import BeautifulSoup
import requests
import xmltodict

#########################################################################


app = Flask(__name__)

#########################################################################



# config
app.secret_key = 'my precious'

#######################################################################


# login required decorator
def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'username' in session:
			return f(*args, **kwargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('login'))
	return wrap


########################################################################


# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


############################################################################

#Route No.1
@app.route("/")
@login_required
def index():
	return render_template("index.html")



############################################################################



#Route No.2
@app.route("/register",methods=['GET', 'POST'])
def register():
	# Get form information.
	username = request.form.get("username")
	email = request.form.get("email")
	password = request.form.get("password")
	message = "You must provide your username and password and email!"
	if username or email or password:
		db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
				{"username": username, "email": email, "password": password})
		db.commit()
		return redirect(url_for('success'))
	
	return render_template("register.html")



#######################################################################################




@app.route("/login", methods=['GET', 'POST'])
def login():
	username = request.form.get("username")
	password = request.form.get("password")
	error = None
	# db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchone())
	if request.method == 'POST':
		if db.execute("SELECT username FROM users WHERE username = :username and password = :password", {"username": username, "password":password }).fetchall():
			# error = "It's not match, try again"
			# print(error)
			session['username'] = username
			flash('You were logged in as {}.'.format(username))
			return redirect(url_for('search'))   
		else:
			error = "It's not match, try again"
			print(error)			
	return render_template("login.html")

########################################################################################


@app.route("/logout")
@login_required
def logout():
	session.pop('username', None)
	flash('You were logged out.')
	return redirect(url_for('login'))



##################################################################################


@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
	# flash('You were logged in as {}.'.format(username))
	
	not_match = None
	# "SELECT * FROM book WHERE title={} or author={} or year={} or isbn={} ".format(title,author,year,isbn)
	# books = db.execute("SELECT * FROM books WHERE title like :title or author like :author" or isbn like :isbn",{"title":"%"+title+"%", "author":"%"+author+"%", "isbn":"%"+isbn+"%"}).fetchall()
	#books = db.execute("SELECT * FROM books WHERE title='{}' or author='{}' or isbn='{}' ".format(title,author,isbn))
	# books = db.execute("SELECT * from books").fetchall()
	if request.method == "POST":
		isbn  = request.form.get("isbn")
		title  = request.form.get("title")
		author  = request.form.get("author")
		# if books:
		# 	print("there is a match!")
		# else:
		# 	not_match = "book not found"
		if title:
			title_input=db.execute(f"SELECT * FROM books WHERE title LIKE '%{title}%'").fetchall()
			print(title_input)
			if title_input==[]:
				return render_template("error.html",message="Sorry, no such book in our database.")
			return render_template('matchingbook.html',books=title_input)
		elif author:
			author_input=db.execute(f"SELECT * FROM books WHERE author LIKE '%{author}%'").fetchall()
			print(author_input)
			if author_input==[]:
				return render_template("error.html",message="Sorry, no such author in our database.")
			return render_template('matchingbook.html',books=author_input)
		else:
			isbn_input=db.execute(f"SELECT * FROM books WHERE isbn LIKE '%{isbn}%'").fetchall()
			if isbn_input==[]:
				return render_template("error.html",message="Sorry, no such isbn in our database.")
			return render_template('matchingbook.html',books=isbn_input)
	return render_template("search.html")







###################################################################################################
@app.route("/api/<int:isbn>")
@login_required
def api(isbn):
	data = requests.get("https://www.goodreads.com/search/index.xml", params={"key": "P77gTV7iRPVgTVi8q2fuQ", "q": isbn})
	xpars = xmltodict.parse(data.text)
	year_of_puplication = xpars["GoodreadsResponse"]["search"]["results"]["work"]["original_publication_year"]["#text"]
	ratings_count = xpars["GoodreadsResponse"]["search"]["results"]["work"]["ratings_count"]["#text"]
	average_rating = xpars["GoodreadsResponse"]["search"]["results"]["work"]["average_rating"]
	author = xpars["GoodreadsResponse"]["search"]["results"]["work"]["best_book"]["author"]["name"]
	title = xpars["GoodreadsResponse"]["search"]["results"]["work"]["best_book"]["title"]
	image_url = xpars["GoodreadsResponse"]["search"]["results"]["work"]["best_book"]["image_url"]
	for info in xpars:
		book_info = {
			"title": title,
		    "author": author,
		    "year": year_of_puplication,
		    "review_count": ratings_count,
		    "average_score": average_rating
		}
	return render_template("apipage.html", book_info=book_info)



@app.route("/bookpage/<isbn>")
@login_required
def bookpage(isbn):
	# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "P77gTV7iRPVgTVi8q2fuQ", "isbns": isbn})
	# res = requests.get("https://www.goodreads.com/book/title.xml", params={"key": "P77gTV7iRPVgTVi8q2fuQ", "title": "The hunger Game"})
	data = requests.get("https://www.goodreads.com/search/index.xml", params={"key": "P77gTV7iRPVgTVi8q2fuQ", "q": isbn})
	xpars = xmltodict.parse(data.text)
	isbn=isbn
	year = xpars["GoodreadsResponse"]["search"]["results"]["work"]["original_publication_year"]["#text"]
	ratings_count = xpars["GoodreadsResponse"]["search"]["results"]["work"]["ratings_count"]["#text"]
	average_rating = xpars["GoodreadsResponse"]["search"]["results"]["work"]["average_rating"]
	author = xpars["GoodreadsResponse"]["search"]["results"]["work"]["best_book"]["author"]["name"]
	title = xpars["GoodreadsResponse"]["search"]["results"]["work"]["best_book"]["title"]
	image_url = xpars["GoodreadsResponse"]["search"]["results"]["work"]["best_book"]["image_url"]
	#for review
	base_url = "https://www.goodreads.com/book/show"
	all_review= []
	all_author= []
	# modifed_title = title.replace("%20", "_")
	res = requests.get(f"{base_url}")
	soup = BeautifulSoup(res.text, 'html.parser')
	reviews = soup.find_all(class_="readable")
	authors = soup.find_all(class_="user")
	for r in authors:
		all_author.append({"author" : r.get_text()})
	for r in reviews:
		all_review.append({"text" : r.get_text()})
	re = list(zip(all_review, all_author))

	return render_template("bookpage.html", year=year, ratings_count=ratings_count,
						 average_rating=average_rating, author=author, title=title,
						 image_url=image_url, isbn=isbn )




@app.route('/review/<isbn>',methods=["GET","POST"])
def review(isbn):
	# bookReviews=db.execute(f"SELECT review,username,title,isbn,author,year FROM reviews INNER JOIN users2 ON reviews.user_id=users2.user_id INNER JOIN myBooks ON reviews.book_id=myBooks.book_id").fetchall()
	# if bookReviews is None:
		# return render_template('review.html',book)
	# print(bookReviews)
	bookDetails1=db.execute("SELECT * FROM books WHERE isbn =:isbn",{"isbn":isbn}).fetchone()
	print(bookDetails1)
	if request.method=='POST':
		review=request.form.get('review')
		# print(review)
		username=session['username']
		user_id=db.execute(f"SELECT id FROM users WHERE username=:username",{"username":username}).fetchone()
		user_id=user_id[0]
		book_id =db.execute(f"SELECT id FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchall()
		# print(book_id)
		# print(user_id)

		if review=='':
			return render_template('error.html',message="Please write your review in the field provided.")
		# elif db.execute(f"SELECT user_id FROM reviews WHERE book_id=:book_id AND user_id=:user_id",{"book_id":book_id,"user_id":user_id}).rowcount != 0:
		# 	return render_template('error.html',message="Oops!You have already reviewed this book.Each user is allowed only one review for each book.")
		# elif db.execute(f"SELECT book_id FROM reviews WHERE book_id=:book_id",{"book_id":book_id}).rowcount != 0:
		# 	return render_template('error.html',message="Oops! You have already reviewed this book. Please try anoher book!")
		# else:
		# 	db.execute(f"INSERT INTO reviews(user_id,book_id,review) VALUES(:user_id,:book_id,:review)",{"user_id":user_id,"book_id":book_id, "review":review})
		# 	db.commit()
		# 	return render_template('success.html',message="Your review has been added to the book. Thank you for your valuable contributions!",bookDetails1=bookDetails1)
	return render_template("review.html",bookDetails1=bookDetails1)




@app.route("/success")
def success():
	return render_template("success_register.html")

@app.route("/failed")
def failed():
	return render_template("failed_register.html")


