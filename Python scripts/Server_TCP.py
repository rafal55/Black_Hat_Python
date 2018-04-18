#! /usr/bin/python
import socket
import threading
import sys

def handle_client(client_socket):

    request = client_socket.recv(1024)
    print ("[*] Odebrano: %s" % request.decode())
    client_socket.send("ACK!".encode())
    client_socket.close()

def main():    
    bind_ip = "127.0.0.1"
    bind_port = 80

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.settimeout(10)
    server.listen(1)
    print("[*] Nasluchiwanie na porcie %s:%d" % (bind_ip,bind_port))

    while True:
        try:
            client,addr = server.accept()
        except:
            server.close()
            restart = input("Server stopped. Restart server (y/n)?")
            if restart == "n": sys.exit(1)
            else: main()

        print("[*] Przyjeto polaczenie od: %s:%d" % (addr[0],addr[1]))
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

main()