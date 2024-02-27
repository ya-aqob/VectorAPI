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

# constants
recycleConstant = 4
trashConstant = 3

key_path = r"/etc/secrets/recyclequest-key"
sheet_id = '1H1-5p2iVq1dg0X31dbopoEbIa_gALT8je-Rom1XfIYM'
creds = None
if os.path.exists(key_path):
    creds = service_account.Credentials.from_service_account_file(key_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
service = build("sheets", "v4", credentials=creds)
spreadsheet_identifier = "1H1-5p2iVq1dg0X31dbopoEbIa_gALT8je-Rom1XfIYM"
value_input_option = 'USER_ENTERED'
range_name = 'Sheet1!A:A';

app = Flask(__name__) #starts flask app

if __name__ == '__main__':
    app.run(debug=False)


# creates user
def create_user(spreadsheet_id, range_name, value_input_option, _values):
    try:    
        values = _values
        resource = {
            "values": values}
        result = (service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption=value_input_option, insertDataOption='INSERT_ROWS', body=resource).execute())
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")


#creates user and initializes values to zero
@app.post("/api/users")
def new_user():
    data = request.get_json()
    userName = data["userName"]
    points = 0
    level = 0
    county = data["county"]
    recycledItems = 0
    trashItems=0
    userID = hash(time.time())
    unhashedPass = data["password"]
    salt = str(os.urandom(random.randint(0, 5)))
    unhashedPass = (unhashedPass+salt)
    unhashedPass = unhashedPass.encode('ascii', 'utf-8')
    hashedPass = hashlib.sha256(bytes(unhashedPass)).hexdigest()
    create_user(spreadsheet_identifier, range_name, value_input_option, [[str(userName), str(userID), str(hashedPass), str(salt), str(points), str(level), str(county), str(recycledItems), str(trashItems)]])
    return {"userID": f"User {userName} created successfully.", "points": f"User {userName} has the ID {userID}."}
 
#adds new points for a given user based on recycled items from client
@app.post("/api/points")
def update_leaderboard():
    data = request.get_json()
    userName = data["userName"]
    itemsRecycled = data["recycledItems"]
    itemsDisposed = data["disposedItems"]
    newPoints = recycleConstant * itemsRecycled + trashConstant * itemsDisposed



# tests password attempt against hashed password and stored salt
#@app.post("/api/login")
#def login_verified():
 #   data = request.get_json()
  #  userName = data["userName"]
   # passAttempt = data["passwordAttempt"]
    #hashPassAttempt = passAttempt + salt
    #hashPassAttempt = hashlib.sha256(bytes(hashPassAttempt))


#@app.get("/api/leaderboard/<string:userName>")
#def get_user_points():

