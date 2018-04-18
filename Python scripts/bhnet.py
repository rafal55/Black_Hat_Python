#! /usr/bin/python

import sys
import socket
import getopt
import threading
import time
import subprocess

#global variables
listen = False
command = False
upload = False
execute = ""
target = "192.168.0.109"
upload_destination = ""
port = 9999

def usage():
    print ("Narzedzie BHP Net")
    print("Spodob uzycia: bhpnet.py -t target_host -p port")
    print("-l --linsten                   -nasluchiwanie na [host]:[port] polaczen przychodzacych")
    print("-e --execute=file to return    -wykonuje dany plik, gdy odbierze polaczenie")
    print("-c --command                   -inicjuje wiersz polecen")
    print("-u --upload=destination        -gdy obierze polaczenie, wysyla plik i go zapisuje w [destination]")
    print("Przeyklady:")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")

def run_command(command):
    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = ("Nie udalo sie wykonac polecenia.\r\n").encode()
    return output  

def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.settimeout(None)
    server.listen(1)
    print("[*] Nasluchiwanie na porcie %s:%d" % (target, port))

    while True:
        client_socket, addr = server.accept()
        print("[*] Przyjeto polaczenie od: %s:%d" % (addr[0],addr[1]))

        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def client_handler(client_socket):
    global upload
    global execute
    global command

    request = client_socket.recv(1024)
    print ("[*] Odebrano: %s" % request.decode())

    if len(upload_destination):
        file_buffer = ""

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("Zapisano plik w %s\r\n" % upload_destination)
        except:
            client_socket.send("Nie udalo sie zapidac pliku w %s\r\n" % upload_destination)

    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send("<BHP:#> ".encode())

            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += str(client_socket.recv(4096).decode())
            response = run_command(cmd_buffer)
            client_socket.send(response)

def client_sender(buffer):

    print("starting client")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer.encode())
        while True:
            recv_len = 1
            response = ""

            while recv_len:
                print("receiving data from server...\n")
                time.sleep(0.5)
                data = client.recv(4096).decode("utf-8", "ignore")
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            print (response, end ='')
            buffer = input()
            buffer += "\n"

            client.send(buffer.encode())
    except:
        print("[*] Wyjatek! Zamykanie.")
        client.close() 

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()
    
    try:
        opts,args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    
    for o,a in opts:
            if o in ("-h","--help"):
                usage()
            elif o in ("-l","--listen"):
                listen = True
            elif o in ("-e","--execute"):
                execute = a
            elif o in ("-c","--command"):
                command = True
            elif o in ("-u","--upload"):
                upload_destination = a
            elif o in ("-t","--target"):
                target = a
            elif o in ("-p","--port"):
                port = int(a)
            else:
                assert False,"Nieobslugiwana opcja"
    if not listen and len(target) and port > 0:
        #buffer = sys.stdin.read()
        buffer = "Starting"
        client_sender(buffer)

    if listen:
        print("Starting server")
        server_loop()

main()

