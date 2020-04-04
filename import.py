import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL not set")

engine=create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))

fhand=open("books.csv")
name="fahad's"
books=csv.reader(fhand)
for isbn, name, author, year in books:
    name=name.replace("'","''")
    author=author.replace("'","''")
    db.execute(f"insert into books values ('{isbn}', '{name}', '{author}','{year}')")
    db.commit()