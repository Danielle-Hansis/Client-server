import math

'''commands implementation'''

def handle_login(client: socket.socket, line: str, cred_dict: dict, state: dict) -> bool:
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
        return True

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
    if x == 0 and y == 0:
        return None  # signal invalid input
    if x == 0 or y == 0:
        return abs(x or y)
    return abs(x // math.gcd(x, y) * y)