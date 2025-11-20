#!/usr/bin/python3
import socket
import select
import sys
import funcs

''' GLOBAL VARS '''
DEFAULT_PORT = 1337
BACKLOG = 5
CLIENTS = set()
SOCKET_BUFFERS = {}
CLIENT_STATE = {}



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
        rlist = [server_socket] + list(CLIENTS)  # sockets to be monitored
        try:
            readable, _, _ = select.select(rlist, [], [])  # sockets ready for accept()/recv()
        except select.error:
            print("select failed")
            break
        for soc in readable:
            if soc is server_socket:  # the listening socket is ready to handle a new client
                handle_new_client(server_socket)
            else:  # client has data to pass / client closed
                if not handle_data_from_client(soc, cred_dict):
                    CLIENTS.discard(soc)
                    soc.close()


def handle_data_from_client(client: socket, cred_dict: dict) -> bool:
    try:
        data = client.recv(4096)
    except ConnectionResetError:        # Connection died without FIN
        return False
    except OSError:
        return False
    if not data:        # Client closed
        return False
    if client not in SOCKET_BUFFERS:        # Init buffer if needed
        SOCKET_BUFFERS[client] = b""
    SOCKET_BUFFERS[client] += data

    if client not in CLIENT_STATE:
        CLIENT_STATE[client] = {"stage": "awaiting_user","username": None}

    while b"\n" in SOCKET_BUFFERS[client]:
        line, rest = SOCKET_BUFFERS[client].split(b"\n", 1)
        SOCKET_BUFFERS[client] = rest
        line = line.rstrip(b"\r")
        text_line = line.decode("utf-8")
        if not handle_command(client, text_line, cred_dict):
            SOCKET_BUFFERS.pop(client, None)
            CLIENT_STATE.pop(client, None)
            return False
    return True


def handle_new_client(server_socket: socket):
    try:
        client, address = server_socket.accept()
    except OSError:
        print("An error has occurred")
        return
    CLIENTS.add(client)
    client.sendall(b"Welcome! Please log in.\n")
    return


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
            line = line.strip()
            user_password = line.split('\t')
            if len(user_password) == 2:
                cred_dict[user_password[0]] = user_password[1]
            else:
                print("Entries should be: user  password")
    if len(cred_dict) == 0:
        print("WARNING: No users found")
    return cred_dict


def handle_command(client: socket.socket, command: str, cred_dict:dict) -> bool:
    state = CLIENT_STATE[client]

    # Client hasn't logged in yet - need to handle log in first
    if state["stage"] != "logged_in":
        return funcs.handle_login(client, command, cred_dict, state)

    # User is already logged in
    if command == "quit":
        return False

    if command.startswith("parentheses"):
        return funcs.handle_parentheses(client, command)

    if command.startswith("lcm"):
        return funcs.handle_lcm(client, command)

    if command.startswith("caesar"):
        return funcs.handle_caesar(client, command)

    # Unknown command
    else:
        client.sendall(b"error: invalid input\n")
        return False


if __name__ == "__main__":
    main()




