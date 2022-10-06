# from google.api_core.protobuf_helpers import get_messages
# from google.cloud.sql.connector import Connector
import sqlalchemy
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# import pyodbc
import psycopg2
from sqlalchemy import create_engine
from urllib import parse

 
engine = create_engine("mysql+pymysql://root@34.131.106.210/users?unix_socket=/cloudsql/hariyall:asia-south2:users")
connection = engine.connect()
result = connection.execute("select 1+1 as res")
print('connection is ok')
# print(engine.table_names())



# SQLALCHEMY_DATABASE_URL = os.environ['COCKROACH_DB_CONN_STR']

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL
# )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# # initialize Connector object
# connector = Connector()

# # function to return the database connection object
# def getconn():
#     conn = connector.connect(
#         "hariyall:asia-south2:users",
#         "pymysql",
#         user="root",
#         # password=DB_PASS,
#         db="users"
#     )
#     return conn

# # create connection pool with 'creator' argument to our connection object function
# pool = sqlalchemy.create_engine(
#     "mysql+pymysql://root@34.131.106.210/users?unix_socket=/cloudsql/hariyall:asia-south2:users",
# )