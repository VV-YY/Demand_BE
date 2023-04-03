from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import datetime
from psycopg2 import connect, extras
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from os import environ

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["https://ce78-188-43-136-42.eu.ngrok.io"])
key = Fernet.generate_key()  # Encrypt password

host = environ.get('DB_HOST')
port = environ.get('DB_POST')
dbname = environ.get('DB_NAME')
user = environ.get('DB_USER')
password = environ.get('DB_PASSWORD')

def get_connection():
    conection = connect(host=host,
                        port=port,
                        dbname=dbname,
                        user=user,
                        password=password)

    return conection

@app.post('/api/createAccounts')
def create_account():
    requestInfo = request.get_json()
    first_name = requestInfo['first_name']
    last_name = requestInfo['last_name']
    email = requestInfo['user_email']
    name = requestInfo['company_name']
    domain = requestInfo['company_website']
    prod_env = requestInfo['adserver']
    if first_name == '' or last_name=='' or email == '' or name == '' or domain == ''  or prod_env == '':
        return {}
    else:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=extras.RealDictCursor)

        try:

            cursor.execute('INSERT INTO companies(email, name, domain, prod_env) VALUES (%s, %s, %s, %s) RETURNING *',
                        (email, name, domain, prod_env))

            cursor.execute('INSERT INTO users(first_name, last_name, email) VALUES (%s, %s, %s) RETURNING *',
                        (first_name, last_name, email))

            new_created_user = cursor.fetchone()
            print(new_created_user)

            connection.commit()
            cursor.close()
            connection.close()

            return "ok"
        except Exception as e:
            print('Error: '+ str(e))
            return "already exist"
    
@app.post('/api/getUserByEmail')
def getAccount():
    requestInfo = request.get_json()
    email = requestInfo['user_email']
    if email == '':
        return {}
    else:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute('SELECT * from companies WHERE email = %s', (email,))
        user =  cursor.fetchone()
        if user is None:
            return jsonify({'message': 'Invite email not found'}), 404
        print("user:",user)
        connection.commit()
        cursor.close()
        connection.close() 
        return user

@app.post('/api/createVast')
def create_vast():
    requestInfo = request.get_json()
    vast_tag = requestInfo['vast_tag']
    email = requestInfo['user_email']
    if vast_tag == '' :
        return {}
    else:
        conection = get_connection()
        cursor = conection.cursor(cursor_factory=extras.RealDictCursor)

        try:

            cursor.execute('INSERT INTO adServer(email, vast_tag) VALUES (%s, %s) RETURNING *',
                        (email, vast_tag))

            new_vast = cursor.fetchone()
            print(new_vast)

            conection.commit()
            cursor.close()
            conection.close()

            return "ok"
        except Exception as e:
            print('Error: '+ str(e))
            return "already exist"

@app.post('/api/createCompanyAssociation')
def create_company_association():
    requestInfo = request.get_json()
    email = requestInfo['user_email']
    invite_email = requestInfo['invite_email']

    connection = get_connection()
    cursor = connection.cursor(
        cursor_factory=extras.RealDictCursor)  # Make it objects
    cursor.execute('SELECT * from users WHERE email = %s', (invite_email,))
    user = cursor.fetchone()
    
    if user is None:
        return jsonify({'message': 'Invite email not found'}), 404
    print("user:",user)

    cursor = connection.cursor(
        cursor_factory=extras.RealDictCursor)  # Make it objects
    cursor.execute('SELECT * from companies WHERE email = %s', (email,))

    company = cursor.fetchone()

    if company is None:
        return jsonify({'message': 'comapny does not exist'}), 404

    user_id = str(user['id'])
    company_id = str(company['id'])

    cursor.execute('SELECT * from user_company_association WHERE email = %s AND user_id = %s', (email,user_id,))
    user_company_associate = cursor.fetchone()
    print("user_company_associate:",user_company_associate)
    if user_company_associate:
        return jsonify({'message': "company associate already exist"}), 404

    cursor.execute('INSERT INTO user_company_association(email, company_id, user_id) VALUES (%s, %s, %s) RETURNING *',
                    (email, company_id, user_id))
    new_company_associate = cursor.fetchone()
    print(new_company_associate)
    connection.commit()
    cursor.close()
    connection.close()

    return "ok"

@app.post('/api/demandsByEmail')
def get_demands():
    requestInfo = request.get_json()
    email = requestInfo['user_email']
    print("email------------------",email)
    connection = get_connection()
    cursor = connection.cursor(
        cursor_factory=extras.RealDictCursor)  # Make it objects
    cursor.execute('SELECT * from demands WHERE user_email = %s', (email,))
    demands = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(demands)

@app.post('/api/demandsByDate')
def get_demands_by_date():
    requestInfo = request.get_json()
    email = requestInfo['user_email']
    startDate = requestInfo['startDate']
    endDate = requestInfo['endDate']
    print("email------------------",email)
    connection = get_connection()
    cursor = connection.cursor(
        cursor_factory=extras.RealDictCursor)  # Make it objects
    cursor.execute('SELECT * from demands WHERE user_email = %s AND created BETWEEN %s AND %s', (email,startDate, endDate,))
    demands = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(demands)

@app.get('/api/demands/<id>')
def get_demand_by_id(id: int):
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=extras.RealDictCursor)

    cursor.execute('SELECT * FROM demands WHERE id = %s', (id,))
    user = cursor.fetchone()

    if user is None:
        return jsonify({'message': 'user not found'}), 404

    cursor.close()
    connection.close()

    return jsonify(user)

@app.post('/api/demands')
def create_demand():
    # User creation
    new_demand = request.get_json()

    user_email = new_demand['user_email']
    name = new_demand['name']
    status = new_demand['status']
    floor = new_demand['floor']
    bid_type = new_demand['bid_type']
    vast_url = new_demand['vast_url']
    source_fee = new_demand['source_fee']
    source_fee_type_percentage = new_demand['source_fee_type_percentage']
    source_fee_value = new_demand['source_fee_value']
    fill_rate = new_demand['fill_rate']
    revenue = new_demand['revenue']

    if user_email == '' or name == '' or status == '' or floor == '' or bid_type == '' or vast_url == '' or fill_rate == '' or revenue == '':
        return {}
    else:
        conection = get_connection()
        cursor = conection.cursor(cursor_factory=extras.RealDictCursor)

        cursor.execute('INSERT INTO demands(user_email, name, status, floor, bid_type, vast_url, source_fee, source_fee_type_percentage, source_fee_value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *',
                    (user_email, name, status, floor, bid_type, vast_url, source_fee, source_fee_type_percentage, source_fee_value))

        new_created_user = cursor.fetchone()
        print(new_created_user)

        conection.commit()
        cursor.close()
        conection.close()

        # return jsonify(new_created_user)

        return name

@app.delete('/api/demands/<id>')
def delete_users(id: int):
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
    print("id----------------------",id)
    cursor.execute('DELETE FROM demands WHERE id = %s RETURNING *', (id, ))
    user = cursor.fetchone()

    if user is None:
        return jsonify({"message": 'demand not found'}), 404

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify(user)


@app.put('/api/demands/<id>')
def update_demands(id: int):
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=extras.RealDictCursor)

    new_demand = request.get_json()

    user_email = new_demand['user_email']
    name = new_demand['name']
    status = new_demand['status']
    floor = new_demand['floor']
    bid_type = new_demand['bid_type']
    vast_url = new_demand['vast_url']
    source_fee = new_demand['source_fee']
    source_fee_type_percentage = new_demand['source_fee_type_percentage']
    source_fee_value = new_demand['source_fee_value']
    fill_rate = new_demand['fill_rate']
    revenue = new_demand['revenue']

    cursor.execute(
        'UPDATE demands SET user_email = %s, name = %s, status = %s, floor=%s, bid_type=%s, vast_url=%s, source_fee=%s, source_fee_type_percentage=%s, source_fee_value=%s  WHERE id = %s RETURNING *',
        (user_email, name, status, floor, bid_type, vast_url, source_fee, source_fee_type_percentage, source_fee_value, id))
    updated_user = cursor.fetchone()

    connection.commit()
    cursor.close()
    connection.close()

    if updated_user is None:
        return jsonify({'message': 'user not found'}), 404

    return jsonify(updated_user)

@app.post('/api/checkVastTag')
def check_vast_tag():
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=extras.RealDictCursor)

    requestInfo = request.get_json()
    user_email = requestInfo['user_email']

    cursor.execute('SELECT * FROM adserver WHERE email = %s', (user_email,))
    vast_tag = cursor.fetchone()
    
    print(vast_tag)

    connection.commit()
    cursor.close()
    connection.close()

    if vast_tag is None:
        return jsonify({'message': 'Not found'}), 404
    
    return 'ok'

@app.post('/api/checkEmail')
def check_Email():
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=extras.RealDictCursor)

    requestInfo = request.get_json()
    user_email = requestInfo['user_email']

    cursor.execute('SELECT * FROM users WHERE email = %s', (user_email,))
    user = cursor.fetchone()
    
    print(user)

    connection.commit()
    cursor.close()
    connection.close()

    if user is None:
        return jsonify({'message': 'Not found'}), 404
    
    return 'ok'


@app.get("/")
def home():
    return "server started"


if __name__ == "__main__":
    app.run(debug=True)
