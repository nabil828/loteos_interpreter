__author__ = 'Owner'

# code for each mode
local = 100
planetLab = 200
testing = 300
client_server = 400  # for the thin_server


def print_mode(x):
    # print ">>>>>"  + str(x)
    if x == local:
        return "local"
    elif x == planetLab:
        return "planetLab"
    elif x == testing:
        return "testing"
    elif x == client_server :
        return "client_server "
    else:
        return "Something wrong happened!!!!!!!!!!!!"
