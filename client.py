"""
Assignment for 2022T2 COMP3331
Python 3
Usage: python3 client.py SERVER_IP SERVER_PORT CLIENT_UDP_SERVER_PORT
coding: utf-8

Author: Zheng Luo (z5206267)
"""

from re import L
from socket import *
import sys, time, threading, os

commandPrompting = "\
The following commands are available:\n\
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
UDPServerPort = int(sys.argv[3])
serverAddress = (serverHost, serverPort)
UDPServerAddress = (serverHost, UDPServerPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)
# build connection with the server and send message to it
clientSocket.connect(serverAddress)

serverSocketUDP = socket(AF_INET, SOCK_DGRAM)
serverSocketUDP.bind(UDPServerAddress)

# TODO: Re-logging bug

def TCPConnection():
    '''
    Communicating with server with TCP
    '''
    # User authentication section.
    while True:
        # Requesting username as input:
        username = input("Enter your username: ").strip()
        # Dealing with potential edge cases:
        if username == "":
            continue
        usernameMsg = f"login username {username}"
        clientSocket.sendall(usernameMsg.encode())

        # Receive response from the server
        data = clientSocket.recv(2048)
        usernameResponse = data.decode()

        # Username has been found in the database, 
        # checking the password correctness.
        while usernameResponse == "usernameTrue":
            password = input("Enter your password: ").strip()
            if password == "":
                continue
            authMsg = f"login auth {username} {password}"
            clientSocket.sendall(authMsg.encode())
            data = clientSocket.recv(2048)
            passwordResponse = data.decode()
            if passwordResponse == "authTrue":
                print("Login in successfully! Welcome!")
                portInfoMsg = f"login port {username} {UDPServerPort}"
                clientSocket.sendall(portInfoMsg.encode())
                break
            elif passwordResponse == "authFalse":
                print("Password incorrect, please try again.")
            else:
                print("Password incorrect, and your account has been blocked due to too many attempts. \nPlease try again after 10 seconds.")
                time.sleep(10)
        # There is no such username.
        if usernameResponse == "usernameFalse":
            print("There is no such username, please try again.")
        else:
            break

    # User command and operation section.
    while True:
        # Section for entering the command.
        while True:
            inputmsg = input(commandPrompting)
            if inputmsg == "":
                print("Please enter valid command!\n")
                time.sleep(1)
                continue
            inputList = inputmsg.split()
            command = inputList[0]
            if command in acceptedCommand:
                if command == "BCM" and len(inputList) < 2:
                    print("Error usage, there should be 1 argument for this command, \nSample Usage: BCM message\n")
                elif command == "ATU" and not len(inputList) == 1:
                    print("Error usage, there should be no argument for this command, \nSample usage: ATU\n")
                elif command == "SRB" and len(inputList) < 2:
                    print("Error usage, there should be at least 1 argument for this command, \nSample usage: SRB username1 username2 ...\n")
                elif command == "SRM" and len(inputList) < 3:
                    print("Error usage, there should be 2 arguments for this command, \nSample usage: SRM roomID message\n")
                elif command == "RDM" and not len(inputList) == 3:
                    print("Error usage, there should be 2 arguments for this command, \nSample usage: RDM messageType(b or s) timestamp(1 Jun 2022 16:00:00)\n")
                elif command == "OUT" and not len(inputList) == 1:
                    print("Error usage, there should be no argument for this command, \nSample usage: OUT\n")
                elif command == "UPD" and not len(inputList) == 3:
                    print("Error usage, there should be 2 arguments for this command, \nSample usage: UPD username filename\n")
                else:
                    break
            else:    
                print(f"ERROR: Command {command} is not recognised, please try again!\n")
            time.sleep(1)
        if command == "BCM":
            inputmsg = ""
            for i in range(1, len(inputList)):
                inputmsg += inputList[i] + ' '
            clientSocket.sendall(f"BCM {username} {inputmsg}".encode())
            BCMmsgResponse = clientSocket.recv(2048).decode()
            print(f"BCM msg has been received at server: {BCMmsgResponse}")
        elif command == "ATU":
            clientSocket.sendall("ATU".encode())
            ATUResponse = clientSocket.recv(2048).decode()
            print(ATUResponse)
        elif command == "SRB" or command == "SRM" or command == "RDM":
            clientSocket.sendall(inputmsg.encode())
            data = clientSocket.recv(2048)
            print(data.decode())
        elif command == "OUT":
            print("Goodbye! See you next time!")
            clientSocket.sendall(inputmsg.encode())
            break
        elif command == "UPD":
            clientSocket.sendall(inputmsg.encode())
            data = clientSocket.recv(2048).decode()
            # The recipent is existed and actived, ready to send!
            if data.startswith("UPD"):
                inputFile = inputList[2]
                # Check whether given file exist in the current directory.
                if not os.path.exists(inputFile):
                    print("Input file is not existed in the current directory!")
                    continue
                # Starting UDP connection with audience.
                audienceAddress = data.split()[1]
                audienceUDPPort = int(data.split()[2])
                rawFile = open(inputFile, "rb")
                # fileSize = os.path.getsize(file)
                # Split large file into multiple small files for transmission.
                eachFile = rawFile.read(2048)
                while eachFile:
                    serverSocketUDP.sendto(eachFile, (audienceAddress, audienceUDPPort))
                    eachFile = rawFile.read(2048)
                rawFile.close()
            else:
                print(data)

    # close the socket
    clientSocket.close()

def UDPConnection():
    '''
    Communicating with other client(P2P) using UDP connection.
    '''
    while True:
        data = serverSocketUDP.recv(2048)
        receivedFile = open("sample.mp4", "wb")
        try:
            while data:
                receivedFile.write(data)
                serverSocketUDP.settimeout(2)
                data = serverSocketUDP.recv(2048)
        except timeout:
            print("Download finished.")
            receivedFile.close()
            serverSocketUDP.settimeout(None)




if __name__ == "__main__":
    UDP = threading.Thread(target=UDPConnection)
    TCP = threading.Thread(target=TCPConnection)
        
    UDP.start()
    TCP.start()
