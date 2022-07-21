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



# acquire server host and port from command line parameter
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 server.py server_port number_of_consecutive_failed_attempts======\n")
    exit(0)
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)
failAttempts = int(sys.argv[2])
if failAttempts < 1 or failAttempts > 5:
    print(f"\n===== Error usage, Invalid number of allowed failed consecutive attempt: {failAttempts}.======\n")
    exit(0)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

resetUserlog()
resetBCMRecord()
# TODO: reset SRM room records.

BCMMsgList = []
activeUserList = []
separateRoomList = []
"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate thread, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        # WHAT IS CLIENT PORT NUMBER?
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
        
        
    def run(self):
        message = ''
        # currentLoginAttempt = 0
        

        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            message = data.decode().split()
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if len(message) < 1:
                self.clientAlive = False
                print("===== the user disconnected - ", clientAddress)
                break
            
            # handle message from the client
            print(message)
            # username = ''
            command = message[0]
            if command == 'login':
                operationType = message[1]
                print("[recv] New login request")
                if operationType == "username":
                    self.clientSocket.send(f"{operationType}{str(usernameExist(message[2]))}".encode())
                elif operationType == "auth":
                    result = userAuthenticator(message[2], message[3])
                    self.clientSocket.send(f"{operationType}{str(result)}".encode())
                    # TODO: if currentLoginAttempt == failAttempts:
                elif operationType == "port":
                    # Means login successfully, and UDP port has been attached.
                    username = message[2]
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
                # currentLoginAttempt += 1
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
                    ATUMsg = "no other active user"
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
                self.clientSocket.send(SRBMsg.encode())
            elif command == "SRM":
                print(separateRoomList)
                SRMReplyMsg = ""
                SRMInputMsg = ""
                inputRoomID = int(message[1])
                for i in range(2, len(message)):
                    SRMInputMsg += message[i] + " "
                # Check if the room with provided room ID exists
                if not roomIsExist(inputRoomID, separateRoomList):
                    SRMReplyMsg = f"The separate room (ID: {inputRoomID}) does not exist"
                # Check if the client is a member of the separate room
                elif not memberIsPartOfRoom(username, separateRoomList):
                    SRMReplyMsg = f"You are not in this separate room (ID: {inputRoomID})chat"
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
                        currentMsgContent =BCMMsgs["content"]
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
                self.clientSocket.send(RDMReplyMsg.encode())
            elif command == "OUT":
                # Remove current user from activeUserList:
                for user in activeUserList:
                    if user["username"] == username:
                        activeUserList.remove(user)
                # Update the userlog.txt by removing the current user and updating seq.
                updateActiveUserLog(activeUserList)



    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    # def process_login(self):
    #     message = 'user credentials request'
    #     print('[send] ' + message);
    #     self.clientSocket.send(message.encode())


print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()
