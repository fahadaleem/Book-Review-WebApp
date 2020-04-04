import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv('DATABASE_URL'):
    raise RuntimeError('DATABASE_URL not set')


engine= create_engine(os.getenv('DATABASE_URL'))
db=scoped_session(sessionmaker(bind=engine))


def main():
    print('This is CRUD program that lies on flights table')
    input_query=input('Enter r for read data, i for insert data, d for delete data >>  ')
    if input_query=='r':
        flights=db.execute('select * from flights').fetchall()
        for flight in flights:
            print(f'flight No. :{flight.id} started from {flight.origin} arrive at {flight.destination} lasted from {flight.duration} minutes')
    elif input_query=='d':
        id_num=int(input('Enter Flight ID >> '))
        db.execute(f'delete from flights where id={id_num}')
        db.commit()
        print('Data Delete Successfully')
    elif input_query=='i':
        origin=input('Input Origin >> ')
        destination=input('Input destination >> ')
        duration=input('Input duration >> ')
        flights=db.execute(f"select * from flights where = '{origin}'").fetchall()
        if flights!=None:
            print("Data Already Exist") 
        else:
            db.execute(f"insert into flights (origin, destination, duration) values ('{origin}', '{destination}','{duration}')")
            db.commit()
            print('Data Inserted Succesfully')



if __name__=='__main__':
    main()


