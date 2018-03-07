import requests
import json
import time as t
import datetime
import re
from helperfunctions import *
from dbhelper import DBHelper_train_times

headers = {"Authorization":"Bearer API_KEY_FROM_DEUTSCHE_BAHN_HERE_FOR_1bahnQL"}

trainDB = DBHelper_train_times()
trainDB.setup()

# train-related functions
def graphQLQuery(query):
    """executes query on graphQL-API and returns the response as json"""

    endpoint = "https://api.deutschebahn.com/1bahnql/v1/graphql?query={}".format(query)
    response = requests.get(endpoint, headers=headers)
    jsonResponse = json.loads(response.content)
    return jsonResponse

def searchStations(name):
    """constructs query to search for stations and returns results as json with names and EvaIDs"""

    query = '''{
                search(searchTerm: "%s") {
                  stations {
                    name
                    primaryEvaId
                  }
                }
              }''' % (name)
    result = graphQLQuery(query)
    return result['data']['search']['stations']

def getEvaId(stations, stationName):
    """returns the EvaID from stations json for given stationName"""

    for station in stations:
        if station['name'] == stationName:
            return station['primaryEvaId']
    return -1
    
def getDepartures(evaID):
    """returns next departures from graphQL-API, json with train type, number, platform and time"""

    query = '''{
                    stationWithEvaId(evaId: %s){
                        timetable{
                            nextDepatures{
                                type
                                trainNumber
                                platform
                                time
                            }
                        }
                    }
                }''' % (evaID)
    result =graphQLQuery(query)
    return result['data']['stationWithEvaId']['timetable']['nextDepatures']

def returnTrains(station, train=None, direction=None):
    """returns a list of trains leaving given station during the next 24h. optional: train & direction to prefilter results"""

    trains = []
    url = 'https://1.db.transport.rest/stations/{}/departures?duration=1439'.format(station)
    departures = json.loads(requests.get(url).content)
    for departure in departures:
        if train == None or departure['line']['name'] == train:
            if direction == None or departure['direction'] == direction:
                if departure['line']['product'] in ['national', 'regional', 'regionalExp', 'naitonalExp']:
                    trainName = re.findall("[a-zA-Z]+", departure['line']['name'])[0]
                else:
                    trainName = departure['line']['name']
                trains.append([departure['journeyId'], trainName, departure['when'], departure['direction']])
    return trains

def getNextStops(station, directions):
    """returns uniqueNextStops, nextStopsDirection"""
    
    nextStopsDirection = {}
    uniqueNextStops = []
    query = '''{
              stationWithEvaId(evaId:%s){
                timetable{
                  nextDepatures{
                    stops
                  }
                }
              }
            }''' % station
    results = graphQLQuery(query)['data']['stationWithEvaId']['timetable']['nextDepatures']
    
    for result in results:
        if result['stops'][-1] in directions:
            uniqueNextStops.append(result['stops'][0])
            nextStopsDirection[result['stops'][-1]] = result['stops'][0]
    return list(set(uniqueNextStops)), nextStopsDirection

def checkDelayAndCancelled(station, time, train, direction=None):
    """checks if trains 20min before/after set time are delayed or cancelled"""
    url = 'https://1.db.transport.rest/stations/{}/departures?duration=40&when=today%{}'.format(station, timeTo12h(timeShift(time, -20)))
    departures = json.loads(requests.get(url).content)
    
    delayed = []
    cancelled = []
    onTime = []
    
    for departure in departures:
        if departure['line']['name'] == train:
            if direction == None or departure['direction'] == direction:
                if 'cancelled' in departure.keys():
                    cancelled.append(departure)
                    onTime=False
                elif departure['delay']:
                    delayed.append(departure)
                    onTime=False
                else:
                    onTime.append(departure)
    return delayed, cancelled, onTime


def estimateTrainTime(journeyID, station):
    """tries to estimate the departure time of a journeyID, based on trains before and after given journeyID"""

    url = 'https://1.db.transport.rest/stations/{}/departures?duration=1439&when=today%{}'.format(station, timeTo12h(timeShift('17:50:00', 20)))
    departures = json.loads(requests.get(url).content)
    times = []
    element = int(journeyID[9])
    for departure in departures:
        if departure['journeyId'][:10] == journeyID[:10] and (int(departure['journeyId'][9]) == element+1 or int(departure['journeyId'][9]) == element-1):
            times.append(t.strptime(departure['when'][:-10], '%Y-%m-%dT%H:%M:%S'))
    if len(times) == 2 and times[0] != None and times[1] != None:
        estimate = datetime.datetime(*times[0][:7]) +(datetime.datetime(*times[2][:7])-datetime.datetime(*times[0][:7]))/2
        return estimate.strftime('%H:%M:%S')
    else:
        return '[time (yet) unknown]'

def getTrainTime(journeyID, station):
    """tries to fetch departure times from trainDB, otherwise tries estimateTrainTime()"""

    request = list(trainDB.getDataForJourneyStation(journeyID[:10], station))
    if request != []:
        return request[0][1]
    else:
        return estimateTrainTime(journeyID, station)
    
def getDelayAndCancelled(station, time, train, direction):
    """prepares data for delayed and cancelled trains for output and updates statistics"""

    result = []
    delayed, cancelled, onTime = checkDelayAndCancelled(station, time, train, direction)
    for delay in delayed:
        result.append('{} at {} towards {} is delayed by {} minutes'.format(delay['line']['name'], getTrainTime(delay['journeyId'], delay['station']['id']), delay['direction'], int(delay['delay']/60)))
        trainDB.incDelayed(delay['journeyId'][:10], delay['station']['id'])
    for cancelation in cancelled:
        result.append('{} at {} towards {} is cancelled'.format(cancelation['line']['name'], getTrainTime(cancelation['journeyId'], cancelation['station']['id']), cancelation['direction']))
        trainDB.incCancelled(cancelation['journeyId'][:10], cancelation['station']['id'])
    for train in onTime:
        if list(trainDB.getDataForJourneyStation(train['journeyId'][:10], train['station']['id'])) == []:
            trainDB.add(train['journeyId'][:10], train['station']['id'], train['when'][11:19])
        trainDB.incOnTime(train['journeyId'][:10], train['station']['id'])
    return result