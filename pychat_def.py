# pychat_def.py
# 
# Aaron Chan
# CS494 (Spring 2018)
# 
#
import socket

PORT = 5000
MAX  = 30
TERMINATE = '<$terminate$>'

def create_socket(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(address)
    sock.listen(MAX)
    print("Chat server started --> (host,port) = "+str(address))
    return sock


class Lobby:
    def __init__(self):
        self.rooms = {} # {room_name: Room}
        self.clients = [] # list of client sockets
        self.prefix = b'[ Lobby ] '

    def greet_new(self, client):
        client.socket.sendall(self.prefix + b': Welcome to the chat server.\nType your name:')

    def broadcast(self, source_client, msg):
        msg = self.prefix + source_client.name.encode() + b": " + msg
        for client in self.clients:
            client.socket.sendall(msg.encode())

    def list_rooms(self, client):
        if len(self.rooms) == 0:
            msg = self.prefix + ': There are no other rooms. Create one using ''/join [room_name]\n'
            client.socket.sendall(msg.encode())
        else:
            msg = 'Active rooms...\n'
            for room in self.rooms:
                msg += room + ": " + str(len(self.rooms[room].client)) + "user(s)\n"
            client.socket.sendall(msg.encode())

    def handle_msg(self, source_client, msg):
        
        print(source_client.name + ": " + msg) 
        if ">>name" in msg: # initial name set
            name = msg.split()[1]
            print(source_client.name + " is now " + name + "\n")
            source_client.name = name
            source_client.socket.sendall(self.prefix + b': For chat commands, use /help\n')

        elif "/nick" in msg: # new client/user
            name = msg.split()[1]
            source_client.name = name

        elif "/join" in msg: # create or join existing room
            if len(msg.split()) >= 2: #error check
                room_name = msg.split()[1]
                if (room_name in self.rooms) and (room_name in source_client.active_rooms):
                    source_client.socket.sendall(self.prefix + b': You are already in this room.\n')
                elif (room_name in self.rooms):
                    source_client.active_rooms.append(room_name)
                    self.rooms[room_name].client_list.append(source_client)

                else: # room does not exist
                    new_room = Room(room_name)
                    self.rooms[room_name] = new_room
                    self.rooms[room_name].client_list.append(source_client)
                    self.rooms[room_name].greet_new(source_client)
                    source_client.active_rooms.append(room_name)
            
            else: # no room name provided
                source_client.socket.sendall(self.prefix + b': No room name provided\n')

        elif "/quit" in msg: # client leaving the server
            source_client.socket.sendall(TERMINATE.encode())
            for client in self.clients:
                if not source_client:
                    client.socket.sendall(self.prefix + b': ' + source_client.name.encode() + b' has left the server\n') 
            if len(source_client.active_rooms) != 0:
                for room in source_client.active_rooms:
                    self.rooms[room].remove_client(source_client)
            self.clients.remove(source_client)

        else: # broadcast message to lobby
            msg = self.prefix + b'<' + source_client.name.encode() + b'>' + msg.encode()
            for client in self.clients:
                if not source_client:
                    client.socket.sendall(msg)


# Acts as subscription list. Easy broadcast to anyone in the same room                    
class Room:
    def __init__(self, name):
        self.name = name
        self.client_list = []
        self.prefix = b'[' + name.encode() + b'] '

    def greet_new(self, source_client):
        msg = self.prefix + b': ' + source_client.name.encode() + b' has joined the room\n'
        for client in self.client_list:
            client.socket.sendall(msg)

    def broadcast(self, source_client, msg):
        msg = self.prefix + b'<' + source_client.name.encode() + b'>: ' + msg
        for client in self.client_list:
            client.socket.sendall(msg)

    def client_leave(self, source_client):
        self.client_list.remove(source_client)
        msg = self.prefix + b': ' + source_client.name.encode() + b' has left the room\n'
        for client in self.client_list:
            client.socket.sendall(msg)

    def remove_client(self, source_client):
        self.client_list.remove(source_client)


# Keep track of rooms client is in and their name
class Client:
    def __init__(self,socket):
        socket.setblocking(0)
        self.socket = socket
        self.name = "new"
        self.active_rooms = []

    def fileno(self):
        return self.socket.fileno()
