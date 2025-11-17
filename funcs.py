import math
import socket

'''commands implementation'''

def handle_login(client: socket.socket, line: str, cred_dict: dict, state: dict) -> bool:       # TODO: Make sure we disconnect (return false) when need to, because I was very confused about this whole thing
    line = line.strip()     # Get rid of everything
    if state.get("stage") is None:
        state["stage"] = "awaiting_user"
        state["username"] = None

    if state["stage"] == "awaiting_user":
        if line.startswith("User:"):
            username = line[len("User:"):].strip()
            state["username"] = username
            state["stage"] = "awaiting_password"
            return True
        return False        # disconnect when you write nonesense - TODO: to danielle, did I understand the instructionsright? We need to disconnect if user gets it wrong???

    if state["stage"] == "awaiting_password":
        if line.startswith("Password:"):
            password = line[len("Password:"):].strip()
            username = state.get("username")

            if username in cred_dict and cred_dict[username] == password:
                msg = f"Hi {username}, good to see you\n"
                client.sendall(msg.encode("utf-8"))
                state["stage"] = "logged_in"
            else:
                client.sendall(b"Failed to login.\n")
                state["stage"] = "awaiting_user"        # Reset to allow another attempt
                state["username"] = None
            return True            # TODO: SAME HERE, I am confuseddddd
        return False

    return False        # Safety

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
    if x == 0 and y == 0:
        return None  # signal invalid input
    if x == 0 or y == 0:
        return abs(x or y)
    return abs(x // math.gcd(x, y) * y)

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



