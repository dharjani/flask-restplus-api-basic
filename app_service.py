import json
import uuid
from uuid import UUID
from xmlrpc.client import DateTime
from datetime import datetime
import bcrypt

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
    
    def is_username_present(self, username):
        userData = json.loads(self.usersJSON)
        for user in userData:
            if user["emailaddress"] == username:
                return True;
        return False;

    def get_user(self, uname):
        userData = json.loads(self.usersJSON)
        for user in userData:
            if user["emailaddress"] == uname:
                return json.dumps(user, cls = UUIDEncoder);
        return json.dumps({'message': 'User Account not found'});

    def create_user(self, usermodel):
        userData = json.loads(self.usersJSON)
        un = str(usermodel['username'])
        fn = str(usermodel['first_name'])
        ln = str(usermodel['last_name'])
        p_w = usermodel['password']
        pw = p_w.encode("utf-8")
        salt = bcrypt.gensalt()
        hashedpw = bcrypt.hashpw(pw, salt)
        newuser = [{
            'id': uuid.uuid1(),
            'emailaddress' : un,
            'first_name': fn,
            'last_name': ln,
            "password": str(hashedpw),
            "psalt": str(salt),
            "account_created" : str(datetime.now()),
            "account_updated" : str(datetime.now())
        }]
        concatUsers = userData + newuser
        self.usersJSON = json.dumps(concatUsers, cls = UUIDEncoder)
        return json.dumps(newuser[0], cls = UUIDEncoder);

    def update_user(self, usermodel):
        userData = json.loads(self.usersJSON)
        un = str(usermodel['username'])#.strip()
        fn = str(usermodel['first_name'])
        ln = str(usermodel['last_name'])
        p_w = usermodel['password']
        for user in userData:
            if user["emailaddress"] == un:
                if bool(fn and fn.strip()):
                    user["first_name"] = fn
                    user["account_updated"] = str(datetime.now())
                if bool(ln and ln.strip()):
                    user["last_name"] = ln
                    user["account_updated"] = str(datetime.now())
                #if bool(p_w and p_w.strip()):
                if not p_w is None:
                    pw = p_w.encode("utf-8")
                    salt = bcrypt.gensalt()
                    hashedpw = bcrypt.hashpw(pw, salt)
                    user["password"] = str(hashedpw)
                    user["psalt"] = str(salt)
                    user["account_updated"] = str(datetime.now())
                self.usersJSON = json.dumps(userData, cls = UUIDEncoder)
                return json.dumps(user, cls = UUIDEncoder);
        return json.dumps({'message': 'User Account not found'});

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

    
