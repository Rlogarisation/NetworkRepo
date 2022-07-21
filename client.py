"""
Assignment for 2022T2 COMP3331
Python 3
Usage: python3 client.py SERVER_IP SERVER_PORT CLIENT_UDP_SERVER_PORT
coding: utf-8

Author: Zheng Luo (z5206267)
"""
from socket import *
import sys

commandPrompting = "\
======================The following commands are available:======================\n\
BCM: Public messages, usage: BCM message\n\
ATU: Display active users, usage: ATU\n\
SRB: Separate room building, usage: SRB username1 username2 ...\n\
SRM: Separate room message, usage: SRM roomID message\n\
RDM: Read messages, usage: RDM messageType(b or s) timestamp(1 Jun 2022 16:00:00)\n\
OUT: Log out, usage: OUT\n\
UPD: Upload file, usage: UPD username filename\n\
Please enter the command as suggested by usage:\n"
acceptedCommand = ["BCM", "ATU", "SRB", "SRM", "RDM", "OUT", "UPD"]

#Server would be running on the same host as Client
if len(sys.argv) != 4:
    print("\n===== Error usage, python3 client.py SERVER_IP SERVER_PORT CLIENT_UDP_SERVER_PORT======\n")
    exit(0)
serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
UDPServerPort = sys.argv[3]
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
            print("Login in successfully! Welcome!")
            portInfoMsg = f"login port {username} {UDPServerPort}"
            clientSocket.sendall(portInfoMsg.encode())
            break
        else:
            print("Password incorrect, please try again.")
    # There is no such username.
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
            if command == "BCM" and len(inputList) < 2:
                print("===== Error usage, BCM message======\n")
            elif command == "SRB" and len(inputList) < 2:
                print("===== Error usage, SRB username1 username2 ...======\n")
            elif command == "SRM" and len(inputList) < 3:
                print("===== Error usage, SRM roomID message======\n")
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
    elif command == "ATU":
        clientSocket.sendall("ATU".encode())
        data = clientSocket.recv(1024)
        ATUResponse = data.decode()
        print(ATUResponse)
    elif command == "SRB" or command == "SRM" or command == "RDM":
        clientSocket.sendall(inputmsg.encode())
        data = clientSocket.recv(1024)
        print(data.decode())
    elif command == "OUT":
        print("Goodbye! See you next time!")
        clientSocket.sendall(inputmsg.encode())
        break
        
# close the socket
clientSocket.close()
