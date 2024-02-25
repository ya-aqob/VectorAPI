from flask import Flask, request
import os
import psycopg2
from dotenv import load_dotenv
from dotenv import find_dotenv
import hashlib, time
import random

#notes and to-do list
#leaderboard sorting

# path = placeholder sets path to .env file
load_dotenv(verbose=True) # loads .env file
url = os.getenv("DATABASE_URL") # gets url from .env file
application = Flask(__name__) #starts flask app
connection = psycopg2.connect(url) #creates database connection

#constant group
CREATE_USER_TABLE = ("CREATE TABLE IF NOT EXISTS userinfo (username TINYTEXT, userid INT, password CHAR, salt CHAR);") # creates new user table
CREATE_LEADERBOARD_TABLE = ("CREATE TABLE IF NOT EXISTS leaderboard (id INT, points INT);") # creates new leaderboard table
INSERT_USER_INFORMATION = ("INSERT INTO userinfo (username, userid, password) VALUES (%s, %s, %s);") # creates new user in user table
INSERT_USER_LEADERBOARD = ("INSERT INTO leaderboard (id, points) VALUES (%d, %d)") # creates new user in leaderboard table
UPDATE_NEW_POINTS = "UPDATE leaderboard SET points = {%d} WHERE id = {%d}; " # adds points for given user
FIND_USER_ID = "SELECT userid from userinfo WHERE username = {%s}" # grabs userid based on what username is
SELECT_PASSWORD_VERIFICATION = "SELECT password, salt from userinfo WHERE userid = {%d}" # grabs saved hashed password and salt
recycleConstant = 4 # points per item recycled
disposalConstant = 3 # points per item disposed

# creates user table and leaderboard table if none exists, adds new user with username and theoretically unique hashed userID and password, initializes points to zero for given user
@application.post("/api/users")
def create_user():
    data = request.get_json()
    userName = data["userName"]
    userID = hash(time.time())
    unhashedPass = data["password"]
    salt = string(os.random(random.randint(0, 5)))
    unhashedPass = (unhashedPass+salt)
    hashedPass = hashlib.sha256(bytes(unhashedPass)).hexdigest()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USER_TABLE)
            cursor.execute(INSERT_USER_INFORMATION, (userName, userID, hashedPass, salt))
            cursor.execute(CREATE_LEADERBOARD_TABLE)
            cursor.execute(INSERT_USER_LEADERBOARD, (userID, 0))
    return {"userID": f"User {userName} created successfully.", "points": f"User {userName} has the ID {userID}."}

# adds new points for a given user based on recycled items from client, the execute may or may not work
@application.post("/api/leaderboard")
def update_leaderboard():
    data = request.get_json()
    userName = data["userName"]
    itemsRecycled = data["recycledItems"]
    itemsDisposed = data["disposedItems"]
    newPoints = recycleConstant * itemsRecycled + disposalConstant * itemsDisposed
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(FIND_USER_ID, (userName))
            userID = cursor.fetchall()
            for row in userID:
                userID = row[0]
            cursor.execute(UPDATE_NEW_POINTS, (userID, newPoints))
    return {"User": f"{userName} has earned "}

# tests password attempt against hashed password and stored salt
@application.post("/api/login")
def login_verified():
    data = request.get_json()
    userName = data["userName"]
    passAttempt = data["passwordAttempt"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(FIND_USER_ID, (userName))
            userID = cursor.fetchall()
            for row in userID:
                userID = row[0]
            cursor.execute(SELECT_PASSWORD_VERIFICATION, (userID))
            passwordInfo = cursor.fetchall()
            for row in passwordInfo:
                hashedPassword = row[0]
                salt = row[1]
    hashPassAttempt = passAttempt + salt
    hashPassAttempt = hashlib.sha256(bytes(hashPassAttempt))
    if hashPassAttempt == hashedPassword:
        return {"verificationStatus": f"{userName} has successfully been verified."}
    else:
        return {"verificationStatus": f"User not successfully verified."}


@application.get("/api/leaderboard/<string:userName>")
def get_user_points(userName):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(FIND_USER_ID, (userName))
            userID = cursor.fetchall()
            for row in userID:
                userID = row[0]
            cursor.execute(FIND_USER_ID, (userName))
            points = cursor.fetchall()
            for row in points:
                userPoints = row[0]
    return {"pointsStatus": f"{userName} has {userPoints} points."}

