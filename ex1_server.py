#!/usr/bin/python3
import socket
import select
import sys
import struct
import funcs

''' constants '''
DEFAULT_PORT = 1337
BACKLOG = 5  # 5 is reasonable as a backlog, since the whole point is not to be blocking
CLIENTS = set()  # holds unique connections
SOCKET_BUFFERS = {}     # NEW - dict to save commands until we're done with processing
CLIENT_STATE = {}       # NEW - dict to save client state; pre or post login




def main():
    users_file_path, port = parse_args(sys.argv)
    cred_dict = create_user_dict(users_file_path)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4,TCP
    server_socket.bind(('', port))
    server_socket.listen(BACKLOG)
    # NEW - Try and Finally
    try:
        server_workflow(server_socket, cred_dict)
    finally:
        server_socket.close()


def server_workflow(server_socket: socket, cred_dict: dict):
    while True:
        #  build the rlist dynamically every loop from the sockets that currently exist:
        rlist = [server_socket] + list(CLIENTS)  # sockets to be monitored
        try:
            readable, _, _ = select.select(rlist, [], [])  # sockets ready for accept()/recv()
        except select.error as e:
            print("select failed")
            break
        for soc in readable:
            if soc is server_socket:  # the listening socket is ready to handle a new client
                handle_new_client(server_socket)
            else:  # a client has data to pass/ a client closed
                if not handle_data_from_client(soc, cred_dict):
                    CLIENTS.discard(soc)
                    soc.close()



def handle_data_from_client(client: socket, cred_dict: dict) -> bool:
    try:
        data = client.recv(4096)        # 4KB is convention - in tirgul he did 1024
    except ConnectionResetError:        # Connection died without FIN
        return False
    except OSError:
        return False
    if not data:        # Client closed
        return False
    if client not in SOCKET_BUFFERS:        # Init buffer if needed     NEW FROM HERE
        SOCKET_BUFFERS[client] = b""
    SOCKET_BUFFERS[client] += data          # Append data to buffer

    if client not in CLIENT_STATE:
        CLIENT_STATE[client] = {"stage": "awaiting_user","username": None}

    while b"\n" in SOCKET_BUFFERS[client]:  # As long as we have a full line - process it
        line, rest = SOCKET_BUFFERS[client].split(b"\n", 1)     # Split once
        SOCKET_BUFFERS[client] = rest
        line = line.rstrip(b"\r")
        text_line = line.decode("utf-8")
        if not handle_command(client, text_line, cred_dict):       # NEW
            return False
    return True

def handle_new_client(server_socket: socket):
    try:
        client, address = server_socket.accept()
    except OSError:
        print("an error has occurred")
        return
    CLIENTS.add(client)
    client.sendall(b"Welcome! Please log in.")  # TODO: maybe create a sendall implementation
    return



'''argument setup'''
# the server gets started by ./ex1_server.py users_file [port]
# file_users: path to a text file with tab separated user   &passwords
# port: not mandatory, default is 1337
def parse_args(args: list):
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("the format is: ./ex1_server.py users_file [port]")
        sys.exit()
    users_file_path = sys.argv[1]
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("invalid port")
            sys.exit()
    else:
        port = DEFAULT_PORT
    return users_file_path, port


def create_user_dict(users_file_path: str):
    cred_dict = {}
    try:
        users_file = open(users_file_path, 'r')
    except FileNotFoundError:
        print("user file not found")
        sys.exit()

    with users_file:
        for line in users_file:
            line = line.strip()  # gets rid of '\n'
            user_password = line.split('\t')  # gets rid of tab, becomes ['user','pass'] hopefully
            if len(user_password) == 2:
                cred_dict[user_password[0]] = user_password[1]
            else:
                print("entries should be: user  password")
    if len(cred_dict) == 0:
        print("WARNING: no users found")
    return cred_dict





'''supported commands'''
def handle_command(client: socket.socket, command: str, cred_dict:dict) -> bool:        # NEW
    state = CLIENT_STATE[client]

    if state["stage"] != "logged_in":       # Need to handle log in first - NEW, I added this + the func in funcs
        return funcs.handle_login(client, command, cred_dict, state)

    # NOW - User is logged in
    if command == "quit":
        return False

    if command.startswith("parentheses"):
        if ":" in command:
            seq = command.split(":", 1)[1].strip()
        else:
            seq = ""
        ok = funcs.balanced_parentheses(seq)
        client.sendall(f"the parentheses are balanced: {'yes' if ok else 'no'}\n".encode())
        return True
    # TODO: Add all the other funny functions <3

