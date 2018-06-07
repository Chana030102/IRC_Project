# pychat_client.py
#
#
#
import select, socket, sys
from pychat_def import Lobby, Room, Client
import pychat_def

READ_BUFFER = 4096

if len(sys.argv) < 2:
    print("Usage: python3 pychat_client.py [hostname]", file = sys.stderr)
    sys.exit(1)

else: 
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection.connect((sys.argv[1], pychat_def.PORT))
print("Connected to the server\n")
msg_prefix = ''

def prompt():
    print('>: ',end='', flush = True)

socket_list = [sys.stdin, server_connection]

while True:
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    for s in read_sockets:
        if s is server_connection: # message from server
            msg = s.recv(READ_BUFFER)
            if not msg:
                print("Server down\n")
                sys.exit(2)
            else:
                if msg == pychat_def.TERMINATE.encode():
                    sys.stdout.write('Good Bye\n')
                    sys.exit(2)
                else:
                    sys.stdout.write(msg.decode())
                    if 'Type your name:' in msg.decode():
                        msg_prefix = ">>name "
                    else:
                        msg_prefix = ''
                    prompt()

        else:
            msg = msg_prefix + sys.stdin.readline()
            server_connection.sendall(msg.encode())

