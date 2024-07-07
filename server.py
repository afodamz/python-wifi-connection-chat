import socket
import select
import argparse
from colorama import Fore, init, Back, Style, init
import sys
import signal

init()
parser = argparse.ArgumentParser(description="A simple CLI chat app with arguments")
HEADER_LENGTH = 10

parser.add_argument("--port", type=int, help="Input port name")
parser.add_argument("--ip", type=str, help="Input ip name")

# Parse the command-line arguments
args = parser.parse_args()

IP = args.ip if args.ip else "127.0.0.1"
PORT = args.port if args.port else 4040

clients = {}

def signal_handle(sig, frame):
    global server_running
    print("***"*5, Fore.YELLOW + "SHUTTING DOWN SERVER" + Fore.WHITE, "***"*5)
    server_running = False
    
    # To send message for clients to the server
    for client_socket in clients:
        try:
            client_socket.sendall(b"SERVER_SHUTDOWN")
            client_socket.close()
        except Exception as e:
            print(f"Error sending shutdown message to client: {e}")
                            
    server_socket.close()
    sys.exit

signal.signal(signal.SIGINT, signal_handle)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]
clients_username = []


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False

server_running = True

try:
    print("***"*5, Fore.GREEN + "STARTING SERVER" + Fore.WHITE, "***"*5)
    while server_running:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, clientaddress = server_socket.accept()
                user = receive_message(client_socket)

                print('clients_username', clients_username)
                username = user['data'].decode('utf-8')
                if username not in clients_username:
                    if user is False:
                        continue

                    sockets_list.append(client_socket)
                    clients_username.append(username)

                    clients[client_socket] = user

                    print("Accepted new connection from {}:{} username: {}".format(Fore.BLUE + clientaddress[0] + Fore.WHITE, Fore.MAGENTA + str(clientaddress[1]) + Fore.WHITE,  Fore.GREEN + user['data'].decode('utf-8') + Fore.WHITE), Style.RESET_ALL)
                else:
                    rejection_message = "Your username is already taken. Connection closed."
                    client_socket.send(rejection_message.encode("utf-8"))
                    client_socket.close()

            else:
                message = receive_message(notified_socket)
                if message is False:
                    userData = clients[notified_socket]['data'].decode('utf-8')
                    print("closed connection from {}".format(userData))
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    clients_username = [x for x in clients_username if x != userData]
                    rejection_message = f"{userData} has disconnected."
                    # client_socket.send(rejection_message.encode("utf-8"))
                    # if value_to_delete in clients_username:
                    #     my_list.remove(userData)
                    continue

                else:
                    user = clients[notified_socket]
                    # print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

                    # share message with everyone
                    for client_socket in clients:
                        if client_socket != notified_socket:
                            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]
except socket.error as e:
    print(f"Socket error: {e}")




