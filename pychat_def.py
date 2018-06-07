# pychat_def.py
# 
# Aaron Chan
# CS494 (Spring 2018)
# 
#
import socket

PORT = 5000

def create_socket(address)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    s.bind(address)
    s.listen(MAX)
    print("Chat server started --> (host,port) = "+str(address))
    return s

class Lobby:
    def __init__(self):
        self.rooms = {} # {room_name: Room}
        self.clients = [] # list of client sockets

    def greet_new(self, client):
        client.socket.sendall(b'Welcome to the chat server.\nType your name:')

    def broadcast(self, source_client, msg):
        msg = source_client.name.encode() + b": " + msg
        for client in self.clients:
            client.socket.sendall(msg.encode())

    def list_rooms(self, client):
        if len(self.rooms) == 0:
            msg = 'There are no other rooms. Create one using ''/join room_name\n'
            client.socket.sendall(msg.encode())
        else:
            msg = 'Active rooms...\n'
            for room in self.rooms:
                msg += room + ": " + str(len(self.rooms[room].client)) + "user(s)\n"
            client.socket.sendall(msg.encode())

    def handle_msg(self, client, msg):
        
        if "/nick" in msg: # new client/user
            name = msg.splt()[1]
            client.name = name

        elif "/join" in msg: # create or join existing room
            if len(msg.split()) >= 2: #error check
                room_name = msg.split()[1]
                if (room_name in self.rooms) and (room_name in client.active_rooms)
                    client.socket.sendall(b'You are already in this room.\n')
                elif (room_name in self.rooms)
                    client.active_rooms.append(room_name)
                    self.rooms[self.rooms.index(room_name)].client_list.append(client)

                else: # room does not exist
                    new_room = Room(room_name)
                    self.rooms[room_name] = new_room
                    self.rooms[self.rooms.index(room_name)].client_list.append(client)
                    self.rooms[self.rooms.index(room_name)].greet_new(client)
                    client.active_rooms.append(room_name)

        elif "/quit" in msg:
            for room in client.active_rooms:
                self.rooms[self.rooms.index(room)].remove_client(client)
            self.clients.remove(client)


                    

# Acts as subscription list. Easy broadcast to anyone in the same room                    
class Room:
    def __init__(self, name):
        self.name = name
        self.client_list = []
        self.prefix = b"[" + name.encode() + b"] "

    def greet_new(self, source_client):
        msg = self.prefix.encode() + source_client.name.encode() + b" has joined the room\n"
        for client in client_list:
            client.socket.sendall(msg)

    def broadcast(self, source_client, msg):
        msg = self.prefix.encode() + b"<" + source_client.name.encode() + b"> : " + msg
        for client in client_list:
            client.socket.sendall(msg)

    def remove_client(self, source_client):
        self.client_list.remove(source_client)
        msg = self.prefix.encode() + source_client.name.encode() + b" has left the room\n"
        for client in client_list:
            client.socket.sendall(msg)


# Keep track of rooms client is in and their name
class Client:
    def __init__(self,socket,name):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.active_rooms = []
