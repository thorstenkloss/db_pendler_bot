# db_pendler telegram bot

Commuting is annoying, but even more annoying are trains that are delayed. Unfortunately 'Deutsche Bahn' has no proper alerts to inform you about delayed and cancelled trains without manually checking schedules. Checking the diffent apps on your mobile phone every morning corrupts your super efficient, streamlined morning routine. db_pendler_bot is here to help.

Currently db_pendler is in the prototyping stage. I am not responsible for you missing your trains or the bot missing alarms causing you to loose valuable moments of your life.

## Getting Started

You can try the bot at https://t.me/db_pendler_bot. Be kind, he is sensitive in his early days!


### Description

'Deutsche Bahn' makes it especially difficult to work with their apis. Either it is slow, provides insufficient information or is not there at all.
This is why this bot connects to two apis:
* [1BahnQL](https://github.com/dbsystel/1BahnQL) (Yes! They are offering graphQL! But unfortunately it is not used to its capacity at all...)
* [db-rest](https://github.com/derhuerst/db-rest) (A private API wrapping around several APIs from DB)

The bot uses two SQLite databases. 
One to store your data (telegram id, station, train, time and direction). Yes, I will sell your data to criminals. They will rob your flat while you commute! Just kidding, but the bot needs to know where you start your ride.
A second one to collect information about which train will leave when. The db-rest-api does not send the time if a train is cancelled, so this is why I need to sample the schedule or interpolate.
And I can build up statistics that way. Everyone loves statistics, right?

From here it monitors the connection you specify and sends you a daily text 20 minutes before your intended time to leave.
It only does that for the station you specified, not for the whole trip. db_pendler_bot is not that smart. Yet.

### Installation

If you want to run the bot yourself, you need to register a telegram bot with the [botfather](https://t.me/BotFather) and put it into the db_pendler_bot.py file.
For the 1BahnQL API you need an API-key from the [DB Developer-Portal](https://developer.deutschebahn.com/store/apis/info?name=1BahnQL-Free&version=v1&provider=DBOpenData). This one goes into the header variable in the trainfunctions.py file



## ToDo

The bot is far from perfect. I will continue working on it. This is a quick prototype... The temperatures are cold right now and the Deutsche Bahn is not able to handle that. So the need for db_pendler_bot is there right now...

* proper support for busses and for regional/national trains
* more finegrained monitoring shortly before the scheduled time (currently only a single check)
* settings
* weekday/every day selection
* proper exception handling
* multiple trips to monitor
* NOW-function to check manually for delays
* probably a lot more...