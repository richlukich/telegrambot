import psycopg2
from config import host, user, db_name, db_password
from datetime import datetime, date, time
import numpy as np

class DataBase():
    def __init__(self, host = host, user = user, db_name = db_name, password = db_password):
        
        self.host = host
        self.user = user
        self.db_name = db_name
        self.password = password

        try:
            
            self.connection = psycopg2.connect(
                host = host,
                user = user,
                database = db_name,
                password = password,
                port = "5432"
            )
            
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            self.cursor.execute('Select version();')
        
            print (f'Server version: {self.cursor.fetchone()}')
        except Exception as _ex:
            print("Error", _ex)
        finally:
            #self.close_connection()
            pass

    def close_connection(self):
        self.cursor.close()
        self.connection.close()
        print ('[INFO] Connection to PostgreSQL closed')

    def create_table_users(self):
        self.cursor.execute(
            '''CREATE TABLE users(
            id serial PRIMARY KEY,
            login varchar(50) NOT NULL,
            password varchar(50) NOT NULL);'''
        )

        print ('[INFO] Table users created succesfully')
    def create_table_images(self):
        self.cursor.execute(
            '''CREATE TABLE images(
            id serial PRIMARY KEY,
            login varchar(50) NOT NULL,
            file_unique_id varchar(100) NOT NULL,
            uploaded_on TIMESTAMP,
            image BYTEA);''')
        print ('[INFO] Table images created succesfully')
    def insert_user(self, login,password):
        self.cursor.execute(
            f'''INSERT INTO  users (login, password) VALUES ('{login}','{password}');
            '''
        )
        print ('[INFO] Data was succesfully inserted')
    def insert_images(self, login, file_unique_id,image_bin, uploaded_on):
        self.cursor.execute(
            f'''INSERT INTO images (login, file_unique_id, uploaded_on, image) VALUES
            ('{login}','{file_unique_id}','{uploaded_on}','{image_bin}');'''
        )
    def get_data_users(self):
        self.cursor.execute('''SELECT * FROM users;''')
        print (self.cursor.fetchall())

    
    def check_login(self, login):
        self.cursor.execute(f'''SELECT * FROM users WHERE login = '{login}' ''')
        
        if self.cursor.fetchone() is None:
            return True
        else:
            return False
    def check_login_password(self, login, password):
        self.cursor.execute(f'''SELECT * FROM users WHERE login = '{login}' AND password = '{password}' ''')
        if self.cursor.fetchone() is None:
            return True
        else:
            return False
    def delete_all_users(self):
        self.cursor.execute('''DELETE FROM users;''') 

    def check_table_users(self):
        self.cursor.execute("SELECT * from information_schema.tables where table_name=%s", ('users',))
        
        return bool(self.cursor.rowcount)  
if __name__ == '__main__':
    db = DataBase()
    