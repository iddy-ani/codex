import pymongo
from datetime import datetime
import getpass
from datetime import timedelta
import requests

def get_user_email(user_idsid):
    url = f'https://ldapagator.apps1-ir-int.icloud.intel.com/user?username={user_idsid}'
    response = requests.get(url, verify=False)

    if response.status_code != 200:
        return None
    
    return response.json().get('email', None)

user = getpass.getuser()
user_email = get_user_email(user)

client = 'mongodb://ExpertGPTDB_rw:12zWgSh5cBl19E9@p1ir1mon019.ger.corp.intel.com:7181,p2ir1mon019.ger.corp.intel.com:7181,p3ir1mon019.ger.corp.intel.com:7181/ExpertGPTDB?ssl=true&replicaSet=mongo7181'
connection = 'ExpertGPTDB'

ConnectionString = pymongo.MongoClient(client)
DatabaseFiles = ConnectionString[connection]

def user_tracking(user_email, method = 'codex'):
    # Update or insert document with the users email and the current timestamp
    DatabaseFiles['tracking'].insert_one(
        {'email': user_email, 'timestamp': datetime.now(), 'method': method}
    )

if not DatabaseFiles['tracking'].find_one({'email': user_email, 'timestamp': {'$gte': datetime.now() - timedelta(hours=1)}}):
        user_tracking(user_email)