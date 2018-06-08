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
        self.clients_list = [] # list of client sockets
        self.prefix = b'[ Lobby ] '

    def greet_new(self, client):
        client.socket.sendall(self.prefix + b': Welcome to the chat server.\nType your name:')

    def client_disconnect(self, source_client):
        msg = self.prefix + source_client.name + b' disconnected from the server\n'
        print(msg.decode())
        for client in self.clients_list:
            if not source_client:
                client.socket.sendall(msg)
        self.client_cleanup(source_client)
    
    def client_cleanup(self, source_client):
        if len(source_client.active_rooms) != 0:
            for room in source_client.active_rooms:
                self.rooms[room].remove_client(source_client)
        self.clients_list.remove(source_client)
        

    def list_rooms(self, client):
        if len(self.rooms) == 0:
            msg = self.prefix + b': There are no other rooms. Create one using /join [room_name]\n'
            client.socket.sendall(msg)
        else:
            msg = 'Active rooms...\n'
            for room in self.rooms:
                msg += self.rooms[room].name + ": " + str(len(self.rooms[room].client_list)) + " user(s)\n"
            client.socket.sendall(msg.encode())

    def delete_room(self, target_room):
        to_modify = dict(self.rooms)
        del to_modify[target_room]
        return to_modify

    def handle_msg(self, source_client, msg):
        parse = msg.split() # [ command, argument1, msg ]
        if(len(parse) == 0): return -1
        print(source_client.name.decode() + ": " + msg, end='') 
        if ">>name" == parse[0]: # initial name set
            print(source_client.name.decode() + " is now " + parse[1])
            source_client.set_name(parse[1])
            source_client.socket.sendall(self.prefix + b': For chat commands, use /help\n')
            msg = self.prefix + source_client.name + b' has joined the server!\n'
            for client in self.clients_list:
                if not source_client:
                    client.socket.sendall(msg)

#        elif "/nick" == parse[0]: # new name for themself
#            source_client.set_name(

        elif "/rooms" == parse[0]: # list rooms available
            self.list_rooms(source_client)
        
        elif "/online" == parse[0]: # list online users in a room
            if len(parse) >= 2: 
                room_name = parse[1]
                if(room_name in self.rooms):
                    self.rooms[room_name].list_clients(source_client)
                else:
                    source_client.socket.sendall(self.prefix + b'That room doesn\'t exist\n')
            else: # list online users of lobby (which is the default server)
                msg = self.prefix + b'Online users: '
                for client in self.clients_list:
                    msg += client.name + b', '
                source_client.socket.sendall(msg + b'\n')


        elif "/join" == parse[0]: # create or join existing room
            if len(parse) >= 2: #error check
                room_name = parse[1]
                if (room_name in self.rooms) and (room_name in source_client.active_rooms):
                    source_client.socket.sendall(self.prefix + b': You are already in this room.\n')
                elif (room_name in self.rooms):
                    self.rooms[room_name].client_list.append(source_client)
                    self.rooms[room_name].greet_new(source_client)
                    source_client.active_rooms.append(room_name)

                else: # room does not exist. Create it
                    new_room = Room(room_name)
                    self.rooms[room_name] = new_room
                    self.rooms[room_name].client_list.append(source_client)
                    self.rooms[room_name].greet_new(source_client)
                    source_client.active_rooms.append(room_name)
            
            else: # no room name provided
                source_client.socket.sendall(self.prefix + b': No room name provided\n')
        
        elif "/leave" == parse[0]: # leave a room
            if len(parse) >= 2: # error check
                    room_name = parse[1]
                    if (room_name in self.rooms) and (room_name in source_client.active_rooms):
                        self.rooms[room_name].client_leave(source_client)
                        if len(self.rooms[room_name].client_list) == 0:
                            self.rooms = self.delete_room(room_name)                            
                        source_client.active_rooms.remove(room_name)
                        msg = self.prefix + b': You have left ' + room_name.encode() + b'\n'
                    elif not (room_name in self.rooms): # room doesn't exist
                        msg = self.prefix + b': That room does not exist.\n'
                    else: # client never joined the room
                        msg = self.prefix + b': You can\'t leave a room you never joined!\n'
            
            else: msg = self.prefix + b': You need to specify a room. --> /leave [room_name]\n'

            source_client.socket.sendall(msg)
        
        elif '/msg' == parse[0]: # send message to a specific room
            if len(parse)>=2:
                target = parse[1]
                if not target in self.rooms:
                    source_client.socket.sendall(self.prefix + b': That room doesn\'t exist\n')
                elif not target in source_client.active_rooms:
                    source_client.socket.sendall(self.prefix + b': You aren\'t in that room\n')
                else:
                    self.rooms[target].broadcast(source_client, msg.split(' ',2)[2])

        elif '/w' == parse[0]: # whisper/private message to another client
            if len(parse) >= 2: 
                target = parse[1]
                if target.encode() == source_client.name:
                    msg = self.prefix + b': You can\'t private message yourself\n'
                    source_client.socket.sendall(msg)
                elif target in self.clients_list:
                    msg = source_client.prefix + msg.split(' ',2)[2]
                    self.clients[target].socket.sendall(msg)
                else: # target doesn't exist
                    source_client.socket.sendall(self.prefix + b': ' + target.encode() + b' is not online\n')
            else: # no intended client provided
                msg = self.prefix + b': No target user provided --> /w [username] [message]\n'
                source_client.socket.sendall(msg)

        elif '/quit' == parse[0]: # client leaving the server
            source_client.socket.sendall(TERMINATE.encode())
            msg = self.prefix + b': ' + source_client.name + b' has left the server\n'
            for client in self.clients_list:
                if not source_client:
                    client.socket.sendall(msg)

        else: # broadcast message to lobby
            msg = self.prefix + source_client.prefix + msg.encode()
            for client in self.clients_list:
                if not source_client:
                    client.socket.sendall(msg)

# Acts as subscription list. Easy broadcast to anyone in the same room                    
class Room:
    def __init__(self, name):
        self.name = name
        self.client_list = []
        self.prefix = b'[ ' + name.encode() + b' ] '

    def greet_new(self, source_client):
        msg = self.prefix + b': ' + source_client.name + b' has joined the room\n'
        for client in self.client_list:
            client.socket.sendall(msg)

    def broadcast(self, source_client, msg):
        msg = self.prefix + source_client.prefix + msg.encode()
        for client in self.client_list:
            if not source_client:
                client.socket.sendall(msg)

    def list_clients(self, source_client):
        if len(self.client_list) > 0:
            msg = b'Online users: '
            for client in self.client_list:
                msg += client.name.encode() + b', '
        else:
            msg = b'No users in this room.'
        source_client.socket.sendall(self.prefix + msg + b'\n') 

    def client_leave(self, source_client):
        self.client_list.remove(source_client)
        msg = self.prefix + b': ' + source_client.name + b' has left the room\n'
        for client in self.client_list:
            client.socket.sendall(msg)

    def remove_client(self, source_client):
        self.client_list.remove(source_client)


# Keep track of rooms client is in and their name
class Client:
    def __init__(self,socket):
        socket.setblocking(0)
        self.socket = socket
        self.name = b'new'
        self.active_rooms = []
        self.prefix = b'<' + self.name + b'>: '
    
    def set_name(self,name):
        self.name = name.encode()
        self.prefix = b'<' + name.encode() + b'>: '
    
    def fileno(self):
        return self.socket.fileno()


