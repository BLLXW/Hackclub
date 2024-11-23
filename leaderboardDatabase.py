import sqlite3 as sql

def createLeaderboardTable():
    database = sql.connect("theDatabase.sqlite")
    c = database.cursor()
    
    # delete leaderboard table if already exists
    c.execute("DROP TABLE IF EXISTS tblLeaderboard")
    
    # create leaderboard table
    c.execute("CREATE TABLE tblLeaderboard (Username TEXT NOT NULL, TimeSurvived INTEGER NOT NULL)")
    
    database.commit()
    database.close()
    
def addScore(username, timeSurvived):
    database = sql.connect("theDatabase.sqlite")
    c = database.cursor()
    
    c.execute("INSERT INTO tblLeaderboard (Username, TimeSurvived) VALUES (?, ?)", (username, timeSurvived))
    
    database.commit()
    database.close()
    
def getTopScores():
    database = sql.connect("theDatabase.sqlite")
    c = database.cursor()
    
    c.execute("SELECT Username, TimeSurvived FROM tblLeaderboard ORDER BY TimeSurvived ASC")
    
    scores = c.fetchall()
    database.close()
    
    return scores