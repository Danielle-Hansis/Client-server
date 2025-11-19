#!/usr/bin/python3
import sys
import socket
import select

# GLOBAL VARS
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
    try:        # Creating socket
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError:
        print("socket creation failed")
        sys.exit()

    try:        # Connecting to server
        client_sock.connect((hostname, port))
    except (ConnectionRefusedError, socket.gaierror, OSError) as e:     # Server not listening there or some DNS problem or OS
        # If the connection fails for any reason, close the socket and exit
        print("failed to connect to server:", e)
        client_sock.close()
        sys.exit()

    # Buffer to store bytes we receive from the server
    recv_buffer = b""

    # Main loop: handle both server responses and user input
    while True:
        # Wait until either the socket or stdin is ready to be read
        rlist, _, _ = select.select([client_sock, sys.stdin], [], [])

        # 1) Data from server
        if client_sock in rlist:
            try:
                data = client_sock.recv(4096)
            except OSError:
                break

            if not data:        # Server closed the connection
                break

            recv_buffer += data

            # Process all complete lines (ending with '\n')
            while b"\n" in recv_buffer:
                # Split once on the first newline
                line, recv_buffer = recv_buffer.split(b"\n", 1)

                # Remove a trailing '\r' if it's there (Windows-style line endings)
                line = line.rstrip(b"\r")

                # Decode bytes to string, replacing any bad bytes
                text = line.decode("utf-8", errors="replace")           # TODO: Do we need this replace thing? DANIELLE

                # Print the server's line to the user
                print(text)

        # 2) Data from user (stdin)
        if sys.stdin in rlist:
            user_line = sys.stdin.readline()

            if user_line == "":     # User is done - disconnect
                break

            # Send the line as-is (including its '\n') to the server
            try:
                client_sock.sendall(user_line.encode("utf-8"))
            except OSError:     # sending failed for whatever reason
                break

    client_sock.close()


if __name__ == "__main__":
    main()