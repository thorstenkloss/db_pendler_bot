import sqlite3


class DBHelper_users:
    def __init__(self, dbname="pendler_users.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = """CREATE TABLE IF NOT EXISTS user_time 
                  (user_id int, station text, evaid int, rideTime text, train text, direction text)"""
        self.conn.execute(stmt)
        self.conn.commit()

    def addUser(self, user_id, station, evaid, rideTime, train, direction):
        stmt = """INSERT INTO user_time 
                  (user_id, station, evaid, rideTime, train, direction)
                  VALUES ({}, \"{}\", {}, \"{}\", \"{}\", \"{}\")""".format(user_id, station, evaid, rideTime, train, direction)
        self.conn.execute(stmt)
        self.conn.commit()

    def updateUser(self, user_id, station, evaid, rideTime, train, direction):
        stmt = """UPDATE user_time 
                  SET station = \"{}\", evaid = {}, rideTime = \"{}\", train = \"{}\", direction = \"{}\" 
                  WHERE user_id = {}""".format(station, evaid, rideTime, train, direction, user_id)
        self.conn.execute(stmt)
        self.conn.commit()

    def deleteUser(self, user_id):
        stmt = """DELETE FROM user_time 
                  WHERE user_id = {}""".format(user_id)
        self.conn.execute(stmt)
        self.conn.commit()

    def getDataForUserID(self, user_id):
        stmt = """SELECT station, evaid, rideTime, train, direction 
                  FROM user_time 
                  WHERE user_id = {}""".format(user_id)
        return self.conn.execute(stmt)

    def getAllUserID(self):
        stmt = """SELECT user_id 
                  FROM user_time"""
        return self.conn.execute(stmt)


class DBHelper_train_times:
    def __init__(self, dbname="pendler_times.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = """CREATE TABLE IF NOT EXISTS train_times 
                  (journeyID text, station text, rideTime text, onTime int, delayed int, cancelled int)"""
        self.conn.execute(stmt)
        self.conn.commit()

    def add(self, journeyID, station, rideTime):
        stmt = """INSERT INTO train_times 
                  (journeyID, station, rideTime, onTime, delayed, cancelled) 
                  VALUES (\"{}\", \"{}\", \"{}\", {}, {}, {})""".format(journeyID, station, rideTime, 0, 0, 0)
        self.conn.execute(stmt)
        self.conn.commit()

    def incOnTime(self, journeyID, station):
        stmt = """UPDATE train_times 
                  SET onTime = onTime + 1 
                  WHERE journeyID = \"{}\" AND station = \"{}\"""".format(journeyID, station)
        slef.conn.execute(stmt)
        self.conn.commit()

    def incDelayed(self, journeyID, station):
        stmt = """UPDATE train_times 
                  SET delayed = delayed + 1 
                  WHERE journeyID = \"{}\" AND station = \"{}\"""".format(journeyID, station)
        slef.conn.execute(stmt)
        self.conn.commit()

    def incCancelled(self, journeyID, station):
        stmt = """UPDATE train_times 
                  SET cancelled = cancelled + 1 
                  WHERE journeyID = \"{}\" AND station = \"{}\"""".format(journeyID, station)
        slef.conn.execute(stmt)
        self.conn.commit()

    def deleteJourney(self, journeyID):
        stmt = """DELETE FROM train_times 
                  WHERE journeyID = \"{}\"""".format(journeyID)
        self.conn.execute(stmt)
        self.conn.commit()

    def getDataForJourney(self, journeyID):
        stmt = """SELECT station, rideTime, onTime, delayed, cancelled 
                  FROM train_times WHERE journeyID = \"{}\"""".format(journeyID)
        return self.conn.execute(stmt)

    def getDataForJourneyStation(self, journeyID, station):
        stmt = """SELECT station, rideTime, onTime, delayed, cancelled 
                  FROM train_times 
                  WHERE journeyID = \"{}\" AND station = \"{}\"""".format(journeyID, station)
        return self.conn.execute(stmt)

    def getDataForStation(self, station):
        stmt = """SELECT station, rideTime, onTime, delayed, cancelled 
                  FROM train_times 
                  WHERE station = \"{}\"""".format(station)
        return self.conn.execute(stmt)

    def getAllJourneys(self):
        stmt = """SELECT journeyID 
                  FROM train_times"""
        return self.conn.execute(stmt)
