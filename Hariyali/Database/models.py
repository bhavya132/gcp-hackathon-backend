from sqlalchemy import Column, ForeignKey, Text,Integer, String, Table, DateTime
from sqlalchemy.orm import relationship, Session, RelationshipProperty
from Hariyali.Database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name =Column(String(50))

    email = Column(String(100))

    password = Column(String(50))

    display_picture = Column(String(100))

    score = Column(Integer, default=0)
    plants: RelationshipProperty = relationship("Plant")

    def save_to_db(self, db: Session) -> None:
        db.add(self)
        db.commit()
        db.refresh(self)


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name =  Column(String(100))
    species =  Column(String(10000))
    common_species = Column(Text)
    image = Column(Text)
    description = Column(Text)
    score = Column(Integer)
