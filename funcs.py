import math


'''commands implementation'''
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