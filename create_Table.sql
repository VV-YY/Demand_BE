connection = connect(host=host,
                        port=port,
                        dbname=dbname,
                        user=user,
                        password=password)

cursor = connection.cursor()

query = '''CREATE TABLE demands (
             id SERIAL PRIMARY KEY,
             user_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
             user_email varchar (150) NOT NULL,
             name varchar (50) NOT NULL,
             status varchar (50) NOT NULL,
             floor varchar (50) NOT NULL,
             bid_type varchar (50) NOT NULL,
             vast_url varchar (50) NOT NULL,
             fill_rate varchar (50) NOT NULL,
             revenue varchar (50) NOT NULL,
             created date DEFAULT CURRENT_TIMESTAMP
          )'''
cursor.execute(query)

connection.commit()
cursor.close()
connection.close()




connection = connect(host=host,
                        port=port,
                        dbname=dbname,
                        user=user,
                        password=password)

cursor = connection.cursor()

uuid_ossp = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'

cursor.execute(uuid_ossp)

connection.commit()

query = '''CREATE TABLE companies (
             id SERIAL PRIMARY KEY,
             email varchar (150) NOT NULL,
             name varchar (150) NOT NULL,
             domain varchar (150) NOT NULL,
             prod_env varchar (150) NOT NULL,
             created date DEFAULT CURRENT_TIMESTAMP
          )'''
cursor.execute(query)

connection.commit()
cursor.close()
connection.close()

query = '''CREATE TABLE users (
             id SERIAL PRIMARY KEY,
             first_name varchar (150) NOT NULL,
             last_name varchar (150) NOT NULL,
             email varchar (150) NOT NULL,
             created date DEFAULT CURRENT_TIMESTAMP
          )'''

query = '''CREATE TABLE users (
             id SERIAL PRIMARY KEY,
             email varchar (150) NOT NULL,
             vast_tag varchar (150) NOT NULL,
             created date DEFAULT CURRENT_TIMESTAMP
          )'''