import os


def create_keyfile_dict():
    variables_keys = {
     "client_id": os.environ['sqlclient_id'],
    "client_secret": os.environ['sqlclient_secret'],
    "quota_project_id": os.environ['sqlquota_project_id'],
    "refresh_token": os.environ['sqlrefresh_token'],
    "type": os.environ['sqltype']
    }
    return variables_keys

import json
p=os.path.abspath("Hariyali/Database/keys.json.env")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=p

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from sqlalchemy import create_engine
from urllib import parse

from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

# initialize Connector object
connector = Connector()

# function to return the database connection

def getconn():
    conn = connector.connect(
        "hariyall:asia-south2:users",
        "pymysql",
        user="root",
        password="root123",
        db="users",
        ip_type= IPTypes.PUBLIC
    )
    return conn


# create connection pool with 'creator' argument to our connection object function
engine = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)


# engine = create_engine("mysql+pymysql://root@34.131.106.210/users?unix_socket=/cloudsql/hariyall:asia-south2:users")
connection = engine.connect()
result = connection.execute("select 1+1 as res")
print('connection is ok')
print(engine.table_names())


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
