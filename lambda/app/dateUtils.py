from datetime import datetime

def toDate(dateStr):
    return datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%SZ")

def dateIsInThePast(dateStr):
    return toDate(dateStr) < datetime.now()