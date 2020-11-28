import re
import sys
from copy import deepcopy

braces_regex = re.compile('\<(.+)\>')

data = [x.rstrip() for x in sys.stdin.readlines()]

# dict containing tuples, (value, bool) - bool value determines whether the symbol is terminal (True) or nonterminal (False)
grammar_dict = dict()
nonterminals = [braces_regex.search(x).group(1) for x in data[0].split(' ')[1:]]
first_state = 'S'
while first_state in nonterminals:
    first_state += 'S'
grammar_dict[(first_state, 0)] = [(nonterminals[0], True)]

index = 0
for element in data[3:]:
    if element[0] == ' ':
        grammar_dict[(latest_key, index := index + 1)] = [
            (match.group(1), True) if (match := braces_regex.search(x)) else (x, False)
            for x in element[1:].split(' ')]
    else:
        latest_key = braces_regex.findall(element)[0]

print(grammar_dict)
# finds all void nonterminals

void_nonterminals = set()
for key in grammar_dict:
    if ('$', False) in grammar_dict[key]:
        void_nonterminals.add((key[0], True))
while True:
    new_void_nonterminals = set(void_nonterminals)
    for left, right in grammar_dict.items():
        all_void = True
        for symbol in right:
            if symbol not in void_nonterminals:
                all_void = False
        if all_void:
            new_void_nonterminals.add((left[0], True))
    if len(new_void_nonterminals - void_nonterminals) == 0:
        break
    void_nonterminals = void_nonterminals | new_void_nonterminals

# creates begin_directly dict: key represents a state, value is set of symbols with which the key begins directly
begins_directly = dict()
for left, right in grammar_dict.items():
    if begins_directly.get(left[0]) is None:
        begins_directly[left[0]] = set()
    if right[0] != ('$', False):
        begins_directly[left[0]].add(right[0])
    for symbol in right:
        if symbol not in void_nonterminals and symbol != ('$', False):
            begins_directly[left[0]].add(symbol)
            break

# creates begins set by transitively checking begin_directly set
begins = deepcopy(begins_directly)

for key in begins_directly:
    begins[key].add((key, True))

change_occurred = True
while change_occurred:
    for key in begins_directly:
        for symbol in begins_directly[key]:
            if symbol[1] and begins_directly.get(symbol[0]) is not None:
                for transitive_symbol in begins_directly[symbol[0]]:
                    begins[key].add(transitive_symbol)
    if begins == begins_directly:
        change_occurred = False
    else:
        begins_directly = deepcopy(begins)

# print(begins)

sequence_end = '_|_'
last_point_index = -1  # easier to check for reduction later
enka_dict = {}  # (production_index, after_set, point_index, input_symbol) -> (production_index, after_set, point_index)
# create epsilon nka
change_occurred = True
after_set = {sequence_end}
nonterminals_to_process = [((first_state, 0), after_set)]
print(nonterminals_to_process[0])

while len(nonterminals_to_process) > 0:
    # TODO: check whether the state already exists
    current_nonterminal = nonterminals_to_process[0]
    production = grammar_dict.get(current_nonterminal[0])
    for index, symbol in enumerate(production):
        print(current_nonterminal[0][1])
        print(current_nonterminal[1])
        print(production[index])
        enka_dict[(current_nonterminal[0][1], list(current_nonterminal[1]), index, production[index])] \
            = (current_nonterminal[0][1], list(current_nonterminal[1]), index + 1)
        print(symbol)
        print(index)
    nonterminals_to_process.pop(0)
