__author__ = 'Owner'

# code for each mode
local = 100
planetLab = 200
testing = 300


def print_mode(x):
    # print ">>>>>"  + str(x)
    if x == local:
        return "local"
    elif x == planetLab:
        return "planetLab"
    elif x == testing:
        return "testing"
    else:
        return "Something wrong happened!!!!!!!!!!!!"
