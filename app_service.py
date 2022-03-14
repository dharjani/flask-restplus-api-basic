import json
#from tkinter import E
import uuid
from uuid import UUID
from xmlrpc.client import DateTime, boolean
from datetime import datetime
import bcrypt
from sqlalchemy import false
import boto3
from config import S3_BUCKET, S3_KEY, S3_SECRET, RDS_DB, RDS_HOST, RDS_PWD, RDS_USERNAME#,S3_PREFIXURL
from flask import session
from io import StringIO
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key
from werkzeug.datastructures import FileStorage
import pymysql

rdsconn = pymysql.connect(host= RDS_HOST,port = 3306,user = RDS_USERNAME, password = RDS_PWD, db = RDS_DB)
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)

class AppService:

    authusers = [
        {
            'id': uuid.uuid1(),
            'emailaddress' : 'jane.doe@example.com',
            'first_name': "Jane",
            'last_name': "Doe",
            "password": "skdjfhskdfjh",
            "psalt": "skdjfhsfjh",
            "account_created": str(datetime.now()),
            "account_updated": str(datetime.now())
        },
        {
            'id': uuid.uuid1(),
            'emailaddress' : 'john.doe@example.com',
            'first_name': "John",
            'last_name': "Doe",
            "password": "skdjfhskdfjhlasdj",
            "psalt": "skdjfhskdfjh",
            "account_created": str(datetime.now()),
            "account_updated": str(datetime.now())
        },
        {
            'id': uuid.uuid1(),
            'emailaddress' : 'mary.doe@example.com',
            'first_name': "Mary",
            'last_name': "Doe",
            "password": "fhskdfjhkahsdh",
            "psalt": "skdjfhskdfjh",
            "account_created": str(datetime.now()),
            "account_updated": str(datetime.now())
        }
    ]
    
    students = [
        {
            'id': 1,
            'name': "std1",
            "description": "Record for student 1"
        },
        {
            "id": 2,
            "name": "std2",
            "description": "Record for student 2"
        },
        {
            "id": 3,
            "name": "std3",
            "description": "Record for student 3"
        }
    ]

    def __init__(self):
        self.studentsJSON = json.dumps(self.students)
        self.usersJSON = json.dumps(self.authusers, cls = UUIDEncoder)

    def isBlank (inputstr):
        return not (inputstr and inputstr.strip())

    def isNotBlank (inputstr):
        return bool(inputstr and inputstr.strip())

    def get_authenticatedusers(self):
        return self.usersJSON
    
    # def is_username_present(self, username):
    #     userData = json.loads(self.usersJSON)
    #     for user in userData:
    #         if user["emailaddress"] == username:
    #             return True;
    #     return False;

    def is_username_present(self, username):
        try:
            cur=rdsconn.cursor() 
            query_string = "SELECT * FROM csye6225.User WHERE emailaddress = %s"
            cur.execute(query_string, (username,))
            details = cur.fetchall()
            for user in details:
                    return True;
            return False;
        except Exception as e:
            print(e)

    def get_user(self, uname):
        try:
            cur=rdsconn.cursor() 
            query_string = "SELECT * FROM csye6225.User WHERE emailaddress = %s"
            cur.execute(query_string, (uname,))
            details = cur.fetchall()
            for user in details:
                userdata = {
                    'id': user[1],
                    'emailaddress' : user[2],
                    'first_name': user[3],
                    'last_name': user[4],
                    'password': str(user[5]),
                    'psalt': str(user[6]),
                    'account_created' : str(user[7]),
                    'account_updated' : str(user[8])
                }
                return json.dumps(userdata, cls = UUIDEncoder);
            return json.dumps({'message': 'User Account not found'});
        except Exception as e:
            print(e)

    def create_user(self, usermodel):
        try:
            userData = json.loads(self.usersJSON)
            un = str(usermodel['username'])
            fn = str(usermodel['first_name'])
            ln = str(usermodel['last_name'])
            p_w = usermodel['password']
            pw = p_w.encode("utf-8")
            salt = bcrypt.gensalt()
            hashedpw = bcrypt.hashpw(pw, salt)
            newuid = uuid.uuid1()
            dtnow = datetime.now()
            newuser = [{
                'id': newuid,
                'emailaddress' : un,
                'first_name': fn,
                'last_name': ln,
                "password": str(hashedpw),
                "psalt": str(salt),
                "account_created" : str(dtnow),
                "account_updated" : str(dtnow)
            }]
            cur=rdsconn.cursor()
            cur.execute("INSERT INTO csye6225.User (id,emailaddress,firstname,lastname,password,salt,createdate,updatedate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (str(newuid),un,fn,ln,str(hashedpw),str(salt),dtnow,dtnow))
            rdsconn.commit()
            concatUsers = userData + newuser
            self.usersJSON = json.dumps(concatUsers, cls = UUIDEncoder)
            return json.dumps(newuser[0], cls = UUIDEncoder);
        except Exception as e:
            print(e)

    def update_user(self, usermodel):
        try:
            #userData = json.loads(self.usersJSON)
            un = str(usermodel['username'])#.strip()
            fn = str(usermodel['first_name'])
            ln = str(usermodel['last_name'])
            p_w = usermodel['password']
            cur=rdsconn.cursor() 
            query_string = "SELECT * FROM csye6225.User WHERE emailaddress = %s"
            cur.execute(query_string, (un,))
            details = cur.fetchall()
            for user in details:
                currFN = user[3]
                currLN = user[4]
                currPW = str(user[5])
                currST = str(user[6])
                currUD = str(user[8])
                anyColUpdate = False
                if bool(fn and fn.strip()):
                    currFN = fn
                    currUD = str(datetime.now())
                    anyColUpdate = True
                if bool(ln and ln.strip()):
                    currLN = ln
                    currUD = str(datetime.now())
                    anyColUpdate = True
                #if bool(p_w and p_w.strip()):
                if not p_w is None:
                    pw = p_w.encode("utf-8")
                    salt = bcrypt.gensalt()
                    hashedpw = bcrypt.hashpw(pw, salt)
                    currPW = str(hashedpw)
                    currST = str(salt)
                    currUD = str(datetime.now())
                    anyColUpdate = True
                if anyColUpdate:
                    cur=rdsconn.cursor()
                    cur.execute("UPDATE csye6225.User SET firstname = %s, lastname = %s, password = %s, salt = %s, updatedate = %s WHERE emailaddress = %s", (currFN, currLN, currPW, currST, currUD, un))
                    rdsconn.commit()
                #self.usersJSON = json.dumps(userData, cls = UUIDEncoder)
                userdata = {
                    'id': user[1],
                    'emailaddress' : user[2],
                    'first_name': currFN,
                    'last_name': currLN,
                    'password': currPW,
                    'psalt': currST,
                    'account_created' : str(user[7]),
                    'account_updated' : currUD
                }
                return json.dumps(userdata, cls = UUIDEncoder);
                #return self.get_user(un) #json.dumps(user, cls = UUIDEncoder);
            return json.dumps({'message': 'User Account not found'});
        except Exception as e:
            print(e)

    def get_profile_pic(self, uname):
        try:
            cur=rdsconn.cursor() 
            query_string = "SELECT * FROM csye6225.User WHERE emailaddress = %s"
            cur.execute(query_string, (uname,))
            details = cur.fetchall()
            for user in details:
                file_name = user[9]
                if not file_name is None:
                    picdata = {
                        'file_name': str(file_name),
                        'id': str(user[10]),
                        'url': str(user[11]),
                        'upload_date' : str(user[12]),
                        'user_id': str(user[2])
                    }
                    return json.dumps(picdata, cls = UUIDEncoder);
                return json.dumps({'message': 'User Account does not have a Profile Picture uploaded'});
            return json.dumps({'message': 'User Account not found'});
                # key = "obj1.png" #request.form['key']
                # my_bucket = self.get_bucket()
                # file_obj = my_bucket.Object(key).get()
                # print(file_obj['ResponseMetadata']['HTTPHeaders'])
                # return {
                #     'status': 'success',
                #     'message': 'get file success',
                #     'key': key
				#     #'s3_key': file_obj
				#     #'s3_lastmodified': file_obj.last_modified
                # }
        except Exception as e:
            print(e)

    def get_user_id(self, un):
        try:
            cur=rdsconn.cursor() 
            query_string = "SELECT * FROM csye6225.User WHERE emailaddress = %s"
            cur.execute(query_string, (un,))
            details = cur.fetchall()
            for user in details:
                userid = user[1]
                return str(userid);
            return str(0);
        except Exception as e:
            print(e)


    def add_profile_pic(self, filename, un):
        try:
            cur=rdsconn.cursor() 
            query_string = "SELECT * FROM csye6225.User WHERE emailaddress = %s"
            cur.execute(query_string, (un,))
            details = cur.fetchall()
            for user in details:
                userid = user[1]
                newuid = uuid.uuid1()
                surl = S3_BUCKET + '/' + str(userid) + '/' + filename
                dtnow = datetime.now()
                cur=rdsconn.cursor()
                cur.execute("UPDATE csye6225.User SET filename = %s, fileid = %s, s3url = %s, uploaddate = %s WHERE emailaddress = %s", (filename, newuid, surl, dtnow, un))
                rdsconn.commit()
                picdata = {
                    'file_name': str(filename),
                    'id': str(newuid),
                    'url': str(surl),
                    'upload_date' : str(dtnow),
                    'user_id': str(userid)
                }
                return json.dumps(picdata, cls = UUIDEncoder);
            return json.dumps({'message': 'User Account not found'});
        except Exception as e:
            print(e)

    def get_profile_pic_key(self, un):
        try:
            cur=rdsconn.cursor() 
            query_string = "SELECT * FROM csye6225.User WHERE emailaddress = %s"
            cur.execute(query_string, (un,))
            details = cur.fetchall()
            for user in details:
                file_name = user[9]
                if not bool(file_name and file_name.strip()):
                #if not file_name is None:
                    return '-1'
                user_id = str(user[1])
                file_key = user_id + '/' + str(file_name)
                return file_key;
            return '';
        except Exception as e:
            print(e)

    def delete_profile_pic(self, un):
        try:
            cur=rdsconn.cursor()
            cur.execute("UPDATE csye6225.User SET filename = NULL, fileid = NULL, s3url = NULL, uploaddate = NULL WHERE emailaddress = %s", (un))
            rdsconn.commit()
        except Exception as e:
            print(e)

    def get_students(self):
        return self.studentsJSON
    
    def delete_student_list(self):
        studentData = json.loads(self.studentsJSON)
        studentData.clear()
        self.studentsJSON = studentData
        return json.dumps({'message': 'Student List Deleted'});

    def get_student(self, req_student_id):
        studentData = json.loads(self.studentsJSON)
        for student in studentData:
            if student["id"] == req_student_id:
                return student;
        return json.dumps({'message': 'Student ID not found'});

    def create_student(self,student):
        studentData = json.loads(self.studentsJSON)
        studentData.append(student)
        self.studentsJSON = json.dumps(studentData)
        return self.studentsJSON

    def update_student(self, req_student):
        studentData = json.loads(self.studentsJSON)
        for student in studentData:
            if student["id"] == req_student['id']:
                student.update(req_student)
                return json.dumps(studentData);
        return json.dumps({'message': 'Student ID not found'});

    def delete_student(self, req_student_id):
        studentData = json.loads(self.studentsJSON)
        for student in studentData:
            if student["id"] == req_student_id:
                studentData.remove(student)
                return json.dumps(studentData);
        return json.dumps({'message': 'Student ID not found'});

    def _get_s3_resource(self):
        if S3_KEY and S3_SECRET:
            return boto3.resource(
                's3',
                aws_access_key_id=S3_KEY,
                aws_secret_access_key=S3_SECRET
            )
        else:
            return boto3.resource('s3')

    def get_bucket(self):
        s3_resource = self._get_s3_resource()
        if 'bucket' in session:
            bucket = session['bucket']
        else:
            bucket = S3_BUCKET

        return s3_resource.Bucket(bucket)

    def get_buckets_list():
        client = boto3.client('s3')
        return client.list_buckets().get('Buckets')

    
