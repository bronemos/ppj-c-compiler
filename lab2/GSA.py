import re
import sys

braces_regex = re.compile('\<(.+)\>')

data = [x.rstrip() for x in sys.stdin.readlines()]

# dict containing tuples, (value, bool) - bool value determines whether the symbol is terminal (True) or nonterminal (False)
grammar_dict = dict()
nonterminals = [braces_regex.search(x).group(1) for x in data[0].split(' ')[1:]]
first_state = 'S'
while first_state in nonterminals:
    first_state += 'S'
grammar_dict[(first_state, 0)] = [(nonterminals[0], True)]

index = 1
for element in data[3:]:
    if element[0] == ' ':
        grammar_dict[(latest_key, index)] = []
        element = element[1:]
        grammar_dict[(latest_key, index)].extend(
            (match.group(1), True) if (match := braces_regex.search(x)) else (x, False) for x in element.split(' '))
        index += 1
    else:
        latest_key = braces_regex.findall(element)[0]

# print(grammar_dict)
