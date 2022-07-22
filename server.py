"""
Assignment for 2022T2 COMP3331
Python 3
Usage: python3 server.py server_port number_of_consecutive_failed_attempts
coding: utf-8

Author: Zheng Luo (z5206267)
"""
import sys
from socket import *
from threading import Thread
from helper import *


# Acquire server host and port from command line parameter
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 server.py server_port number_of_consecutive_failed_attempts======\n")
    exit(0)
serverHost = "127.0.0.1"
# Edge case for server port input.
if not (sys.argv[1]).isdigit() or int(sys.argv[1]) < 0 or int(sys.argv[1]) > 65535:
    print("\n===== Error usage, server port valid range is between 0 and 65536======\n")
    exit(0)
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)
# Edge case for fail attempt input.
if not (sys.argv[2]).isdigit() or int(sys.argv[2]) < 1 or int(sys.argv[2]) > 5:
    print(f"\n===== Error usage, the valid range for the number of allowed failed consecutive attempt is between 1 and 5.======\n")
    exit(0)
failAttempts = int(sys.argv[2])

# Define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

# Reset the log files from pervious server history.
resetUserlog()
resetBCMRecord()
# TODO: reset SRM room records.

# Initiate the container for recording user data.
blockedAccList = []
BCMMsgList = []
activeUserList = []
separateRoomList = []

# Define multi-thread class for client
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        print(f"===== New connection created for: {clientAddress} =====")
        self.clientAlive = True
        
    def run(self):
        message = ''
        currentLoginAttempt = 0
        
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(2048)
            message = data.decode().split()
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if len(message) < 1:
                self.clientAlive = False
                print(f"===== The user disconnected - {clientAddress} =====")
                break
            
            # handle message from the client
            print(f"Server has received messsage: {message}")
            command = message[0]
            if command == 'login':
                operationType = message[1]
                username = message[2]
                # Checking the existence of username.
                if operationType == "username":
                    usernameMsg = f"{operationType}{str(usernameExist(username))}"
                    print("Checking username request has been received.")
                    self.clientSocket.send(usernameMsg.encode())
                # Checking the password correctness with given username.
                elif operationType == "auth":
                    print("Authentication request has been received.")
                    authMsg = ""
                    result = userAuthenticator(username, message[3])
                    # Check user is not in blocked list first.
                    if userInBlockedList(username, blockedAccList) and result is False:
                        print(f"User {username} is already in blocked list and password is still incorrect!")
                        authMsg += "Blocked"
                    # Otherwise process with user auth check.
                    else:
                        authMsg = f"{operationType}{str(result)}"
                        currentLoginAttempt += 1
                        if currentLoginAttempt >= failAttempts and result is False:
                            print("The maximum login attmpts have been reached, now blocking this user!")
                            blockedAccList.append(
                                {
                                    "username": username,
                                    "blockedTime": printCurrentTime()
                                }
                            )
                            authMsg += "Blocked"
                    self.clientSocket.send(authMsg.encode())
                # Login successfully, and UDP port has been attached.
                elif operationType == "port":
                    print(f"User {username} has been successfully login!")
                    UDPportNumber = message[3]
                    loginInTime = printCurrentTime()
                    activeUserList.append(
                        {
                            'username':username,
                            'address':self.clientAddress,
                            'UDPPortNumber':UDPportNumber,
                            'activeTime': loginInTime
                        }
                    )
                    updateActiveUserLog(activeUserList)
                    # Remove the user from blockedList if in.
                    for name in blockedAccList:
                        if username == name["username"]:
                            blockedAccList.remove(name)
                    # Reset the currentLoginAttmpt.
                    currentLoginAttempt = 0
            elif command == 'BCM':
                BCMmsg = ""
                for i in range(2, len(message)):
                    BCMmsg += message[i] + ' '
                BCMReceivedTime = printCurrentTime()
                currentBCMMsgLength = len(BCMMsgList)
                # Record BCM msg.
                recordBCM(currentBCMMsgLength + 1, BCMReceivedTime, username, BCMmsg)
                # Append current Msg into BCMMsgList.
                BCMMsgList.append(
                    {
                        "BCMMessageNumber": currentBCMMsgLength + 1,
                        "sentTime": BCMReceivedTime,
                        "sender": username,
                        "content": BCMmsg
                    }
                )
                print(f"{username} broadcasted message{currentBCMMsgLength + 1} at {BCMReceivedTime}: {BCMmsg}")
                # Reply to client
                self.clientSocket.send(f"BCM {currentBCMMsgLength + 1} {BCMReceivedTime}".encode())
            elif command == 'ATU':
                ATUMsg = ""
                for user in activeUserList:
                    listUsername = user["username"]
                    listIPAddress = user["address"][0]
                    listPortNumber = user["address"][1]
                    listTime = user["activeTime"]
                    if not listUsername == username:
                        ATUMsg += f"{listUsername} at IP {listIPAddress} port {listPortNumber} active since {listTime}\n"
                if ATUMsg == "":
                    ATUMsg = "No other active user"
                print(f"The request for checking active user has been received:\n{ATUMsg}")
                self.clientSocket.send(ATUMsg.encode())
            elif command == 'SRB':
                SRBMsg = ""
                currentMemberList = [username]
                # Check all user exist and active.
                for i in range(1, len(message)):
                    if not usernameExist(message[i]):
                        SRBMsg += f"user {message[i]} is not exist!\n"
                    elif not userIsActive(message[i], activeUserList):
                        SRBMsg += f"user {message[i]} is not active!\n"
                    else:
                        currentMemberList.append(message[i])
                
                # Check whether the same room has existed.
                existedRoom = repeatedRoomIsExist(separateRoomList, currentMemberList)
                if existedRoom is not None:
                    SRBMsg = f"A separate room (ID: {existedRoom}) already created for these users"
                # All the provided usernames exist and all the corresponding users are online
                # Create separate room for them:
                if SRBMsg == "":
                    currentRoomID = len(separateRoomList) + 1
                    separateRoomList.append(
                        {
                            "roomID": currentRoomID,
                            "memberList": currentMemberList,
                            "message":[]
                        }
                    )
                    SRBMsg = f"Separate chat room has been created as room ID: {currentRoomID}, users in this room: {currentMemberList}\n"
                print(f"The request for creating separate chat room has been received:\n{SRBMsg}")
                self.clientSocket.send(SRBMsg.encode())
            elif command == "SRM":
                SRMReplyMsg = ""
                SRMInputMsg = ""
                inputRoomID = int(message[1])
                for i in range(2, len(message)):
                    SRMInputMsg += message[i] + " "
                # Check if the room with provided room ID exists
                if not roomIsExist(inputRoomID, separateRoomList):
                    SRMReplyMsg = f"The separate room (ID: {inputRoomID}) does not exist"
                # Check if the client is a member of the separate room
                elif not memberIsPartOfRoom(username, inputRoomID, separateRoomList):
                    SRMReplyMsg = f"User is not in this separate room (ID: {inputRoomID})chat"
                # Append the message, the username, and a timestamp at the end of the message log file
                else:
                    currentTime = printCurrentTime()
                    currentNumberOfMsg = 0
                    
                    # Append the current msg into separated room list.
                    for currentRoom in separateRoomList:
                        if currentRoom["roomID"] == inputRoomID:
                            currentNumberOfMsg = len(currentRoom["message"])
                            currentRoom["message"].append(
                                {
                                    "messageNumber": currentNumberOfMsg + 1,
                                    "sentTime": currentTime,
                                    "sender": username,
                                    "content": SRMInputMsg
                                }
                            )
                    
                    recordSRM(inputRoomID, currentNumberOfMsg + 1, currentTime, username, SRMInputMsg)
                    SRMReplyMsg = f"SRM message {currentNumberOfMsg + 1} has been received at {currentTime}\n"
                print(f"The request for sending message in chat room has been received:\n{SRMReplyMsg}")
                self.clientSocket.send(SRMReplyMsg.encode())
            elif command == "RDM":
                RDMReplyMsg = ""
                messageType = message[1]
                inputTime = ""
                for i in range(2, len(message)):
                    inputTime += message[i] + " "
                # Broadcast information retrival
                if messageType == "b":
                    for BCMMsgs in BCMMsgList:
                        currentMsgSender = BCMMsgs["sender"]
                        currentMsgSentTime = BCMMsgs["sentTime"]
                        currentMsgNumber = BCMMsgs["BCMMessageNumber"]
                        currentMsgContent = BCMMsgs["content"]
                        if timeComparator(inputTime.rstrip(), currentMsgSentTime) < 0:
                            RDMReplyMsg += f"#{currentMsgNumber} {currentMsgSender}@{currentMsgSentTime}: {currentMsgContent}\n"
                # Separate room messages retrival
                elif messageType == "s":
                    for currentRoom in separateRoomList:
                        currentRoomID = currentRoom["roomID"]
                        currentRoomList = currentRoom["memberList"]
                        if username in currentRoomList:
                            for roomMsg in currentRoom["message"]:
                                currentRoomMsgNumber = roomMsg["messageNumber"]
                                currentRoomMsgSender = roomMsg["sender"]
                                currentRoomMsgSentTime = roomMsg["sentTime"]
                                currentRoomMsgContent = roomMsg["content"]
                                if timeComparator(inputTime.rstrip(), currentRoomMsgSentTime) < 0:
                                    RDMReplyMsg += f"Room{currentRoomID} #{currentRoomMsgNumber} {currentRoomMsgSender}@{currentRoomMsgSentTime}: {currentRoomMsgContent}\n"

                if RDMReplyMsg == "":
                    RDMReplyMsg = "No new message"
                print(f"The request for reading messages has been received:\n{RDMReplyMsg}")
                self.clientSocket.send(RDMReplyMsg.encode())
            elif command == "OUT":
                # Remove current user from activeUserList:
                for user in activeUserList:
                    if user["username"] == username:
                        activeUserList.remove(user)
                # Update the userlog.txt by removing the current user and updating seq.
                updateActiveUserLog(activeUserList)
                print(f"The log out request has been received")
            elif command == "UPD":
                UPDMsg = ""
                # check whether given username is active.
                audience = message[1]
                if not usernameExist(audience):
                    UPDMsg = f"Audience {audience} is not existed!"
                elif not userIsActive(audience, activeUserList):
                    UPDMsg = f"audience {audience} is offline!"
                else:
                    for user in activeUserList:
                        if user["username"] == audience:
                            audienceAddress = user["address"]
                            UDPPort = user["UDPPortNumber"]
                            UPDMsg = f"UPD {audienceAddress} {UDPPort}"
                            # TODO: Further implement.
                self.clientSocket.send(UPDMsg.encode())


print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()
