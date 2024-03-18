VectorAPI

VectorAPI is an API built with Flask and GoogleAPI/SheetsAPI to manage data for the RecycleQuest app. It handles account creation, login authentication, point records with timestamps, leaderboard creation and sorting, and more.

-------------------------------------------------------------------------------------

Routes:

POST
/api/users
-takes userName, password, displayName, and county as inputs
-creates new user, initializes stuff

Response Body:
userID: {userName} created successfully, points: User {userName} has the ID {userID}

-------------------------------------------------------------------------------------

POST
/api/points
-takes UserName, recycledItems, disposedItems, triviaCompletion, questPoints
-updates points, calculates new level if applicable, records time and commits to log

Response Body (will be fixed soon TM):
update: User {userName}'s points have been updated. {itemsRecycled}, {itemsDisposed}, {newPoints}

-------------------------------------------------------------------------------------

POST
/api/login
-takes userName and passwordAttempt as input

Response Body:
"loginStatus": loginStatus
loginStatus = 0 or 1, 0 == failure, 1 == success

-------------------------------------------------------------------------------------

GET
/api/profile/<string:userName>
-takes username from http route

Response Body:
"username": userName, "userPoints": userPoints, "userLevel": userLevel, "userCounty": userCounty, "userRecycle": userRecycle, "userTrash": userTrash

-------------------------------------------------------------------------------------

GET
/api/leaderboard
-sorts leaderboard

Response Body (its a list of tuples i think??):
sortedLeaderboard: sortedLB

-------------------------------------------------------------------------------------

GET
/api/progress/<string:userName>
-takes username from http route

Response Body:
"commits": {commit0: {"day": day, "month": month, "points": points, "weekday": weekday abbreviated, "year": year}, commitn: {"day": day, "month": month, "points": points, "weekday": weekday abbreviated, "year": year}}




