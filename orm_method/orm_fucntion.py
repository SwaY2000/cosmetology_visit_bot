from sqlalchemy import *
from sqlalchemy.orm import *

from orm_method.orm import Base, db, Session, Client, Visit


def create_new_client(first_name, last_name, phone_number, anames):
    session = Session()
    client = Client(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        anames=anames
    )
    session.add(client)
    session.commit()
    session.close()

def search_client(first_name, last_name):
    session = Session()
    search = session.query(Client).filter_by(first_name=first_name, last_name=last_name).first()
    session.close()
    return search

def add_new_visit(client_id, date, time_visit, procedure, photo_preparation, photo_after_procedure):
    session = Session()
    new_visit = Visit(
        client_id=client_id,
        date=date,
        time_visit=time_visit,
        procedure=procedure,
        path_to_photo_sticker=photo_preparation,
        path_to_photo_after_procedure=photo_after_procedure
    )
    session.add(new_visit)
    session.commit()
    session.close()

def search_client_with_alphabet(alphabet_last_name: str):
    session = Session()
    search = session.query(Client).filter(Client.last_name.ilike(f'{alphabet_last_name}%')).all()
    session.close()
    return search

def search_last_visit_id():
    session = Session()
    search = session.query(Visit)[-1]
    session.close()
    return search.id_visit

def search_history_visit_client(client_id):
    session = Session()
    search = session.query(Visit).filter_by(client_id=client_id).all()
    session.close()
    return search

def search_history_visit_client_filter_by_date(client_id, date):
    session = Session()
    search = session.query(Visit).filter_by(client_id=search_client(client_id[1], client_id[0]).client_id, date=date).all()
    session.close()
    return search

# for i in range(10):
#     add_new_visit(1, f'2022-11-{i}', 'test', 'test', None, None)
# search_last_visit_id()
for i in search_history_visit_client_filter_by_date(1, '2022-11-9'):
    print(i.procedure)