import sys
import re

braces_regex = re.compile('\<(.+)\>')

data = [x.rstrip() for x in sys.stdin.readlines()]

#dict containing tuples, (value, bool) - bool value determines whether the symbol is terminal (True) or nonterminal (False)
grammar_dict = dict()

for element in data:
    if element[0] == ' ':
        element = element[1:]
        grammar_dict[(latest_key, False)].extend(
            (match.group(1), True) if (match := braces_regex.search(x)) else (x, False) for x in element.split(' '))
    else:
        latest_key = braces_regex.findall(element)[0]
        grammar_dict[(latest_key, False)] = []

print(grammar_dict)
