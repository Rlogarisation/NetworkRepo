"""
Assignment for 2022T2 COMP3331
Python 3
Usage: python3 client.py SERVER_IP SERVER_PORT
coding: utf-8

Author: Zheng Luo (z5206267)
"""
from socket import *
import sys

commandPrompting = "The following commands are available: \n\
BCM: Broadcast messages to all the active users i.e. public messages \n\
ATU: Display active users, \n\
SRS: Separate chat room service, in which users can build a separate room for part of active users and send messages in the separate room\n\
RDM: Read messages, \n\
OUT: Log out, \n\
UPD: Upload file \n\
Please enter the command, and the arguments separate by white space: "
acceptedCommand = ["BCM", "ATU", "SRS", "RDM", "OUT", "UPD"]

#Server would be running on the same host as Client
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 client.py SERVER_IP SERVER_PORT ======\n")
    exit(0)
serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
serverAddress = (serverHost, serverPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# build connection with the server and send message to it
clientSocket.connect(serverAddress)

while True:
    # Check username input:
    username = input("Enter your username: ").strip()
    usernameMsg = f"login username {username}"
    clientSocket.sendall(usernameMsg.encode())

    # Receive response from the server
    data = clientSocket.recv(1024)
    usernameResponse = data.decode()

    # Username has been found in the database.
    while usernameResponse == "usernameTrue":
        password = input("Enter your password: ").strip()
        authMsg = f"login auth {username} {password}"
        clientSocket.sendall(authMsg.encode())
        data = clientSocket.recv(1024)
        passwordResponse = data.decode()
        if passwordResponse == "authTrue":
            print("Login in successfully!")
            break
        else:
            print("Password incorrect, please try again.")
    # There is no such username, create a new account.
    if usernameResponse == "usernameFalse":
        print("There is no such username, please try again.")
    else:
        break

while True:
    while True:
        inputmsg = input(commandPrompting)
        inputList = inputmsg.split()
        command = inputList[0]
        if command in acceptedCommand:
            if command == "BCM" and len(inputList) == 1:
                print("===== Error usage, BCM MESSAGE======\n")
            else:
                break
        else:    
            print(f"Command {command} is not recognised, please try again!")
    if command == "BCM":
        inputmsg = ""
        for i in range(1, len(inputList)):
            inputmsg += inputList[i] + ' '
        BCMmsg = f"BCM {username} {inputmsg}"
        clientSocket.sendall(BCMmsg.encode())
        data = clientSocket.recv(1024)
        BCMmsgResponse = data.decode()
        print(f"BCM msg has been received at server: {BCMmsgResponse}")
    if command == "OUT":
        break
        
# close the socket
clientSocket.close()
