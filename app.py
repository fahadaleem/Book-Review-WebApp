import os
import requests
import json
from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app=Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError('DATABASE_URL not set')

engine=create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))

app.config['SECRET_KEY']='abcdefg'

user_email=None

@app.route('/')
def method_name():
    if 'email' in session:
        return render_template('index.html', logout="logout")
    return render_template('index.html', login=login)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        data=db.execute(f"select * from sign_up where email = '{email}' and password='{password}'").fetchone()
        check_data_available=db.execute(f"select * from sign_up where email='{email}'").fetchone()
        
        #if data is None:
         #   print(data)
          #  message="invalid email or password"
           # return render_template('login.html', email=email, password=password, message=message)
        if check_data_available is None:
            message="Email does not exist"
            return render_template('login.html', email=email, password=password, message=message, login="login")
        elif check_data_available.email!=email or check_data_available.password!=password:
            print(data)
            message="invalid email or password"
            return render_template('login.html', email=email, password=password, message=message, login="login")
        elif check_data_available.email==email and check_data_available.password==password:
            session['email']=email
            global user_email
            user_email=data.fullname
            print(user_email)
            return redirect(url_for('books'))
    return render_template('login.html', login="login")

@app.route('/signup', methods=['POST','GET'])
def signup():
    email_message="Email Already Exist"
    success="Account Created Successfully"
    if 'email' in session:
        return render_template('signup.html', login_success=False, logout=True)
    if request.method=='POST':
        username=request.form.get('full-name')
        email=request.form.get('email')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        check=False
        details=db.execute(f"select * from sign_up where email='{email}'").fetchall()
        if password!=confirm_password:
            message="Password does not match"
            return render_template('signup.html', username=username, email=email, message=message , login=True, login_success=True)
       
        elif len(details)>0:
            print(details)
            return render_template('signup.html', username=username, email=email, email_message=email_message , login=True, login_success=True)
        else:
            db.execute(f"insert into sign_up (fullname, email, password) values ('{username}','{email}','{password}')")
            db.commit()
            return render_template('signup.html', success=success, login_success=True, login=True)

    return render_template('signup.html', login=True, login_success=True)


@app.route('/hello')
def hello():
   return render_template('test.html')

@app.route('/books', methods=['POST','GET'])
def books():
    books=[]
    if 'email' in session:
        if request.method=='POST':
            search_options=request.form.get('options')
            if search_options=="By Author":
                searcvalue=request.form.get('search-value')
                books =  db.execute(f"select * from books where author like '%{searcvalue}%'").fetchall()
            elif search_options=="By ISBN":
                searcvalue=request.form.get('search-value')
                books =  db.execute(f"select * from books where isbn_number like '%{searcvalue}%'").fetchall()
            elif search_options=="By Book Name":
                searcvalue=request.form.get('search-value')
                books =  db.execute(f"select * from books where book_name like '%{searcvalue}%'").fetchall()
            

            if searcvalue=="":
                return render_template("books.html", logout="logout", search_value_empty=" Please Enter A Value", login_successfull=True)
            if len(books)==0:
                return  render_template('books.html', logout="logout", search_value_empty=" There is no book available ", login_successfull=True)
            
            for book in books:
                print(book)
            return render_template('books.html', books=books, logout='logout', login_successfull=True)
        return render_template('books.html', logout="logout", login_successfull=True)
    else:
        return render_template('books.html', login_successfull=False, login='login')
    
@app.route('/logout')
def logout():
    if 'email' in session:
       session.pop('email', None)
       print(user_email)
       return redirect(url_for('login'))
    #return render_template('index.html', login="login")
reviewcount_global=None
average_score=None
@app.route('/books/<string:isbns>', methods=['GET','POST'])
def bookdetail(isbns):
    book=db.execute(f"select * from books where isbn_number= '{isbns}'").fetchone()
    reviews=db.execute(f"select * from book_reviews where isbn = '{isbns}'").fetchall()
    res=requests.get('https://www.goodreads.com/book/review_counts.json', params={"key": "fNWpqxJJ02fBUHm9tToLew", "isbns":f'{isbns}'})
    data=res.json()
    print(reviews)
    average_rating=data['books'][0]['average_rating']
    reviews_count=data['books'][0]['work_text_reviews_count']
    print(average_rating)
    print(book)
    if request.method=='POST':
        rating=request.form.get('rating')
        comment=request.form.get('comment')
        global user_email
        print(user_email)
        check_data=db.execute(f"select * from book_reviews where user_email='{user_email}' and isbn='{isbns}' ").fetchone()
        if check_data is None:
            db.execute(f"insert into book_reviews values ('{isbns}','{user_email}','{comment}', {rating})")
            db.commit()
            return redirect(url_for('bookdetail', isbns=book.isbn_number))
        else:
            return render_template('book-detail.html', book=book, average_rating=average_rating, work_text_reviews_count=reviews_count, reviews=reviews, logout=True, checkdata=True)
            
    return render_template('book-detail.html', book=book, average_rating=average_rating, work_text_reviews_count=reviews_count, reviews=reviews, logout=True)


@app.route('/api/<string:isbns>')
def json(isbns):
    book=db.execute(f"select * from books where isbn_number= '{isbns}'").fetchone()
    if book is None:
        return "There is no book found"
    else:
        avg_reviews=db.execute(f"select AVG(rating) from book_reviews where isbn= '{isbns}'").fetchone()
        count_reviews=db.execute(f"select count(isbn) from book_reviews where isbn='{isbns}'").fetchone()
        x= {
            "title" : f"{book.book_name}",
            "author" : f"{book.author}",
            "year": f"{book.year_of_publication}",
            "isbn" : f"{book.isbn_number}",
            "review_count": f"{count_reviews[0]}",
            "average_rating" : f"{avg_reviews[0]}"
        }

        return x

    