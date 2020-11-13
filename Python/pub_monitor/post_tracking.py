import pandas as pd
import yagmail
from configparser import ConfigParser
import pathlib, os
from datetime import datetime
import pymysql

configs = ConfigParser()
path = pathlib.Path(os.path.realpath(__file__))
configs.read(path.parent/'config.ini')

# database credentials
hostname = os.environ.get('db_hostname')
username = os.environ.get('db_username')
password = os.environ.get('db_password')
db_name = configs.get('DATABASE', 'db_name')

# mail credentials
FROM = configs.get('MAIL', 'FROM')
TO = configs.get('MAIL', 'TO').split(', ')
PASS = os.environ.get('mail_pass')
SUBJECT = configs.get('MAIL', 'SUBJECT')
TEXT = configs.get('MAIL', 'TEXT')
CONTENTS = [f"{configs.get('APP', 'output_dir')}/exchanges_data.xlsx"]

def highlight_yellow(x):
    if x['company_id'] in list(universe_df['DMX']):
        return ['background-color: yellow']*x.size
    else:
        return ['']*x.size

excel_sequence = ['mkey', 'company_id', 'company_name', 'domicile', 't_publication_date', 'trgr', 'publication_date', 'update_date', 'doc_name', 'doc_link', 'ukey', 'doc_tag', 'doc_lang', 'monitor']
db_sequence = ['company_id', 'company_name', 'doc_link', 'doc_name', 'domicile', 'mkey', 'publication_date', 't_publication_date', 'trgr', 'ukey', 'update_date', 'year']

extract_df = pd.read_csv(f"{configs.get('APP', 'output_dir')}/booksdata.csv")
extract_df.fillna(0, inplace=True)

mydb = pymysql.connect( host=hostname, user=username, password=password, database=db_name)
cursor = mydb.cursor()
try:
    sql = "INSERT IGNORE INTO exchanges_data (company_id, company_name, doc_link, doc_name, domicile, mkey, publication_date, t_publication_date,trgr, ukey, update_date, year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = list(extract_df[db_sequence].itertuples(index=False, name=None))
    cursor.executemany(sql, val)
    total_new_publication = cursor.rowcount
    mydb.commit()
except Exception as e:
    print(e)
finally:
    mydb.close()

mydb = pymysql.connect( host=hostname, user=username, password=password, database=db_name)
cursor = mydb.cursor()
with open('etl.sql') as f:
    try:
        for i in f.read().split(';')[:-1]:
            cursor.execute(i)
        # cursor.execute("select * from t1")
        column_names = [i[0] for i in cursor.description]
        delta_excel = pd.DataFrame(cursor.fetchall(), columns=column_names)
        cursor.execute('UPDATE exchanges_data SET is_processed = true WHERE is_processed = false;')
        mydb.commit()
    except Exception as e:
        print(e)
    finally:
        mydb.close()

universe_df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/Universe-SGA.xlsx")

yag = yagmail.SMTP(FROM, PASS, host='smtp.office365.com', port=587, smtp_starttls=True, smtp_ssl=False)

if not delta_excel.empty:
    delta_excel = delta_excel[excel_sequence]
    delta_excel = delta_excel.style.apply(highlight_yellow, axis=1)
    delta_excel.to_excel(f"{configs.get('APP', 'output_dir')}/exchanges_data.xlsx", index=False)
    yag.send(TO, SUBJECT, f"Number of new publication: {total_new_publication}\n\n"+TEXT, CONTENTS)
else:
    yag.send(TO, SUBJECT, "<h2>No Publication Found..!!</h2>\n"+TEXT)
