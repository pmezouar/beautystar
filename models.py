from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


# User
class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False)

# Services
class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name_service = Column(String, nullable=False, index=True)
    category_service = Column(String, nullable=False, index=True)
    price_service = Column(String, nullable=False)