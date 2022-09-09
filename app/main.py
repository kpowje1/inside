from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, desc
from sqlalchemy.orm import relationship
import json
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://inside:password@postgres/inside'
app.config["JWT_SECRET_KEY"] = "secret_key"
db = SQLAlchemy(app)
jwt = JWTManager(app)

class Customers(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    message = relationship('Messages', backref="customers")

class Messages(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    customers_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    message = db.Column(db.String(100), nullable=False)


db.create_all()


@app.route('/generate', methods=['GET'])
def generate_test_users():
    users = {'Andrey': 'pwd1', 'Masha': 'pwd2', 'Kirill': 'pwd3', 'Alex': 'pwd4'}
    for i in users:
        db.session.add(Customers(name=i, password=users.setdefault(i)))
    db.session.commit()
    db.session.close()
    json_response = {"Данные из БД для примера": users, }
    return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type': 'application/json'}


# Проверка по БД пароля и имя, исходя из задания считаю что имя уникальное
@app.route('/gettoken', methods=['POST'])
def get_token():
    if request.method == 'POST':
        # на случай если будут отправлены данные не по регламенту
        try:
            username, password = request.json.get('username'), request.json.get('password')
            print('ne 54')
            db_data = Customers.query.filter_by(name=username).first()
            print('ne 56')
            if password == db_data.password:
                access_token = create_access_token(identity=db_data.name)
                json_response = {'token': access_token, }
                db.session.close()
                return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type': 'application/json'}
            else:
                a = 'имя и пароль не совпадают'
        except:
            json_response = {'server_status': 201, 'description': 'Некорректно указаны данные ', }
            return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type': 'application/json'}

        return 'success' + a, 200, {'Content-Type': 'applicaton/json'}
    else:
        json_response = {'server_status': 201, 'description': 'pls send post request', }
        return json.dumps(json_response, indent=2, ensure_ascii=False), 201, {'Content-Type': 'application/json'}


# Проверка подлинности токена
@app.route("/protected", methods=['GET', 'POST'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    username, message = request.json.get('name'), request.json.get('message')
    user_data = Customers.query.filter_by(name=username).first()
    if 'history' in message:
        count_loop = 1
        message_dict = {}

        # Если в сообщении есть history - то мы берём второй элемент как число сообщений для вывода
        count_messages = int(message.split(' ')[1])
        message_data = Messages.query.filter_by(customers_id=user_data.id).order_by(desc(Messages.id))

        # проверяем чтобы не выйти за длину полученных значений
        while count_loop <= count_messages and count_loop <= message_data.count():
            message_dict.update({message_data[count_loop-1].id:message_data[count_loop-1].message})
            count_loop += 1
        json_response = message_dict
        db.session.close()
        return json.dumps(json_response, indent=2, ensure_ascii=False), 200, {'Content-Type': 'application/json'}
    else:
        db.session.add(Messages(customers_id=user_data.id, message=message))
        db.session.commit()
        db.session.close()
    json_response = {'logged_in_as': current_user, 'add_message': message, }
    return json.dumps(json_response, indent=2, ensure_ascii=False), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run()