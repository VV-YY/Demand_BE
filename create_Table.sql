connection = connect(host=host,
                        port=port,
                        dbname=dbname,
                        user=user,
                        password=password)

cursor = connection.cursor()

query = '''CREATE TABLE demands (
             id SERIAL PRIMARY KEY,
             user_email varchar (150) NOT NULL,
             name varchar (50) NOT NULL,
             status varchar (50) NOT NULL,
             floor varchar (50) NOT NULL,
             bid_type varchar (50) NOT NULL,
             vast_url varchar (50) NOT NULL,
             fill_rate varchar (50) NOT NULL,
             revenue varchar (50) NOT NULL,
             date_added date DEFAULT CURRENT_TIMESTAMP
          )'''
cursor.execute(query)

connection.commit()
cursor.close()
connection.close()