from flask import Flask, request, Blueprint
from flask_restplus import Resource, Api, fields
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
name_by_id_model = api.model('NameByIdModel', {'name_id' : fields.String})

@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {"message" : "Hello World"}

@api.route('/seed_names')
class SeedNames(Resource):
    def get(self):
        name = mongo.db.names
        name.insert_one({"name" : "Michael", "name_id": str(uuid.uuid1())})
        name.insert_one({"name" : "Sam", "name_id": str(uuid.uuid1())})
        name.insert_one({"name" : "David", "name_id": str(uuid.uuid1())})

        return {"message": "Data successfully Stored"}, 201

@api.route('/get_names')        
class GetNames(Resource):
    @api.marshal_with(names_model, envelope='dataset')
    def get(self):
        names = mongo.db.names
        output = []

        if names.estimated_document_count() != 0:
            for n in names.find({}):
                print (n['name_id'], n['name'])
                output.append({'name': n['name'], 'name_id' : n['name_id']})
            return output, 200

        return {'status': "No names available."}

@api.route('/find_names/<name_id>')
class FindNames(Resource):
    @api.expect(name_by_id_model)
    def get(self, name_id):
        names = mongo.db.names
        r = names.find_one({'name_id': name_id})
        if r:
            return {'name_id' : r['name_id'], 'name': r['name']} 
        
        return { "dataset": [ {name_id : "Not found"}]}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
