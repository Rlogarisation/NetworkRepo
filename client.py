#!/usr/bin/python3
"""
    Python 3
    Usage: python3 TCPClient3.py localhost 12000
    coding: utf-8
    
    Author: Wei Song (Tutor for COMP3331/9331)
"""
from socket import *
import sys

#Server would be running on the same host as Client
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT ======\n")
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



# close the socket
clientSocket.close()
