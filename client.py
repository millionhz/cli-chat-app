'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
from threading import Thread
from pathlib import Path
import util


'''
Write your code inside this class.
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen
for incoming messages in this function.
'''


class Client:
    '''
    This is the main Client Class.
    '''

    def __init__(self, username, dest, port):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(None)
        self.name = username

        self.is_alive = True

        try:
            self.sock.connect((self.server_addr, self.server_port))
        except ConnectionRefusedError:
            self.shutdown()

    def start(self):
        '''
        Main Loop is here
        Start by sending the server a JOIN message.
        Waits for userinput and then process it
        '''
        self.send_message("join", 1, self.name)

        while True:
            in_str = input().split(" ")

            if not self.is_alive:
                sys.exit()

            if in_str[0] == "msg":
                self.send_message("send_message", 4, " ".join(in_str[1:]))

            elif in_str[0] == "list":
                self.send_message("request_users_list", 2)

            elif in_str[0] == "file":
                file = Path(in_str[-1])

                if file.is_file():
                    with open(file, "rt", encoding='UTF-8') as file:
                        data = file.read()

                    self.send_message("send_file", 4, " ".join(
                        in_str[1:-1]) + " " + file.name + " " + data)
                else:
                    print("Incorrect file path")

            elif in_str[0] == "help":
                self.print_help()

            elif in_str[0] == "quit":
                self.shutdown(prompt_server=True)

            else:
                print("incorrect userinput format")

    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        '''
        while True:
            try:
                recv_str = self.receive_message()
            except (ConnectionAbortedError, ConnectionResetError):
                self.is_alive = False
                return

            if recv_str[0] == "ERR_SERVER_FULL":
                print("disconnected: server full")
                break

            elif recv_str[0] == "ERR_USERNAME_UNAVAILABLE":
                print("disconnected: username not available")
                break

            elif recv_str[0] == "err_unknown_message":
                print("disconnected: server received an unknown command")
                break

            elif recv_str[0] == "forward_message":
                sender_username = recv_str[1]
                message = " ".join(recv_str[2:])
                print(f"msg: {sender_username}: {message}")

            elif recv_str[0] == "forward_file":
                sender_username = recv_str[1]
                filename = recv_str[2]
                data = " ".join(recv_str[3:])

                print(f"file: {sender_username}: {filename}")

                with open(self.name+"_"+filename, "w", encoding="UTF-8") as file:
                    file.write(data)

            elif recv_str[0] == "RESPONSE_USERS_LIST":
                usernames_str = " ".join(sorted(recv_str[1:], key=str.lower))
                print(f"list: {usernames_str}")

            else:
                pass

        self.is_alive = False
        self.shutdown()

    def send_message(self, msg_type, msg_format, message=None):
        '''
        Send message to server
        '''
        send_str = util.make_message(msg_type, msg_format, message)
        self.sock.send(send_str.encode("utf-8"))

    def receive_message(self):
        '''
        Receive message from server
        '''
        return self.sock.recv(10240).decode().split(" ")

    def print_help(self):
        '''
        Print help message
        '''
        print("Available commands:")
        print(
            "msg [num of clients] [clients] [message]".ljust(50) + "send message to client(s)")
        print(
            "file [num of clients] [clients] [file path]".ljust(50) + "send file to client(s)")
        print("list".ljust(50) + "get list of connected client(s)")
        print("quit".ljust(50) + "shutdown client")

    def shutdown(self, prompt_server=False):
        '''
        Shutdown client instance
        '''
        if prompt_server:
            self.send_message("disconnect", 1, self.name)
            self.sock.close()

        print("quitting")
        sys.exit()


# Do not change this part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a", ["user=", "port=", "address="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
