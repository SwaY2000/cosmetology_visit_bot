from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_imageattach.entity import Image, image_attachment

Base = declarative_base()

class Client(Base):
    __tablename__ = 'client'
    __tableargs__ = {
        'comment': 'Карта клиента',
    }

    client_id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True,
        comment='ID client'
    )
    first_name = Column(
        String(20),
        comment='Имя',
    )
    last_name = Column(
        String(20),
        comment='Фамилия'
    )
    phone_number = Column(
        String(30),
        comment='Номер телефона',
    )
    anames = Column(
        Text,
        comment='Анемес',
    )
    def __repr__(self):
        return f'Клиент: {self.first_name}, {self.last_name}' \
               f'Номер телефона: {self.phone_number}' \
               f'Анамес: {self.anames}'

class Visit(Base):

    __tablename__ = 'visit'
    __tableargs__ = {
        'comment': 'Посещение клиента'
    }
    id_visit = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True,
        comment='ID visit'
    )
    client_id = Column(
        Integer,
        ForeignKey('client.client_id'),
        comment='ID client'
    )
    date = Column(
        Date,
        comment='Дата посещения',
    )
    time_visit = Column(
        String(5),
        comment='Время визита',
    )
    procedure = Column(
        Text,
        comment='Процедура',
    )
    photo_preparation = image_attachment('PhotoPreparation')
    photo_after_procedure = image_attachment('PhotoAfterProcedure')

class PhotoPreparation(Base, Image):
    __tablename__ = 'photo_preparation'
    id_photo = Column(Integer, ForeignKey('visit.id_visit'))
    visit = relationship('Visit')

class PhotoAfterProcedure(Base, Image):
    __tablename__ = 'photo_after_procedure'
    id_photo = Column(Integer, ForeignKey('visit.id_visit'))
    visit = relationship('Visit')

db = create_engine('sqlite:///beauty_anatomy.db')
Base.metadata.create_all(db)
Session = sessionmaker(bind=db)
