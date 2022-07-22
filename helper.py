"""
Assignment for 2022T2 COMP3331
Python 3
Usage: python3 client.py SERVER_IP SERVER_PORT
coding: utf-8

Author: Zheng Luo (z5206267)
"""

import time, os
from datetime import datetime

def usernameExist(username):
    '''
    Check whether username is existed in credentials.txt
    @Input username as String type 
    @Output The function will return true if existed, else false.
    '''
    with open("credentials.txt") as file:
        for i in file.readlines():
            if i.split()[0] == username:
                return True
        return False

def userAuthenticator(username, password):
    '''
    Check whether username and password are identical as shown in credentials.txt
    @Input username and password as String types
    @Output The function will return true if identical, else false.
    '''
    with open("credentials.txt") as file:
        for i in file.readlines():
            info = i.split()
            if username == info[0] and password == info[1]:
                return True 
        return False

def userInBlockedList(username, blockedList):
    '''
    Check whether username is contained in the blocked list for login.
    @Input username as String type and blockedList in the format of 
        [
            {
                "username": username,
                "blockedTime": printCurrentTime()
            }
        ]
    @Output The function will return true if contained, else false.
    '''
    for name in blockedList:
        if username == name["username"]:
            return True
    return False


def updateActiveUserLog(activeUserList):
    '''
    Update the user log file based on the given active user list.
    @Input activeUserList in the format of
        [
            {
                'username':username,
                'address':self.clientAddress,
                'UDPPortNumber':UDPportNumber,
                'activeTime': loginInTime
            }
        ]
    @Output The function do not have an output.
    '''
    resetUserlog()
    file = open("userlog.txt", "a")
    for index, user in enumerate(activeUserList):
        currentUserActiveTime = user["activeTime"]
        currentUsername = user["username"]
        currentClientIP = user["address"][0]
        currentUDPPortNumber = user["UDPPortNumber"]
        file.write(f"{index + 1}; {currentUserActiveTime}; {currentUsername}; {currentClientIP}; {currentUDPPortNumber}\n")
    file.close()

def resetUserlog():
    '''
    Remove the user log in the current directory.
    '''
    if os.path.exists("userlog.txt"):
        os.remove("userlog.txt")

def recordBCM(msgNumber, time, username, msg):
    '''
    Record BCM message into messagelog.txt file.
    @Input msgNumber in Integer, 
    @Input time in the format of %d %b %Y %H:%M:%S,
    @Input username and msg in String
    '''
    file = open("messagelog.txt", "a")
    file.write(f"{msgNumber}; {time}; {username}; {msg}\n")
    file.close()

def resetBCMRecord():
    '''
    Remove the message log in the current directory.
    '''
    if os.path.exists("messagelog.txt"):
        os.remove("messagelog.txt")

def printCurrentTime():
    '''
    Return the current time in the String format of %d %b %Y %H:%M:%S.
    @Output time in String
    '''
    namedTuple = time.localtime()
    return time.strftime("%d %b %Y %H:%M:%S", namedTuple)

def userIsActive(username, activeUserList):
    '''
    Check whether user is active based on given active user list.
    @Input username in String, activeUserList in the format of 
        [
            {
                'username':username,
                'address':self.clientAddress,
                'UDPPortNumber':UDPportNumber,
                'activeTime': loginInTime
            }
        ]
    @Output the function will return true if found, else false.
    '''
    for user in activeUserList:
        if username == user["username"]:
            return True
    return False

def repeatedRoomIsExist(roomList, userList):
    '''
    Check whether the given users have already created the chat room or not.
    @Input roomList in the format of
        [
            {
                "roomID": currentRoomID,
                "memberList": currentMemberList,
                "message":[
                    {
                        "messageNumber": currentNumberOfMsg + 1,
                        "sentTime": currentTime,
                        "sender": username,
                        "content": SRMInputMsg
                    }
                ]
            }
        ]
    @Input userList in the format of [username].
    @Output the function will return the room Id as integer 
    if there is room created by same group of people, else false.
    '''
    for room in roomList:
        if set(room["memberList"]) == set(userList):
            return room["roomID"]
    return None

def roomIsExist(roomID, roomList):
    '''
    Check whether given room Id is in the room list.
    @Input roomID is unique identifier integer,
    @Input roomList in the format of
        [
            {
                "roomID": currentRoomID,
                "memberList": currentMemberList,
                "message":[
                    {
                        "messageNumber": currentNumberOfMsg + 1,
                        "sentTime": currentTime,
                        "sender": username,
                        "content": SRMInputMsg
                    }
                ]
            }
        ]
    @Output the function will return true if room existed, else false.
    '''
    for room in roomList:
        if roomID == room["roomID"]:
            return True
    return False

def memberIsPartOfRoom(username, roomId, roomList):
    '''
    Check whether given user is part of the chat room
    @Input username in String,
    @Input roomId is unique identifier integer,
    @Input roomList in the format of
        [
            {
                "roomID": currentRoomID,
                "memberList": currentMemberList,
                "message":[
                    {
                        "messageNumber": currentNumberOfMsg + 1,
                        "sentTime": currentTime,
                        "sender": username,
                        "content": SRMInputMsg
                    }
                ]
            }
        ]
    @Output the function will return true if user is part of chat room, else false.
    '''
    for room in roomList:
        if room["roomID"] == roomId and username in room["memberList"]:
            return True
    return False

def recordSRM(roomID, msgNumber, time, username, msg):
    '''
    Record the message history in the chat room as SR_{roomID}_messageLog.txt file.
    @Input roomId: the unique integer for each chat room,
    @Input msgNumber: the unique integer for message in the chat room,
    @Input time: String in format of %d %b %Y %H:%M:%S
    @Input username, msg in String.
    '''
    file = open(f"SR_{roomID}_messageLog.txt", "a")
    file.write(f"{msgNumber}; {time}; {username}; {msg}\n")
    file.close()

# def resetSRMRecord():
#     if os.path.exists("messagelog.txt"):
#         os.remove("messagelog.txt")

def timeComparator(timeA, timeB):
    '''
    The function can compare the given time A and given time B.
    @Input timeA and timeB as String in the format of %d %b %Y %H:%M:%S.
    @Output the function will return -1 if A is less than B, else return 1.
    '''
    convertedTimeA = datetime.strptime(timeA, "%d %b %Y %H:%M:%S")
    convertedTimeB = datetime.strptime(timeB, "%d %b %Y %H:%M:%S")
    if convertedTimeA < convertedTimeB:
        return -1
    else :
        return 1
