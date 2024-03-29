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
triviaConstant = 2
#3 is the start of level 2, since level is initialized to 0
levelPoints = [3, 10, 25, 50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 10000000, 10000000]

key_path = r"/etc/secrets/recyclequest-key"
sheet_id = '1H1-5p2iVq1dg0X31dbopoEbIa_gALT8je-Rom1XfIYM'
creds = None
if os.path.exists(key_path):
    creds = service_account.Credentials.from_service_account_file(key_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
service = build("sheets", "v4", credentials=creds)
spreadsheet_identifier = "1H1-5p2iVq1dg0X31dbopoEbIa_gALT8je-Rom1XfIYM"
value_input_option = 'USER_ENTERED'
range_name = 'Sheet1!A2:Z'
pointsRange = 'PointLog!A2:Z'
userID_range = 'Sheet!B:B'

app = Flask(__name__) #starts flask app

if __name__ == '__main__':
    app.run(debug=False)


# creates new user
def create_user(spreadsheet_id, range_name, value_input_option, _values):
    try:    
        values = _values
        resource = {
            "majorDimension": "ROWS",
            "values": values}
        result = (service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_name, body=resource, valueInputOption=value_input_option).execute())
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")

# updates user information
def update(values, spreadsheet_id, range_name):
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption='USER_ENTERED', body=body).execute()
    if str(result.get('updatedCells')) != 0:
        return {'success': "Updated Successful"}
    return {'success': "Updated Failed"}

# creates log for points
def pointLog(spreadsheet_id, range_name, _values):
    values = _values
    resource = {
        "majorDimension": "ROWS",
            "values": values}
    result = (service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_name, body=resource, valueInputOption=value_input_option).execute())
    return result

# used as sort key for leaderboard
def value_getter(item):
    return item[1]

#creates user and initializes values to zero
@app.post("/api/users")
def new_user():
    data = request.get_json()
    userName = data["userName"]
    points = 0
    level = 1
    county = data["county"]
    displayName = data["displayName"]
    recycledItems = 0
    trashItems=0
    userID = hash(time.time())
    unhashedPass = data["password"]
    salt = str(os.urandom(random.randint(0, 5)))
    unhashedPass = (unhashedPass+salt)
    unhashedPass = unhashedPass.encode('ascii', 'utf-8')
    hashedPass = hashlib.sha256(bytes(unhashedPass)).hexdigest()
    create_user(spreadsheet_identifier, range_name, value_input_option, [[str(userName), str(userID), str(hashedPass), str(salt), str(points), str(level), str(county), str(recycledItems), str(trashItems),str(displayName), str(0), str(0)]])
    return {"userID": f"User {userName} created successfully.", "points": f"User {userName} has the ID {userID}."}
 
#adds new points for a given user based on recycled items from client
@app.post("/api/points")
def update_leaderboard():
    data = request.get_json()
    userName = data["userName"]
    itemsRecycled = int(data["recycledItems"])
    itemsDisposed = int(data["disposedItems"])
    triviaPoints = int(data["triviaCompletion"])
    questPoints = int(data["questPoints"])
    newPoints = recycleConstant * itemsRecycled + trashConstant * itemsDisposed + triviaConstant * triviaPoints
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_identifier, range=range_name, valueRenderOption="UNFORMATTED_VALUE").execute()
    values = result.get('values',[])
    for line in values:
        if line[0] == userName:
            userLevel = line[5]
            totalPoints = line[4] + newPoints
            line[4] = totalPoints
            line[7] = line[7] + itemsRecycled
            line[8] = line[8] + itemsDisposed
            line[10] = line[10] + triviaPoints
            line[11] = line[11] + questPoints
            i = userLevel - 1
            while totalPoints >= levelPoints[i]:
                userLevel += 1
                i += 1
            line[5] = userLevel
    update(values=values, spreadsheet_id=spreadsheet_identifier, range_name=range_name)
    values = time.strftime("%a %d %B %Y %H:%M").split()
    values.insert(0, userName)
    values.insert(6, newPoints)
    values.insert(7, triviaPoints)
    values.insert(8, questPoints)
    values.insert(9, itemsDisposed)
    values.insert(10, itemsRecycled)
    pointLog(spreadsheet_identifier, pointsRange, [values])
    return {"update": f"User {userName}'s points have been updated. User's new level is {userLevel}"}

# gets user information for single user
@app.get("/api/profile/<string:userName>")
def user_information(userName):
    userName = userName
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_identifier, range=range_name, valueRenderOption="UNFORMATTED_VALUE").execute()
    values = result.get('values',[])
    for line in values:
        if line[0] == userName:
            userPoints = line[4]
            userLevel = line[5]
            userCounty = line[6]
            userRecycle = line[7]
            userTrash = line[8]
            displayName = line[9]
    return{"username": userName, "userPoints": userPoints, "userLevel": userLevel, "userCounty": userCounty, "userRecycle": userRecycle, "userTrash": userTrash, "displayName": displayName}

# gets leaderboard data and returns it as set of tuples with username and points
@app.get("/api/leaderboard")
def get_leaderboard():
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_identifier, range=range_name, valueRenderOption="UNFORMATTED_VALUE").execute()
    values = result.get('values',[])
    unsortedLB = {}
    for line in values:
        unsortedLB[line[0]] = line[4]
    sortedLB = sorted(unsortedLB.items(), key=lambda item: item[1], reverse=True)
    return {"sortedLeaderboard": sortedLB}

@app.get("/api/progress/<string:userName>")
def progress_check(userName):
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_identifier, range=pointsRange, valueRenderOption="UNFORMATTED_VALUE").execute()
    values = result.get('values',[])
    commitLog = {}
    commitCount = 0
    for line in values:
        if line[0] == userName:
            commitLog[f"commit{commitCount}"] = {"weekday": line[1], "day": line[2], "month": line[3], "year": line[4], "points": line[6]}
            commitCount += 1
    return{"commits": commitLog}
    

@app.post("/api/login")
def login_verification():
    data = request.get_json()
    userName = data["userName"]
    testPassword = data["passwordAttempt"]
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_identifier, range=range_name, valueRenderOption="UNFORMATTED_VALUE").execute()
    values = result.get('values',[])
    returnCheck = 0
    for line in values:
        if line[0] == userName:
            salt = line[3]
            passAttempt = (testPassword + salt)
            passAttempt = passAttempt.encode('ascii', 'utf-8')
            testPassword = hashlib.sha256(bytes(passAttempt)).hexdigest()
            realPassword = line[2]
            if realPassword == testPassword:
                returnCheck = 1
                return {"loginStatus": "1"}
            else:
                returnCheck = 1
                return {"loginStatus": "0"}
    if returnCheck != 1:
        return {"loginStatus": "0", "error": "An error has occurred"}

