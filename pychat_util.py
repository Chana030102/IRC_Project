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
#        msg = self.prefix + source_client.prefix + msg.encode()
        for client in self.client_list:
            if not source_client:
                client.socket.sendall(msg)
#                client.socket.sendall(b'something was written\n')

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
   
    def send_msg(self,msg):
        self.socket.sendall(msg)

    def fileno(self):
        return self.socket.fileno()


