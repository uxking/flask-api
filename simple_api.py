from flask import Flask, request
from flask_restplus import Resource, Api, fields
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'flask-demo'
app.config['MONGO_URI'] = 'mongodb://172.17.0.3:27017/flask-demo'
api = Api(app)
mongo = PyMongo(app)

names_model = api.model('NamesModel', {'name' : fields.String})


@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {"message" : "Hello World"}

@api.route('/seed_names')
class SeedNames(Resource):
    def get(self):
        name = mongo.db.names
        name.insert_one({"name" : "Michael"})
        name.insert_one({"name" : "David"})
        name.insert_one({"name" : "Joseph"})
        name.insert_one({"name" : "Arnold"})
        return {"message": "Data successfully Stored"}

@api.route('/get_names')        
class GetNames(Resource):
    @api.response(200, 'Success', names_model)
    def get(self):
        names = mongo.db.names
        output = []

        if names.count() != 0:
            for n in names.find({}):
                print (n)
                output.append({'name': n['name']})
            return output

        return {'status': "No names available."}
        


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
