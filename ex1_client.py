#!/usr/bin/python3
import sys
import socket
import select

''' GLOBAL VARS '''
DEFAULT_PORT = 1337
DEFAULT_HOST = "localhost"


def parse_args(args: list):
    if len(args) > 3:
        print("the format is: ./ex1_client.py [hostname [port]]")
        sys.exit()
    if len(args) == 1:      # Use DEFAULT values
        hostname = DEFAULT_HOST
        port = DEFAULT_PORT
    elif len(args) == 2:        # Hostname given, DEFAULT port
        hostname = args[1]
        port = DEFAULT_PORT
    else:
        hostname = args[1]
        try:
            port = int(args[2])
        except ValueError:
            print("invalid port")
            sys.exit()
    return hostname, port


def main():
    hostname, port = parse_args(sys.argv)
    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError:
        print("Socket creation failed")
        sys.exit()

    try:
        client_sock.connect((hostname, port))
    except (ConnectionRefusedError, socket.gaierror, OSError):
        print("Failed to connect to server")
        client_sock.close()
        sys.exit()

    recv_buffer = b""       # Store data received from server

    while True:
        rlist, _, _ = select.select([client_sock, sys.stdin], [], [])

        # Case 1 - Data from server
        if client_sock in rlist:
            try:
                data = client_sock.recv(4096)
            except OSError:
                break
            if not data:        # Server closed the connection
                break
            recv_buffer += data
            while b"\n" in recv_buffer:
                line, recv_buffer = recv_buffer.split(b"\n", 1)
                line = line.rstrip(b"\r")
                text = line.decode("utf-8", errors="replace")       # Decode, replace bad bytes to avoid crash
                print(text)

        # Case 2 - Data from user
        if sys.stdin in rlist:
            user_line = sys.stdin.readline()
            if user_line == "":     # User is done - disconnect
                break
            try:
                client_sock.sendall(user_line.encode("utf-8"))
            except OSError:
                break
    client_sock.close()


if __name__ == "__main__":
    main()