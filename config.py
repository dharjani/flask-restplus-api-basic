import os
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")
S3_SECRET = os.getenv("S3_SECRET_ACCESS_KEY")
S3_PREFIXURL = os.getenv("S3_PREFIXURL")
RDS_USERNAME = os.getenv("RDS_USERNAME")
RDS_PWD = os.getenv("RDS_PWD")
RDS_DB = os.getenv("RDS_DB")
RDS_HOST = os.getenv("RDS_HOST")
API_LOGGEDINUSERID = os.getenv("API_LOGGEDINUSERID")
AWS_KEY = os.getenv("AWS_KEY")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
GITHUB_REPO_PATH=os.getenv("GITHUB_REPO_PATH")