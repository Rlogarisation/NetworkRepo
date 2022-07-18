"""
Assignment for 2022T2 COMP3331
Python 3
Usage: python3 server.py server_port number_of_consecutive_failed_attempts
coding: utf-8

Author: Zheng Luo (z5206267)
"""
from socket import *
from threading import Thread
from helper import *
import sys, select, time

namedTuple = time.localtime()
timeString = time.strftime("%d %b %Y, %H:%M:%S", namedTuple)


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

activeUser = 0
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
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        activeUser += 1
        
        
    def run(self):
        message = ''
        currentLoginAttempt = 0
        
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            message = data.decode().split()
            
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if len(message) < 2:
                self.clientAlive = False
                print("===== the user disconnected - ", clientAddress)
                break
            
            # handle message from the client
            print(message)
            username = ''
            BCMmsgCounter = 0
            command = message[0]
            operationType = message[1]
            if command == 'login':
                print("[recv] New login request")
                if operationType == "username":
                    self.clientSocket.send(f"{operationType}{str(usernameExist(message[2]))}".encode())
                if operationType == "auth":
                    result = userAuthenticator(message[2], message[3])
                    self.clientSocket.send(f"{operationType}{str(result)}".encode())
                    if result:
                        username = message[2]
                        # TODO: Need to replace the seq number, client IP address, and include client UDP server port number
                        recordTimestamp(1, message[2])
                # TODO: if currentLoginAttempt == failAttempts:

                currentLoginAttempt += 1
            elif command == 'BCM':
                BCMmsg = ""
                for i in range(2, len(message)):
                    BCMmsg += message[i] + ' '
                print(BCMmsg)
                # Reply to client
                self.clientSocket.send(f"BCM {BCMmsgCounter} {timeString}".encode())
                # Record BCM msg.
                recordBCM(BCMmsgCounter, username, BCMmsg)
                BCMmsgCounter += 1
                
                
    
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
