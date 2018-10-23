from flask import Flask, request, Blueprint
from flask_restplus import Resource, Api, fields, marshal
from flask_pymongo import PyMongo
import uuid

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'flask-demo'
app.config['MONGO_URI'] = 'mongodb://172.17.0.3:27017/flask-demo'

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, doc='/documentation')
app.register_blueprint(blueprint)

mongo = PyMongo(app)

names_model = api.model('NamesModel', {'name' : fields.String, 'name_id': fields.String})
new_name_model = api.model('NewNameModel', {'name': fields.String})
error_model = api.model('ErrorModel', {'error': fields.String})
success_model = api.model('SuccessModel', {'success': fields.String})


@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {"message" : "Hello World"}

@api.route('/seed_data')
class SeedNames(Resource):
    def get(self):
        name = mongo.db.names
        name.insert_one({"name" : "Michael", "name_id": str(uuid.uuid1())})
        name.insert_one({"name" : "Sam", "name_id": str(uuid.uuid1())})
        name.insert_one({"name" : "David", "name_id": str(uuid.uuid1())})
        msg = {"success": "Data stored."}
        return marshal(msg, success_model, envelope='dataset')

@api.route('/add_name')
class AddName(Resource):
    @api.expect(new_name_model, validate=True)
    def post(self):
        if request.json and 'name' in request.json:
            cursor = mongo.db.names
            if cursor.find_one({'name': request.json['name']}):
                error_msg = {'error': 'Name already exists.'}
                return marshal(error_msg, error_model, envelope='dataset')
            
            new_name = {
                'name' : request.json['name'], 
                'name_id' : str(uuid.uuid1())
            }
            
            cursor.insert_one(new_name)
            return marshal(new_name, names_model, envelope='dataset')
            
        error_msg = {'error': 'name is required.'}
        return marshal(error_msg, error_model, envelope='dataset')

@api.route('/get_names')        
class GetNames(Resource):
    def get(self):
        names = mongo.db.names
        output = []

        if names.estimated_document_count() != 0:
            for n in names.find({}):
                print (n['name_id'], n['name'])
                output.append({'name': n['name'], 'name_id' : n['name_id']})
            return marshal(output, names_model, envelope='dataset')

        error_msg = {'error': 'No entries found.'}
        return marshal(error_msg, error_model, envelope='dataset')
        

@api.route('/find_by_id/<name_id>')
class FindNames(Resource):
    def get(self, name_id):
        names = mongo.db.names
        r = names.find_one({'name_id': name_id})
        if r:
            return marshal(r, names_model, envelope='dataset')
        
        error_msg = {'error': f'name_id {name_id} not found'}
        return marshal(error_msg, error_model, envelope='dataset')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
