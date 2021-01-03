from enum import Enum


class Type(Enum):
    int = 'int'
    char = 'char'
    const_char_array = 'const_char_array'


def is_int(num):
    return -2147483648 <= num <= 2147483647


def is_char(num):
    return 0 <= num <= 255


def is_const_char_array(string):
    pass
