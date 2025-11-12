#!/usr/bin/python3
import socket
import select
import sys
import struct


''' constants '''
DEFAULT_PORT = 1337
BACKLOG = 5  # 5 is reasonable as a backlog, since the whole point is not to be blocking
CLIENTS = set()  # holds unique connections


def main():
    users_file_path, port = parse_args(sys.argv)
    cred_dict = create_user_dict(users_file_path)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4,TCP
    server_socket.bind(('', port))
    server_socket.listen(BACKLOG)
    '''we now have a listening socket'''
    server_workflow(server_socket, cred_dict)


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
    #TODO this
    try:
# TODO get info (recv)
    except OSError:
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




