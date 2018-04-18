#! /usr/bin/python

import socket

target_host = "127.0.0.1"
target_port = 80
message = "Rat!".encode()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))
client.send(message)
response = client.recv(4096)
print (response.decode())
