#-*- coding: utf-8 -*- 
from time import strftime

def getToday():
    year = strftime("%Y")
    month = strftime("%m")
    day = strftime("%d")
    today = year + month + day
    return today

def getLastDayByNum(thisday, num):
    year = thisday[0:4]
    month = thisday[4:6]
    day = thisday[6:8]
    if int(day) > num:
        day = str(int(day) - num) 
    #month判定是否为1月; day=day+上个月的天数-num.
    elif month == "01":
        year = str(int(year) - 1) 
        month = "12"
        day = str(int(day) + 31 - num)
    #month是否为3月，需要进行闰年判定
    elif month == "03":
        month = "02"
        if isRun(int(year)):
            day = str(int(day) + 29 - num)
        else:
            day = str(int(day) + 28 - num)
    #一三五七八十腊
    elif is31(month):
        month = str(int(month) - 1)  
        day = str(int(day) + 31 - num)
    else:
        month = str(int(month) - 1)  
        day = str(int(day) + 30 - num)  
     
    if len(month) == 1:
        month = '0' + month 
    if len(day) == 1:
        day = '0' + day    
    return year + month + day  
         
def isRun(year):
    if (year % 4 == 0) and (year % 100 != 0):
        return True
    elif year % 400 == 0:
        return True
    else:
        return False
def is31(month):
    if month == "2" or month == "4" or month == "6" or month == "8" or month == "9" or month == "11":
        return True
    else:
        return False