import time
import sys
import socket
import subprocess


output = subprocess.check_output('dir', stderr=subprocess.STDOUT, shell=True)
print(output)