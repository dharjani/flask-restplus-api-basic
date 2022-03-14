from email import message
from http.client import BAD_REQUEST
import imp
import uuid
from flask import Flask, render_template, request
from flask_restplus import Api, Resource, fields
from app_service import AppService
import json
import random, string
import bcrypt
from io import StringIO
#from boto.s3.connection import S3Connection
#from boto.s3.key import Key as S3Key
from config import S3_BUCKET, S3_KEY, S3_SECRET, API_LOGGEDINUSERID
import boto3
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

class Error(Exception):
    pass

class BadRequestException(Error):
	pass

class BadRequestNoUserException(Error):
	pass

class BadRequestNoPictureException(Error):
	pass

class BadRequestAdditionalUpdatesException(Error):
	pass

flask_app = Flask(__name__)
#flask_app.config['DEBUG'] = True
#flask_app.wsgi_app = ProxyFix(app.wsgi_app)
app = Api(app = flask_app, 
		  version = "1.0", 
		  title = "Simple RESTful Service", 
		  description = "Simple RESTful Service")

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=4999)

appService = AppService();

name_space_triage = app.namespace('triage', description='Operations to triage CRUD operations. Unavailable to all users.')
name_space_admin = app.namespace('admin', description='Operations available only to admin users')
name_space_authusers = app.namespace('authenticated', description='Operations available only to authenticated users')
name_space_authusers_fileupload = app.namespace('fileoperations', description='Upload operations available only to authenticated users')
name_space_public = app.namespace('public', description='Operations available to all users without authentication')


usermodel = app.model('User',
					{'id' : fields.String(description = "User ID", readonly = True, type = uuid, example= "d290f1ee-6c54-4b01-90e6-d701748f0851"),
					'first_name' : fields.Integer(required = True, description = "First Name", help = "First Name cannot be blank", example= "Jane") , 
                    'last_name': fields.String(required = True, description="Last Name", help = "First Name cannot be blank", example= "Doe") ,
                    'username': fields.String(required = True, description="User Name", help="User Name cannot be blank", example= "jane.doe@example.com"),
					'password': fields.String(required = True, description="Password", mask = True, example = "skdjfhskdfjhg"),
					'account_created': fields.DateTime(description="Account Created On", mask = True, readonly = True, example = "2016-08-29T09:12:33.001Z"),
					'account_updated': fields.DateTime(description="Account Updated On", mask = True, readonly = True, example = "2016-08-29T09:12:33.001Z") })

imagemodel = app.model('Image',
					{'file_name' : fields.String(required = True, readonly = True, description = "File Name", help = "File Name cannot be blank", example= "image.jpg"),
					'id' : fields.String(required = True, description = "ID", readonly = True, type = uuid, example= "d290f1ee-6c54-4b01-90e6-d701748f0851"),
                    'url': fields.String(required = True, description="URL", help = "URL cannot be blank", example= "bucket-name/user-id/image-file.extension") ,
					'user_id' : fields.String(required = True, description = "User ID", readonly = True, type = uuid, example= "d290f1ee-6c54-4b01-90e6-d701748f0851"),
					'upload_date': fields.DateTime(required = True, description="Upload Date", mask = True, readonly = True, example = "2016-08-29T09:12:33.001Z") })

s3 = boto3.client('s3',
                    aws_access_key_id=S3_KEY,
                    aws_secret_access_key= S3_SECRET)

upload_parser = app.parser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def random_name():
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

@name_space_public.route("/v1/user")
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

@name_space_authusers.route("/v1/user/self")
class AuthUsersOperationsClass(Resource):

	@app.doc(responses={ 200: 'OK', 400: 'Bad Request Exception', 500: 'Internal Server Error' })
	@app.expect(usermodel)
	def put(self):
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
			resp = json.loads(appService.get_user(API_LOGGEDINUSERID))
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

# @name_space_triage.route("/allunmaskedusers")
# class TriageOperationsClass(Resource):
	
# 	@app.doc(responses={ 200: 'OK', 500: 'Internal Server Error' })
# 	def get(self):
# 		try:
# 			resp = json.loads(appService.get_authenticatedusers())
# 			return resp;
# 		except KeyError as e:
# 			name_space_triage.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
# 		except Exception as e:
# 			name_space_triage.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")

@name_space_authusers.route("/v1/user/self/pic")
class FileOperations(Resource):
	@app.doc(responses={ 200: 'OK', 404: 'Object not found', 500: 'Internal Server Error' })
	#@app.expect(imagemodel)
	def get(self):
		try:
			return json.loads(appService.get_profile_pic(API_LOGGEDINUSERID))
		except Exception as e: 
			print(e)
			name_space_authusers.abort(500, e.__doc__, status = "Could not get file information", statusCode = "500")

	def delete(self):
		try:
			key = appService.get_profile_pic_key(API_LOGGEDINUSERID)
			if key == '':
				raise BadRequestNoUserException
			if key == '-1':
				raise BadRequestNoPictureException
			my_bucket = appService.get_bucket()
			my_bucket.Object(key).delete()
			appService.delete_profile_pic(API_LOGGEDINUSERID)
			return {
                 'status': 'success',
                 'message': 'delete file success',
                 'key': key
             }
		except BadRequestNoUserException as e:
			name_space_authusers.abort(400, e.__doc__, status = "User Name Not Found. Delete operation failed.")
		except BadRequestNoPictureException as e:
			name_space_authusers.abort(400, e.__doc__, status = "Profile Picture Not Found. Delete operation failed.")
		except Exception as e:
			name_space_authusers.abort(400, e.__doc__, status = "Delete operation failed.")
		
	@name_space_authusers_fileupload.expect(upload_parser)
	@app.doc(responses={ 200: 'OK', 400: 'Bad Request', 500: 'Internal Server Error' })
	def post(self):
		try:
			if 'file' not in request.files:
				return {
					'status': 'fail',
					'message': 'no set file'
				}
				
			file = request.files["file"]
			if file.filename == '':
				return {
					'status': 'fail',
					'message': 'no set filename'
				}

			if not allowed_file(file.filename):
				allowed_file_ext = ','.join(ALLOWED_EXTENSIONS)
				return {
					'status': 'fail',
					'message': 'only support file extension:' + allowed_file_ext,
					'data': allowed_file_ext
				}
			
			if file and allowed_file(file.filename):
				mime = file.filename.rsplit(".")[1]
				file_key = random_name() + "." + mime
				user_id = appService.get_user_id(API_LOGGEDINUSERID)
				if user_id == '0':
					raise BadRequestNoUserException
				my_bucket = appService.get_bucket()
				curr_file_key = appService.get_profile_pic_key(API_LOGGEDINUSERID)
				if curr_file_key != '' and curr_file_key != '-1':
					my_bucket.Object(curr_file_key).delete()
				updatedfilename = random_name()+'_'+file.filename
				file_key = user_id + "/" + updatedfilename
				my_bucket.Object(file_key).put(Body=file)
				return json.loads(appService.add_profile_pic(updatedfilename, API_LOGGEDINUSERID))
		except BadRequestNoUserException as e:
			name_space_authusers.abort(400, e.__doc__, status = "User Name Not Found. Could not save information.")
		except Exception as e:
			print(e)
			name_space_authusers.abort(500, e.__doc__, status = "Could not upload file", statusCode = "500")