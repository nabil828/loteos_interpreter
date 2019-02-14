__author__ = 'Owner'

import Colors
import time


def print_(string, node_id=""):
    print Colors.Colors.OKGREEN + "$Wire$[node_id:" + str(node_id) + "]" + "[" + str(time.strftime("%M %S")) + "]" + string + Colors.Colors.ENDC
