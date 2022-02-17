from email import message
from http.client import BAD_REQUEST
import uuid
#from django.apps import apps
from flask import Flask, request
from flask_restplus import Api, Resource, fields
from app_service import AppService
import json
import bcrypt

class Error(Exception):
    pass

class BadRequestException(Error):
	pass

class BadRequestNoUserException(Error):
	pass

class BadRequestAdditionalUpdatesException(Error):
	pass

flask_app = Flask(__name__)
#flask_app.config['DEBUG'] = True
app = Api(app = flask_app, 
		  version = "1.0", 
		  title = "Simple RESTful Service", 
		  description = "Simple RESTful Service")

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0")

appService = AppService();

name_space_triage = app.namespace('triage', description='Operations to triage CRUD operations. Unavailable to all users.')
name_space_admin = app.namespace('admin', description='Operations available only to admin users')
name_space_authusers = app.namespace('authenticated', description='Operations available only to authenticated users')
name_space_public = app.namespace('public', description='Operations available to all users without authentication')


usermodel = app.model('User',
					{'id' : fields.String(description = "User ID", readonly = True, type = uuid, example= "d290f1ee-6c54-4b01-90e6-d701748f0851"),
					'first_name' : fields.Integer(required = True, description = "First Name", help = "First Name cannot be blank", example= "Jane") , 
                    'last_name': fields.String(required = True, description="Last Name", help = "First Name cannot be blank", example= "Doe") ,
                    'username': fields.String(required = True, description="User Name", help="User Name cannot be blank", example= "jane.doe@example.com"),
					'password': fields.String(required = True, description="Password", mask = True, example = "skdjfhskdfjhg"),
					'account_created': fields.DateTime(description="Account Created On", mask = True, readonly = True, example = "2016-08-29T09:12:33.001Z"),
					'account_updated': fields.DateTime(description="Account Updated On", mask = True, readonly = True, example = "2016-08-29T09:12:33.001Z") })

@name_space_public.route("/")
class PublicUsersOperationsClass(Resource):
	@app.doc(responses={ 200: 'OK', 400: 'Bad Request Exception', 500: 'Internal Server Error' })
	@app.expect(usermodel)
	def post(self):
		try:    
			json_data = request.get_json(force=True)
			un = json_data['username']
			if appService.is_username_present(un):
				raise BadRequestException
			#return json.loads(appService.create_user(json_data));
			resp = json.loads(appService.create_user(json_data))
			del resp['password']
			del resp['psalt']
			return resp;
		except BadRequestException as e:
			name_space_public.abort(400, e.__doc__, status = "Could not save information. Username already taken.", statusCode = "400")
		except KeyError as e:
			name_space_public.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
		except Exception as e:
			name_space_public.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")

@name_space_public.route("/healthz")
class PublicUsersOperationsClass(Resource):
	@app.doc(responses={ 200: 'OK', 500: 'Internal Server Error' })
	def get(self):
		try:
			return {
				"status": "Cheers! Application is healthy."
			}
		except KeyError as e:
			name_space_public.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
		except Exception as e:
			name_space_public.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")

@name_space_authusers.route("/")
class AuthUsersOperationsClass(Resource):

	@app.doc(responses={ 200: 'OK', 400: 'Bad Request Exception', 500: 'Internal Server Error' })
	@app.expect(usermodel)
	def post(self):
		try:
			json_data = request.get_json(force=True)
			if appService.is_username_present(str(json_data['username'])) == False:
				raise BadRequestNoUserException
			#return json_data;
			#for k, v in json_data.iteritems():
			#	if k != "first_name" or k != "last_name" or k != "username" or k != "password":
			#		raise BadRequestAdditionalUpdatesException
			resp = json.loads(appService.update_user(json_data))
			del resp['password']
			del resp['psalt']
			return resp;
		except BadRequestNoUserException as e:
			name_space_authusers.abort(400, e.__doc__, status = "User Name Not Found. Could not save information.")
		except BadRequestAdditionalUpdatesException as e:
			name_space_authusers.abort(400, e.__doc__, status = "Update Failed. Only First Name, Last Name and Password can be updated.")
		except KeyError as e:
			name_space_authusers.abort(400, e.__doc__, status = "Could not save information. Incomplete Request", statusCode = "400")
		except Exception as e:
			name_space_authusers.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")

	@app.doc(responses={ 200: 'OK', 500: 'Internal Server Error' })
	def get(self):
		try:
			resp = json.loads(appService.get_user("jane.doe@example.com"))
			del resp['password']
			del resp['psalt']
			return resp;
		except KeyError as e:
			name_space_authusers.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
		except Exception as e:
			name_space_authusers.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
	
#@name_space_admin.route("/allusers")
#class AdminOperationsClass(Resource):
#	
#	@app.doc(responses={ 200: 'OK', 500: 'Internal Server Error' })
#	def get(self):
#		try:
#			resp = json.loads(appService.get_authenticatedusers())
#			for item in resp:
#				del item['password']
#				del resp['psalt']
#			return resp;
#		except KeyError as e:
#			name_space_admin.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
#		except Exception as e:
#			name_space_admin.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")

@name_space_triage.route("/allunmaskedusers")
class TriageOperationsClass(Resource):
	
	@app.doc(responses={ 200: 'OK', 500: 'Internal Server Error' })
	def get(self):
		try:
			resp = json.loads(appService.get_authenticatedusers())
			return resp;
		except KeyError as e:
			name_space_triage.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
		except Exception as e:
			name_space_triage.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")