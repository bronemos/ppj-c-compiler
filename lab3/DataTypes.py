import re
from enum import Enum


class Type(Enum):
    int = 'int'
    char = 'char'
    const_char_array = 'const_char_array'


def is_int(num):
    return -2147483648 <= int(num) <= 2147483647


def is_char(num):
    if not 0 <= num <= 255:
        return False
    char = chr(num)
    if len(char) == 1:
        return True
    else:
        char_re = re.compile(r'^\"(\\\\|\\t|\\n|\\0|\\\'|\\\")\"$')
        if char_re.match(char):
            return True
    return False


def is_const_char_array(string):
    pass
