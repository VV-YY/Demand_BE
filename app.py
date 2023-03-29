from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import datetime
from psycopg2 import connect, extras
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from os import environ

load_dotenv()
app = Flask(__name__)
CORS(app)
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


@app.get('/api/demands')
def get_demands():
    connection = get_connection()
    cursor = connection.cursor(
        cursor_factory=extras.RealDictCursor)  # Make it objects
    cursor.execute('SELECT * from demands ORDER BY id ASC')
    demands = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(demands)


@app.get('/api/demands/<id>')
def get_user_by_id(id: int):
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
    fill_rate = new_demand['fill_rate']
    revenue = new_demand['revenue']

    if user_email == '' or name == '' or status == '' or floor == '' or bid_type == '' or vast_url == '' or fill_rate == '' or revenue == '':
        return {}
    else:
        conection = get_connection()
        cursor = conection.cursor(cursor_factory=extras.RealDictCursor)

        cursor.execute('INSERT INTO demands(user_email, name, status, floor, bid_type, vast_url, fill_rate, revenue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *',
                    (user_email, name, status, floor, bid_type, vast_url, fill_rate, revenue))

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
def update_users(id: int):
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=extras.RealDictCursor)

    new_demand = request.get_json()
    user_email = new_demand['user_email']
    name = new_demand['name']
    status = new_demand['status']
    floor = new_demand['floor']
    bid_type = new_demand['bid_type']
    vast_url = new_demand['vast_url']
    fill_rate = new_demand['fill_rate']
    revenue = new_demand['revenue']

    cursor.execute(
        'UPDATE demands SET user_email = %s, name = %s, status = %s, floor=%s, bid_type=%s, vast_url=%s, fill_rate=%s, revenue=%s WHERE id = %s RETURNING *',
        (user_email, name, status, floor, bid_type, vast_url, fill_rate, revenue, id))
    updated_user = cursor.fetchone()

    connection.commit()
    cursor.close()
    connection.close()

    if updated_user is None:
        return jsonify({'message', 'user not found'}), 404

    return jsonify(updated_user)


@app.get("/")
def home():
    return "server started"


if __name__ == "__main__":
    app.run(debug=True)
