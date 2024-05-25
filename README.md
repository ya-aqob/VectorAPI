VectorAPI

VectorAPI is an API built with Flask and GoogleAPI/SheetsAPI to manage data for the RecycleQuest app. It handles account creation, login authentication, point records with timestamps, leaderboard creation and sorting, and more.

-------------------------------------------------------------------------------------

Routes:

POST
/api/users

Inputs:
userName, password, displayName, county

Processes:
creates and initializes new user account

Response Body:
userID: {userName} created successfully, points: User {userName} has the ID {userID}

-------------------------------------------------------------------------------------

POST
/api/points

Inputs: UserName, recycledItems, disposedItems, triviaCompletion, questPoints

Processes: updates points, calculates new level if applicable, records time and commits to log

Response Body (will be fixed soon TM):
update: User {userName}'s points have been updated. {itemsRecycled}, {itemsDisposed}, {newPoints}

-------------------------------------------------------------------------------------

POST
/api/login

Inputs: userName, passwordAttempt

Processes: Hashes passwordAttempt, checks hashed attempt against hashed real password

Response Body:
"loginStatus": loginStatus
loginStatus = 0 or 1

-------------------------------------------------------------------------------------

GET
/api/profile/<string:userName>

Inputs: username via route

Processes: Fetches user information from DB

Response Body:
"username": userName, "userPoints": userPoints, "userLevel": userLevel, "userCounty": userCounty, "userRecycle": userRecycle, "userTrash": userTrash

-------------------------------------------------------------------------------------

GET
/api/leaderboard

Processes: sorts leaderboard by points

Response Body:
sortedLeaderboard: sortedLB

sortedLB = list of nested tuples
-------------------------------------------------------------------------------------

GET
/api/progress/<string:userName>

Inputs: userName via route

Processes: fetches each individual commit with timestamp

Response Body:
"commits": {commit0: {"day": day, "month": month, "points": points, "weekday": weekday abbreviated, "year": year}, commitn: {"day": day, "month": month, "points": points, "weekday": weekday abbreviated, "year": year}}




