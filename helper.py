"""
Assignment for 2022T2 COMP3331
Python 3
Usage: python3 client.py SERVER_IP SERVER_PORT
coding: utf-8

Author: Zheng Luo (z5206267)
"""

import time, os

def usernameExist(username):
    with open("credentials.txt") as file:
        for i in file.readlines():
            if username == i.split()[0]:
                return True
    return False

def userAuthenticator(username, password):
    with open("credentials.txt") as file:
        for i in file.readlines():
            info = i.split()
            if username == info[0] and password == info[1]:
                return True 
    return False

def recordTimestamp(seq, username, clientIP, UDPPort):
    file = open("userlog.txt", "a")
    file.write(f"{seq}; {printCurrentTime()}; {username}; {clientIP}; {UDPPort}\n")
    file.close()

def resetUserlog():
    if os.path.exists("userlog.txt"):
        os.remove("userlog.txt")

def recordBCM(msgNumber, username, msg):
    file = open("messagelog.txt", "a")
    file.write(f"{msgNumber}; {printCurrentTime()}; {username}; {msg}\n")
    file.close()

def resetBCMRecord():
    if os.path.exists("messagelog.txt"):
        os.remove("messagelog.txt")

def printCurrentTime():
    namedTuple = time.localtime()
    return time.strftime("%d %b %Y %H:%M:%S", namedTuple)