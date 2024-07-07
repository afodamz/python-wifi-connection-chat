import socket
import errno
import sys
import threading
from colorama import Fore, init, Back, Style, init
import argparse

init()
# errno is used to manage error code
parser = argparse.ArgumentParser(description="A simple CLI chat app with arguments")
HEADER_LENGTH = 10

parser.add_argument("--port", type=int, help="Input port name")
parser.add_argument("--ip", type=str, help="Input ip name")

# Parse the command-line arguments
args = parser.parse_args()

IP = args.ip if args.ip else "127.0.0.1"
PORT = args.port if args.port else 4040

my_username = ""
while True:
    my_username = input(Fore.YELLOW + "Please enter username: ")

    # Check if the input is not empty
    if my_username:
        print(f"{Fore.MAGENTA} You entered: {my_username}")
        break  # Exit the loop if valid input is provided
    else:
        print("Input cannot be empty. Please try again.")

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)  # The receive functionality wont be blocking
    username = my_username.encode("utf-8")
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
    client_socket.send(username_header + username)
except ConnectionRefusedError:
    print("The target machine actively refused the connection. Check the server and port.")
except Exception as e:
    print(f"An error occurred: {str(e)}")

message = ""


# Function to send messages
def send_message():
    while True:
        sys.stdout.write(f"{Fore.GREEN + my_username + Fore.WHITE} > ")
        sys.stdout.flush()
        message = input()

        if message:
            if message.lower() == 'exit':
                    print(Fore.RED + "SHUTTING DOWN" + Fore.WHITE)
                    sys.exit()
            message = message.encode('utf-8')
            message_header = f"{len(message): < {HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message)

def receive_message(client_socket):
    while True:
        try:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print(Fore.RED + "connection closed by server")
                sys.exit()
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            rcv_message = client_socket.recv(message_length).decode('utf-8')
            if rcv_message == b"SERVER_SHUTDOWN":
                print(Fore.RED + "Server is shutting down. Closing connection." + Fore.WHITE)
                client_socket.close()
                break
            
            sys.stdout.write("\r" + " " * len(f"{my_username} > "))
            sys.stdout.flush()
            print(f"\r{Fore.BLUE}{username}{Fore.WHITE} > {rcv_message}")
            sys.stdout.write(f"{Fore.GREEN + my_username + Fore.WHITE} > ")
            sys.stdout.flush()
        except IOError as IO:
            if IO.errno != errno.EAGAIN and IO.errno != errno.EWOULDBLOCK:
                print(Fore.RED + 'reading error', str(IO))
                client_socket.close()
                sys.exit()
            continue

        except Exception as e:
            print(Fore.RED + "general error", str(e))
            client_socket.close()
            sys.exit()




def main():
    threading.Thread(target=receive_message, args=(client_socket,)).start()
    
    # Create threads for sending and receiving messages
    receive_thread = threading.Thread(target=receive_message)
    # send_thread = threading.Thread(target=send_message)
    send_message()

    # Start the threads
    # send_thread.start()
    receive_thread.start()

if __name__ == '__main__':
    main()