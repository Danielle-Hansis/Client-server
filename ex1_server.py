#!/usr/bin/python3
import socket
import select
import sys
import struct


def main():
    users_file_path, port = parse_args(sys.argv)
    cred_dict = create_user_dict(users_file_path)


''' constants '''
DEFAULT_PORT = 1337


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




