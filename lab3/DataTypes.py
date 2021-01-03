from enum import Enum
import re


class Type(Enum):
    int = 'int'
    char = 'char'
    const_char_array = 'const_char_array'


def is_int(num):
    return -2147483648 <= num <= 2147483647


def is_char(char):
    char_re = re.compile(r'^\"([a-z]|\\\\|\\t|\\n|\\0|\\\'|\\\")\"$')
    if char_re.match(char):
        return True
    return False

def is_const_char_array(string):
    pass
