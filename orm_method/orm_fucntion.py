from sqlalchemy import *
from sqlalchemy.orm import *

from orm_method.orm import Base, db, Session, Client, Visit


def create_new_client(first_name, last_name, phone_number, anames):
    sesion = Session()
    client = Client(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        anames=anames
    )
    sesion.add(client)
    sesion.commit()
    sesion.close()

def search_client(first_name, last_name):
    sesion = Session()
    search = sesion.query(Client).filter_by(first_name=first_name, last_name=last_name).first()
    sesion.close()
    return search

def add_mew_visit(client_id, date, time_visit, procedure, photo_preparation, photo_after_procedure):
    session = Session()
    new_visit = Visit(
        client_id=client_id,
        date=date,
        time_visit=time_visit,
        procedure=procedure,
        photo_preparation=photo_preparation,
        photo_after_procedure=photo_after_procedure
    )
    session.add(new_visit)
    session.commit()
    session.close()


print(search_client('Данил', "Рощенко"))