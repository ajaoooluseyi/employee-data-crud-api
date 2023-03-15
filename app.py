from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema #imports modules to serialize Python objects
from datetime import datetime


app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False
db = SQLAlchemy(app)


#creating tables in database
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(200), nullable=False )
    lastname = db.Column(db.String(200), nullable=False )
    gender = db.Column(db.String(200), nullable=False )
    salary = db.Column(db.Float)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
            return f"{self.lastname} , {self.firstname} | {self.gender} | {self.salary}"

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique = True )
    email = db.Column(db.String(200), nullable=False, unique = True )
    password_hash = db.Column(db.String(1000))

@auth.verify_password
def verify_password(username, password):
    admin = Admin.query.filter_by(username = username).first()
    if not (username and password):
        return False
    return True


class EmployeeSchema(SQLAlchemyAutoSchema):
    class Meta(SQLAlchemyAutoSchema.Meta):
        model = Employee
        load_instance = True



class GetData(Resource):
    @auth.login_required
    def get(self):
        emp = Employee.query.all() # queries the database for employees
        schema = EmployeeSchema(many=True)
        data = schema.dump(emp)

        return make_response(jsonify({'Employees':data})) #returns list of employees as JSON

class GetDataById(Resource):
    def get(self, id):
        emp = Employee.query.get(id)  # queries the database for employees
        schema = EmployeeSchema()
        data = schema.dump(emp)

        return make_response(jsonify({'Employee':data})) #returns list of employesss as JSON


class PostData(Resource):
    def post(self):
        if request.is_json:
            data = request.get_json()  # gets data from request body
            firstname = data['firstname']
            lastname = data['lastname']
            gender = data['gender']
            salary = data['salary']

            new = Employee(lastname = lastname, firstname = firstname, gender = gender, salary = salary)

            db.session.add(new) # adds task to database
            db.session.commit() # commits changes to database

            schema = EmployeeSchema()
            data = schema.dump(new)

            return make_response(jsonify({'New Employee': data}), 201)
        else:
            return{'error': "Request not JSON"}, 400

class UpdateData(Resource):
    def put(self, id):
        if request.is_json:
            data = request.get_json() # gets data from request body
            emp = Employee.query.get(id) # queries the database by given id
            if emp is None:
                return {'error':'Not found'}, 404
            else:
                emp.firstname = data["firstname"]
                emp.lastname = data["lastname"]
                emp.gender = data["gender"]
                emp.salary = data["salary"] #updates employee data with new data

                db.session.commit() # commits changes to database
                return 'Updated', 200
        else:
            return {'error': 'Request is not JSON'  } ,400

class DeleteData(Resource):
    def delete(self, id):
        emp = Employee.query.get(id) # queries the database by given id
        if emp is None:
            return {'error':'Not found'}, 404
        else:
            db.session.delete(emp)
            db.session.commit() # commits changes to database
            return 'Employee is deleted', 200


api.add_resource(GetData, '/')
api.add_resource(GetDataById, '/<int:id>')
api.add_resource(PostData, '/add/')
api.add_resource(UpdateData, '/update/<int:id>/')
api.add_resource(DeleteData, '/delete/<int:id>/')


if __name__ == '__main__':
    app.run(debug=True)
