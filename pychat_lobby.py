# pychat_lobby.py
#
# Aaron Chan
# CS494 (Spring 2018)
#
# 
import socket, pychat_util
from pychat_util import Room, Client

class Lobby:
    def __init__(self):
        self.rooms = {} # {room_name: Room}
        self.clients_list = [] # list of client sockets
        self.prefix = b'[ Lobby ] '

    def greet_new(self, client):
        client.socket.sendall(self.prefix + b': Welcome to the chat server.\nType your name:')
    
    def add_client(self, client):
        new_client = Client(client.socket)
        self.clients_list.append(new_client)

    def client_disconnect(self, source_client):
        msg = self.prefix + source_client.name + b' disconnected from the server\n'
        print(msg.decode(), end='')
        for client in self.clients_list:
            if not source_client:
                client.socket.sendall(msg)
        self.client_cleanup(source_client)
    
    def client_cleanup(self, source_client):
        if len(source_client.active_rooms) != 0:
            for room in source_client.active_rooms:
                self.rooms[room].remove_client(source_client)
        self.clients_list.remove(source_client)
    
    def broadcast(self, source_client, msg):
        for i in range(0,len(self.clients_list)):
            if not self.clients_list[i] == source_client:
                self.clients_list[i].socket.send(msg.encode())
        

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
        if(len(parse) == 0): return 
        
        print(source_client.name.decode() + ": " + msg, end='') 
        if ">>name" == parse[0]: # initial name set
            print(source_client.name.decode() + " is now " + parse[1])
            source_client.set_name(parse[1])
            source_client.socket.sendall(self.prefix + b': For chat commands, use /help\n')
            msg = self.prefix + source_client.name + b' has joined the server!\n'
            self.broadcast(source_client,msg)

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
                    self.rooms[target].broadcast(source_client, msg)

        elif '/w' == parse[0]: # whisper/private message to another client
            if len(parse) >= 2: 
                target = parse[1]
                if target.encode() == source_client.name:
                    msg = self.prefix + b': You can\'t private message yourself\n'
                    source_client.socket.sendall(msg)
                else:
                    for client in self.clients_list:
                        if target.encode() == client.name:
                            msg = source_client.prefix + msg.split(' ',2)[2].encode()
                            client.socket.sendall(msg)
                        else: # target doesn't exist
                            source_client.socket.sendall(self.prefix + b': ' + target.encode() + b' is not online\n')
            else: # no intended client provided
                msg = self.prefix + b': No target user provided --> /w [username] [message]\n'
                source_client.socket.sendall(msg)

        elif '/quit' == parse[0]: # client leaving the server
            msg = self.prefix + b': ' + source_client.name + b' has left the server\n'
            self.broadcast(source_client,msg)
#            for client in self.clients_list:
#                if not source_client:
#                    client.send_msg(msg)
            source_client.socket.sendall(pychat_util.TERMINATE.encode())

        else: # broadcast message to lobby
            self.broadcast(source_client,msg)
#            for i in range(0,len(self.clients_list)):
#                if not self.clients_list[i] == source_client:
#                    self.clients_list[i].socket.send(msg.encode())
