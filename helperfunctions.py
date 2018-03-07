def timeTo12h(timestr):
    """converts a 24h-formatted timestring (H)H:(M)M(:SS) into 12h format"""

    if not 'am' in timestr.lower() and not 'pm' in timestr.lower():
        timesplit = [int(number) for number in timestr.split(':')]
        if timesplit[0]>11 and timesplit[0]!=0:
            if timesplit[0]!=12:
                timesplit[0] -= 12
            period = 'pm'
        else:
            if timesplit[0]==0:
                timesplit[0] = 12
            period = 'am'
    
        return str(abs(timesplit[0])) + ':' + str(timesplit[1]) + period
    else:
        return timestr
    
def timeConvert(timeStr):
    """converts a string containing a time in any given form to str(HH:MM:00)"""

    timeStr = timeStr.lower()
    period = timeStr[-2:]
    if period == 'am' or period == 'pm':
        hours = int(timeStr.split(':')[0])
        minutes = int(timeStr.split(':')[1][:-2])
        if period == 'pm' and hours < 12:
            hours += 12
        if period == 'am' and hours == 12:
            hours -= 12

        return "{0:0=2d}".format(hours) + ':' + "{0:0=2d}".format(minutes) + ':00'
    else:
        if len(timeStr) == 8:
            return timeStr
        hours = int(timeStr.split(':')[0])
        minutes = int(timeStr.split(':')[1])

        return "{0:0=2d}".format(hours) + ':' + "{0:0=2d}".format(minutes) + ':00'
    
def timeShift(timeStr, minuteShift):
    """adds minuteShift (int, minutes) to 24h-timestring timeStr. minuteShift can be negative """
    timeSplit = timeStr.split(':')
    hours = int(timeSplit[0])
    minutes = int(timeSplit[1])
    seconds = int(timeSplit[2])
    
    minutes += minuteShift
    if minutes < 0:
        minutes +=60
        hours -= 1
        hours = hours % 24
        
    if minutes > 60:
        minutes -=60
        hours +=1
        hours = hours % 24
    
    return "{0:0=2d}".format(hours) + ':' + "{0:0=2d}".format(minutes) + ':' + "{0:0=2d}".format(seconds) 