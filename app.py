from flask import Flask, request
import os
import csv
import psycopg2
from dotenv import load_dotenv
from dotenv import find_dotenv
import hashlib, time
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

key_path = '"C:\Users\jacob\recyclequest-abd56bc8581a.json"'
sheet_id = '1H1-5p2iVq1dg0X31dbopoEbIa_gALT8je-Rom1XfIYM'
creds = None
if os.path.exist(key_path):
    creds = service_account.Credentials.from_service_account_file(key_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])

service = build('sheets', 'v4', credentials = creds)

app = Flask(__name__) #starts flask app

if __name__ == '__main__':
    app.run(debug=False)


# creates user table and leaderboard table if none exists, adds new user with username and theoretically unique hashed userID and password, initializes points to zero for given user
@app.post("/api/users")
def create_user():
    data = request.get_json()
    userName = data["userName"]
    userID = hash(time.time())
    unhashedPass = data["password"]
    salt = str(os.urandom(random.randint(0, 5)))
    unhashedPass = (unhashedPass+salt)
    unhashedPass = unhashedPass.encode('ascii', 'utf-8')
    hashedPass = hashlib.sha256(bytes(unhashedPass)).hexdigest()

# adds new points for a given user based on recycled items from client, the execute may or may not work
@app.post("/api/leaderboard")
def update_leaderboard():
    data = request.get_json()
    userName = data["userName"]
    itemsRecycled = data["recycledItems"]
    itemsDisposed = data["disposedItems"]
    newPoints = recycleConstant * itemsRecycled + disposalConstant * itemsDisposed


# tests password attempt against hashed password and stored salt
@app.post("/api/login")
def login_verified():
    data = request.get_json()
    userName = data["userName"]
    passAttempt = data["passwordAttempt"]
    hashPassAttempt = passAttempt + salt
    hashPassAttempt = hashlib.sha256(bytes(hashPassAttempt))


@app.get("/api/leaderboard/<string:userName>")
def get_user_points():

