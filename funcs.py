import math
import socket

''' Commands Implementation '''


def handle_login(client: socket.socket, line: str, cred_dict: dict, state: dict) -> bool:
    line = line.strip()
    if state.get("stage") is None:
        state["stage"] = "awaiting_user"
        state["username"] = None

    if state["stage"] == "awaiting_user":
        if line.startswith("User:"):
            username = line[len("User:"):].strip()
            state["username"] = username
            state["stage"] = "awaiting_password"
            return True
        client.sendall(b"error: invalid input\n")
        return False        # disconnect when you write nonesense

    if state["stage"] == "awaiting_password":
        if line.startswith("Password:"):
            password = line[len("Password:"):].strip()
            username = state.get("username")

            if username in cred_dict and cred_dict[username] == password:
                msg = f"Hi {username}, good to see you.\n"
                client.sendall(msg.encode("utf-8"))
                state["stage"] = "logged_in"
            else:
                client.sendall(b"Failed to login.\n")
                state["stage"] = "awaiting_user"        # Reset to allow another attempt
                state["username"] = None
            return True
        client.sendall(b"error: invalid input\n")
        return False
    client.sendall(b"error: invalid input\n")
    return False


def handle_parentheses(client, command: str) -> bool:
    if ":" in command:
        seq = command.split(":", 1)[1].strip()
    else:
        seq = ""

    # Check that only parentheses in client's input text
    for ch in seq:
        if ch not in ("(", ")"):
            client.sendall(b"error: invalid input\n")
            return False

    ok = balanced_parentheses(seq)
    client.sendall(f"the parentheses are balanced: {'yes' if ok else 'no'}\n".encode())
    return True


def handle_lcm(client, command: str) -> bool:
    if ":" not in command:
        client.sendall(b"error: invalid input\n")
        return False

    after_colon = command.split(":", 1)[1].strip()
    parts = after_colon.split()
    if len(parts) != 2:
        client.sendall(b"error: invalid input\n")
        return False

    x_str, y_str = parts
    try:
        x = int(x_str)
        y = int(y_str)
    except ValueError:
        client.sendall(b"error: invalid input\n")
        return False

    result = calc_lcm(x, y)
    client.sendall(f"the lcm is: {result}\n".encode())
    return True


def handle_caesar(client, command: str) -> bool:
    if ":" not in command:
        client.sendall(b"error: invalid input\n")
        return False

    after_colon = command.split(":", 1)[1].strip()
    parts = after_colon.rsplit(" ", 1)
    if len(parts) != 2:
        client.sendall(b"error: invalid input\n")
        return False

    plaintext, shift_str = parts[0], parts[1]
    try:
        shift = int(shift_str)
    except ValueError:
        client.sendall(b"error: invalid input\n")
        return False

    result = caesar_code(plaintext, shift)
    if result is None:
        client.sendall(b"error: invalid input\n")
        return False

    client.sendall(f"the ciphertext is: {result}\n".encode())
    return True


def balanced_parentheses(seq: str):
    counter = 0
    for ch in seq:
        if ch == '(':
            counter += 1
        elif ch == ')':
            counter -= 1
            if counter < 0:
                return False
    return counter == 0


def calc_lcm(x: int, y: int) -> int:
    x = abs(x)
    y = abs(y)

    if x == 0 or y == 0:
        return 0

    return (x * y) // math.gcd(x, y)


def caesar_code(plaintext: str, x: int) -> str:
    y = []
    plaintext = plaintext.lower()
    for character in plaintext:
        if not ('a' <= character <= 'z' or character == ' '):     # Invalid input
            return None
        if 'a' <= character <= 'z':
            y.append(chr((ord(character) - ord('a') + x) % 26 + ord('a')))
        else:
            y.append(character)
    return ''.join(y)
