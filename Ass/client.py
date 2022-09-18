"""
Assignment for 2022T2 COMP3331
Python 3
Usage: python3 client.py SERVER_IP SERVER_PORT CLIENT_UDP_SERVER_PORT
coding: utf-8

Author: Zheng Luo (z5206267)
"""

from socket import *
import sys, time, threading, os, math, datetime

# Constant declaration section
COMMAND_PROMPTING = "\
The following commands are available:\n\
BCM: Public messages, usage: BCM message\n\
ATU: Display active users, usage: ATU\n\
SRB: Separate room building, usage: SRB username1 username2 ...\n\
SRM: Separate room message, usage: SRM roomID message\n\
RDM: Read messages, usage: RDM messageType(b or s) timestamp(1 Jun 2022 16:00:00)\n\
OUT: Log out, usage: OUT\n\
UPD: Upload file, usage: UPD username filename\n\
Please enter the command as suggested by usage:\n"
ACCEPTED_COMMAND = ["BCM", "ATU", "SRB", "SRM", "RDM", "OUT", "UPD"]
PACKET_SIZE = 2048

# Input argument checking section
# Server would be running on the same host as Client
if len(sys.argv) != 4:
    print("\n===== Error usage, python3 client.py SERVER_IP SERVER_PORT CLIENT_UDP_SERVER_PORT======\n")
    exit(0)
serverHost = sys.argv[1]
if not (sys.argv[2]).isdigit() or int(sys.argv[2]) < 0 or int(sys.argv[2]) > 65535:
    print("\n===== Error usage, server port valid range is between 0 and 65536======\n")
    exit(0)
serverPort = int(sys.argv[2])
if not (sys.argv[3]).isdigit() or int(sys.argv[3]) < 0 or int(sys.argv[3]) > 65535:
    print("\n===== Error usage, UDP server port valid range is between 0 and 65536======\n")
    exit(0)
UDPServerPort = int(sys.argv[3])
serverAddress = (serverHost, serverPort)
UDPServerAddress = (serverHost, UDPServerPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)
# build connection with the server and send message to it
clientSocket.connect(serverAddress)

serverSocketUDP = socket(AF_INET, SOCK_DGRAM)
serverSocketUDP.bind(UDPServerAddress)


def TCPConnection():
    '''
    Communicating with server with TCP
    '''
    # User authentication section.
    # Return the current user's username if log in successfully.
    username = userAuthenticationSection()
    # User command and operation section.
    while True:
        # Section for pre checking the command.
        # Return the input string if input is valid.
        inputmsg = commandPreChecking()
        inputList = inputmsg.split()
        command = inputList[0]
        # Operating section for entering the commmand.
        if command == "BCM":
            BCMInputmsg = ""
            for i in range(1, len(inputList)):
                BCMInputmsg += inputList[i] + ' '
            clientSocket.sendall(f"BCM {username} {BCMInputmsg}".encode())
            BCMmsgResponse = clientSocket.recv(PACKET_SIZE).decode()
            print(f"BCM msg has been received at server: {BCMmsgResponse}")
        elif command == "ATU" or command == "SRB" or command == "SRM" or command == "RDM":
            clientSocket.sendall(inputmsg.encode())
            print(clientSocket.recv(PACKET_SIZE).decode())
        elif command == "OUT":
            print("Goodbye! See you next time!")
            clientSocket.sendall(inputmsg.encode())
            break
        elif command == "UPD":
            # Sending UPD file to another peer.
            UPDFileSending(inputmsg, inputList, username)
    # close the socket
    clientSocket.close()
    # Exit the whole program.
    os._exit(os.EX_OK)

def UDPConnection():
    '''
    Communicating with other client(P2P) using UDP connection.
    '''
    while True:
        data = serverSocketUDP.recv(PACKET_SIZE).decode()
        if data.split()[0] == "UPD":
            username = data.split()[1]
            fileName = data.split()[2]
            fileSize = int(data.split()[3])
            totalPacketSize = math.ceil(fileSize/PACKET_SIZE)
            receivedFileName = f"{username}_{fileName}"
            print(f"Receiving file {fileName} {fileSize}bytes {totalPacketSize} packets in total from {username}")
            receivedFile = open(receivedFileName, "wb")
            try:
                dataCounter = 1
                data = serverSocketUDP.recv(PACKET_SIZE)
                while data:
                    print(f"Receiving data packets {dataCounter}/{totalPacketSize}")
                    dataCounter += 1
                    receivedFile.write(data)
                    serverSocketUDP.settimeout(1)
                    data = serverSocketUDP.recv(PACKET_SIZE)
            except timeout:
                print("Download finished.")
                print(COMMAND_PROMPTING)
                receivedFile.close()
                serverSocketUDP.settimeout(None)

def userAuthenticationSection():
    '''
    userAuthenticationSection will prompt users to enter their username and password,
    until they have been log in successfully.
    '''
    while True:
        # Assuming there is no empty line in credential.txt.
        # Assuming there is no repeated username.
        # Requesting username as input:
        username = input("Enter your username: ").strip()
        # Dealing with potential edge cases:
        if username == "":
            continue
        usernameMsg = f"login username {username}"
        clientSocket.sendall(usernameMsg.encode())

        # Receive response from the server
        data = clientSocket.recv(PACKET_SIZE)
        usernameResponse = data.decode()

        # Username has been found in the database, 
        # checking the password correctness.
        while usernameResponse == "usernameTrue":
            password = input("Enter your password: ").strip()
            if password == "":
                continue
            authMsg = f"login auth {username} {password}"
            clientSocket.sendall(authMsg.encode())
            data = clientSocket.recv(PACKET_SIZE)
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
    return username

def commandPreChecking():
    '''
    commandPreChecking function prechecks the user input.
    '''
    while True:
        inputmsg = input(COMMAND_PROMPTING)
        if inputmsg == "":
            print("Please enter valid command!\n")
            time.sleep(1)
            continue
        inputList = inputmsg.split()
        command = inputList[0]
        if command in ACCEPTED_COMMAND:
            if command == "BCM" and len(inputList) < 2:
                print("Error usage, there should be 1 argument for this command, \nSample Usage: BCM message\n")
            elif command == "ATU" and not len(inputList) == 1:
                print("Error usage, there should be no argument for this command, \nSample usage: ATU\n")
            elif command == "SRB" and len(inputList) < 2:
                print("Error usage, there should be at least 1 argument for this command, \nSample usage: SRB username1 username2 ...\n")
            elif command == "SRM" and (len(inputList) < 3 or not inputList[1].isdigit()):
                print("Error usage, there should be 2 arguments for this command, \nSample usage: SRM roomID message\n")
            elif command == "RDM" and (not len(inputList) == 6 or not (inputList[1] == "b" or inputList[1] == "s")):
                # Check given time string format:
                inputTime = f"{inputList[2]} {inputList[3]} {inputList[4]} {inputList[5]}"
                try:
                    datetime.datetime.strptime(inputTime, '%d %b %Y %H:%M:%S')
                except ValueError:
                    raise ValueError("Incorrect data format, should be %d %b %Y %H:%M:%S")
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
    return inputmsg

def UPDFileSending(inputmsg, inputList, username):
    '''
    UPDFileSending section perform the operation for sending UPD file to other users.
    '''
    clientSocket.sendall(inputmsg.encode())
    data = clientSocket.recv(PACKET_SIZE).decode()
    # The recipent is existed and actived, ready to send!
    if data.startswith("UPD"):
        inputFile = inputList[2]
        inputFileSize = os.path.getsize(inputFile)
        # Check whether given file exist in the current directory.
        if not os.path.exists(inputFile):
            print("Input file is not existed in the current directory!")
            return
        # Starting UDP connection with audience.
        audienceAddress = data.split()[1]
        audienceUDPPort = int(data.split()[2])
        # Inform the audience to receive files.
        informMsg = f"UPD {username} {inputFile} {inputFileSize}"
        serverSocketUDP.sendto(informMsg.encode(), (audienceAddress, audienceUDPPort))

        # Split large file into multiple small files for transmission.
        rawFile = open(inputFile, "rb")
        eachFile = rawFile.read(PACKET_SIZE)
        fileCounter = 1
        while eachFile:
            print(f"Sending the file#{fileCounter} with size of {len(eachFile)}")
            # Sending the UDP packages too fast will result the packages cannnot all be received,
            # Hence a small gap of wait time is implemented.
            time.sleep(0.0001)
            fileCounter += 1
            serverSocketUDP.sendto(eachFile, (audienceAddress, audienceUDPPort))
            eachFile = rawFile.read(PACKET_SIZE)
        rawFile.close()
    else:
        print(data)


if __name__ == "__main__":
    UDP = threading.Thread(target=UDPConnection)
    TCP = threading.Thread(target=TCPConnection)
        
    UDP.start()
    TCP.start()

    
    