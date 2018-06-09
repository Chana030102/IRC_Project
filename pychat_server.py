# pychat_server.py
#
#
#

import select, socket, sys, pdb
import pychat_util, pychat_lobby
from pychat_util import Room, Client
from pychat_lobby import Lobby

READ_BUFFER = 4096
listen_sock = pychat_util.create_socket((socket.gethostname(),pychat_util.PORT))

lobby = Lobby()
connection_list = []
connection_list.append(listen_sock)

while True:
    read_clients, write_clients, error_sockets = select.select(connection_list,[],[])
    for client in read_clients:
        if client is listen_sock: # new client as connected
            new_socket, add = client.accept()
            new_client = Client(new_socket)
            connection_list.append(new_client)
            lobby.greet_new(new_client)
            lobby.add_client(new_client)
#            lobby.clients_list.append(new_client)

        else: # new message from a client
            msg = client.socket.recv(READ_BUFFER)
            if msg:
                msg = msg.decode().lower()
                lobby.handle_msg(client, msg)
            else:
                client.socket.close()
                lobby.client_disconnect(client)
                connection_list.remove(client)

    for sock in error_sockets: # close error sockets
        sock.close()
        connection_list.remove(sock)
    
