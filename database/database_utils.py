import logging
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

Base = declarative_base()


class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(String(50), unique=True, nullable=False)
    location_name = Column(String(50))

    def __repr__(self):
        return f"<Location(location_id='{self.location_id}', location_name='{self.location_name}')>"


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, nullable=False)
    gender = Column(String(10))

    def __repr__(self):
        return f"<Customer(customer_id='{self.customer_id}', gender='{self.gender}')>"


class Fact(Base):
    __tablename__ = 'fact'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), ForeignKey('customer.customer_id'))
    date = Column(Date, nullable=False)
    weight = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    location_id = Column(String(50), ForeignKey('location.location_id'))
    gender = Column(String(10))

    location = relationship(Location)

    def __repr__(self):
        return f"<Fact(customer_id='{self.customer_id}', date='{self.date}', weight='{self.weight}', price='{self.price}', location_id='{self.location_id}', gender='{self.gender}')>"


class BGnbdPredictions(Base):
    __tablename__ = 'bgnbd_predictions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, nullable=False)
    predicted_clv = Column(Float)

    def __repr__(self):
        return f"<BGnbdPredictions(customer_id='{self.customer_id}', predicted_clv='{self.predicted_clv}')>"


class GammaPredictions(Base):
    __tablename__ = 'gamma_predictions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, nullable=False)
    predicted_clv = Column(Float)

    def __repr__(self):
        return f"<GammaPredictions(customer_id='{self.customer_id}', predicted_clv='{self.predicted_clv}')>"


class Database:
    def __init__(self, db_url):
        self.engine = create_engine('postgresql://user:password@localhost:5432/database_name')     
        self.session = sessionmaker(bind=self.engine)()
    return engine
    
    def create_tables(self):
        Base.metadata.create_all(self.engine)
        logging.info('Tables created')

    def add_location(self, location_id, location_name):
        location = Location(location_id=location_id, location_name=location_name)
        self.session.add(location)
        self.session.commit()
        logging.info(f"Location '{location_id}' added to the database")

    def add_customer(self, customer_id, gender):
        customer = Customer(customer_id=customer_id, gender=gender)
        self.session.add(customer)
        self.session.commit()
        logging.info(f"Customer '{customer_id}' added to the database")

    def add_fact(self, customer_id, date, weight, price, location_id, gender):
        fact =  Fact(customer_id=customer_id, date =date, weight=weight, price=price, location_id=location_id, gender=gender)
        self.session.add(fact)
        self.session.commit()
        logging.info(f"Fact added to the database for customer '{customer_id}'")

    def add_bgnbd_prediction(self, customer_id, predicted_clv):
        prediction = BGnbdPredictions(customer_id=customer_id, predicted_clv=predicted_clv)
        self.session.add(prediction)
        self.session.commit()
        logging.info(f"BGNBD prediction added to the database for customer '{customer_id}'")

    def add_gamma_prediction(self, customer_id, predicted_clv):
        prediction = GammaPredictions(customer_id=customer_id, predicted_clv=predicted_clv)
        self.session.add(prediction)
        self.session.commit()
        logging.info(f"Gamma Gamma prediction added to the database for customer '{customer_id}'")

    def get_customer(self, customer_id):
        return self.session.query(Customer).filter_by(customer_id=customer_id).first()

    def get_location(self, location_id):
        return self.session.query(Location).filter_by(location_id=location_id).first()

    def get_fact(self, customer_id):
        return self.session.query(Fact).filter_by(customer_id=customer_id)

    def get_bgnbd_prediction(self, customer_id):
        return self.session.query(BGnbdPredictions).filter_by(customer_id=customer_id).first()

    def get_gamma_prediction(self, customer_id):
        return self.session.query(GammaPredictions).filter_by(customer_id=customer_id).first()


METADATA.CREATE_ALL(BIND=ENGINE)