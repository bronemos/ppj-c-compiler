import re
from enum import Enum


class Type(Enum):
    int = 'int'
    char = 'char'
    const_char_array = 'const_char_array'


def is_int(num):
    return -2147483648 <= int(num) <= 2147483647


def is_char(char):
    char_re = re.compile(r'^\'((?!\\)[\x00-\xff]|\\\\|\\t|\\n|\\0|\\\'|\\\")\'$')
    return char_re.match(char)


def is_const_char_array(string):
    string_re = re.compile(r'^\"((?!\\)[\x00-\xff]|\\\\|\\t|\\n|\\0|\\\'|\\\")*\"$')
    return string_re.match(string)
