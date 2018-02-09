import httplib2
import os
import base64
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import select
import socket
import re

import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
import logging
                
UNREAD_QUOTES = 'Label_8'
READ_QUOTES = 'Label_9'

CREDENTIALS_DIR = '.credentials'
CREDENTIALS_FNAME = 'credentials.json'

GET_QUOTE = 'q'
GET_PHONE_NUMBER = 'u'
GET_NUM_USERS = 'nu'
GET_NUM_QUOTES = 'nq'

SUCCESS = 's'
INVALID_FORMAT = 'i'

ADDR = 'localhost'
PORT = 50000

QUOTES_DIR = 'quotes'
PHONE_NUMBER_FNAME = 'phone number'

def pull_quotes():
    mids_request = gmail.users().messages().list(
        userId='me',
        labelIds=[UNREAD_QUOTES]
    ).execute()
    if u'messages' not in mids_request:
        return
    unread_mids = [
        d[u'id']
        for d in
        mids_request[u'messages']
    ]
    for mid in unread_mids:
        message = gmail.users().messages().get(
            userId='me',id=mid
        ).execute()
        data = message[
            u'payload'
        ][
            u'parts'
        ][0][
            u'body'
        ][
            u'data'
        ]
        lines = base64.urlsafe_b64decode(
            str(data)
        ).strip().split('\r')
        quote = ''
        for line in lines[1:]:
            if (
                    '<https://voice.google.com>' in line
            ) or (
                'Google Voice' in line
            ): break
            quote += line
            quote = quote.strip()
        for header_dict in message[u'payload'][u'headers']:
            if header_dict[u'name']==u'From':
                phone_number = re.compile(
                    r'<\d+\.(\d+)\.\w+@txt\.voice\.google\.com>'
                ).search(
                    header_dict[u'value']
                ).group(1)
                break
        logging.info('message pulled: %s', phone_number)
        logging.info(quote)
        gmail.users().messages().modify(
            userId='me',
            id=mid,
            body={
                'removeLabelIds':[UNREAD_QUOTES],
                'addLabelIds':[READ_QUOTES]
            }
        ).execute()
        while True:
            success, user_id = get_user_id(phone_number)
            if success: break
            else: add_user(phone_number)
        add_quote(user_id,quote)

def get_gmail():
    home_dir = os.path.expanduser('~')
    credentials_dir = os.path.join(home_dir,CREDENTIALS_DIR)
    credentials_path = os.path.join(credentials_dir,CREDENTIALS_FNAME)
    store = Storage(credentials_path)
    credentials = store.get()
    http = credentials.authorize(httplib2.Http())
    gmail = discovery.build('gmail', 'v1', http=http)
    return gmail

def get_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind((ADDR,PORT))
    server.listen(5)
    return server

def add_quote(user_id,quote):
    with open(
            os.path.join(
                QUOTES_DIR,
                user_id,
                str(get_num_quotes(user_id)[1])
            ),
            'w'
    ) as f:
        f.write(quote)

def get_user_id(phone_number):
    success = True
    user_id = None
    phone_numbers = [
        get_phone_number(str(user_id))[1]
        for user_id in range(get_num_users())
    ]
    if phone_number in phone_numbers:
        user_id = str(phone_numbers.index(phone_number))
    else:
        success = False
    return success, user_id

def add_user(phone_number):
    user_dir = os.path.join(QUOTES_DIR,str(get_num_users()))
    os.mkdir(user_dir)
    with open(os.path.join(user_dir,PHONE_NUMBER_FNAME),'w') as f:
        f.write(phone_number)
    
def get_conns():
    readable,_,_ = select.select([server],[],[],0.0)
    if readable:
        conn,_ = server.accept()
        conns.append(conn)

def get_quote(user_id,quote_id):
    quote = None
    success = True
    try:
        quote = open(os.path.join(QUOTES_DIR,user_id,quote_id),'r').read()
    except IOError:
        success = False
    return success, quote

def get_num_users():
    return len(os.listdir(QUOTES_DIR))
    
def get_phone_number(user_id):
    phone_number = None
    success = True
    try:
        phone_number = open(os.path.join(QUOTES_DIR,user_id,PHONE_NUMBER_FNAME),'r').read()
    except IOError:
        success = False
    return success, phone_number

def get_num_quotes(user_id):
    success = True
    num_quotes = None
    try:
        num_quotes = len(os.listdir(os.path.join(QUOTES_DIR,user_id)))
        num_quotes -= 1
    except OSError:
        success = False
    return success, num_quotes

def close_conn(conn):
    conns.remove(conn)
    conn.close()

conns = []
server = get_server()
gmail = get_gmail()
while True:
    get_conns()
    readable,_,_ = select.select(conns,[],[],0.0)
    for conn in readable:
        message = conn.recv(1024).strip()
        logging.info('message:', message)
        if not message:
            close_conn(conn)
            continue
        message_components = message.split(' ')
        command = message_components[0]
        if command == GET_QUOTE:
            try:
                user_id = message_components[1]
                quote_id = message_components[2]
            except IndexError:
                conn.send(INVALID_FORMAT)
                close_conn(conn)
                continue            
            success, quote = get_quote(user_id,quote_id)
            if success:
                conn.send(' '.join((SUCCESS,quote)))
            else:
                conn.send(INVALID_FORMAT)
        elif command == GET_PHONE_NUMBER:
            try:
                user_id = message_components[1]
            except IndexError:
                conn.send(INVALID_FORMAT)
                close_conn(conn)
                continue
            success, phone_number = get_phone_number(user_id)
            if success:
                conn.send(' '.join((SUCCESS, phone_number)))
            else:
                conn.send(INVALID_FORMAT)
        elif command == GET_NUM_USERS:
            conn.send(' '.join((SUCCESS,str(get_num_users()))))
        elif command == GET_NUM_QUOTES:
            try:
                user_id = message_components[1]
            except IndexError:
                conn.send(INVALID_FORMAT)
                close_conn(conn)
                continue
            success, num_quotes = get_num_quotes(user_id)
            if success:
                conn.send(' '.join((SUCCESS, str(num_quotes))))
            else:
                conn.send(INVALID_FORMAT)
        else:
            conn.send(INVALID_FORMAT)
        close_conn(conn)
    pull_quotes()
