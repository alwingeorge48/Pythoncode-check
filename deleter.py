import pandas as pd
import json, pathlib, os
from sqlalchemy import create_engine
from configparser import ConfigParser
from pathlib import Path
import sys
import requests
import mysql.connector

# get config file
configs = ConfigParser()
path = pathlib.Path(os.path.realpath(__file__))
configs.read(path.parent/'config.ini')

# get database configurations
# hostname = os.environ.get('canoe_db_hostname')
# username = os.environ.get('canoe_db_username')
# password = os.environ.get('canoe_db_password')
# db_name = os.environ.get('canoe_db_name')
hostname = 'mysql-sga-rpa-ec2-test.cf3hejlfgvsh.ap-south-1.rds.amazonaws.com'
username = 'test_master_user'
password = 'Rpasga123456'
db_name = 'rpa_mysql_ec2_Test'
dialect = configs.get('DATABASE', 'dialect')
driver = configs.get('DATABASE', 'driver')

engine = create_engine(f"{dialect}+{driver}://{username}:{password}@{hostname}/{db_name}")
extract_df = pd.read_sql(f"SELECT canoe_doc_id FROM booksdata WHERE canoe_doc_id IS NOT NULL AND MONTH(publication_date) = {sys.argv[1]} AND YEAR(publication_date) = {sys.argv[2]}", con=engine)
# import pdb; pdb.set_trace()

# get access-token
url = "https://api.canoesoftware.com/v1/tokens"
headers = {
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
}
body = {
    "username": os.environ.get('canoe_portal_username'),
    "password": os.environ.get('canoe_portal_password'),
}
response = requests.post(url, json.dumps(body), headers=headers,  )
parsed = json.loads(response.text)

# delete request headers
headers = {
    "Authorization": f"Bearer {parsed['access_token']}",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

for id in extract_df['canoe_doc_id'].to_list():
    url = f"https://api.canoesoftware.com/v1/documents/{id}"
    response = requests.delete(url,  headers=headers,  )
    parsed = json.loads(response.text)
    parsed['canoe_doc_id'] = id
    print(json.dumps(parsed, indent=4))

try: 

    with mysql.connector.connect( host=hostname, user=username, password=password, database=db_name) as mydb:

    # deleting table entries
        with mydb.cursor() as cursor:
            sql = f"DELETE FROM booksdata WHERE canoe_doc_id IS NOT NULL AND MONTH(publication_date) = {sys.argv[1]} AND YEAR(publication_date) = {sys.argv[2]}"
            cursor.execute(sql)
            print(cursor.rowcount, "entries deleted.")
            mydb.commit()

except Exception as e:
    print(e)