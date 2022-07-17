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