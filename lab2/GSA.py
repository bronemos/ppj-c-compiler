import re
import sys
from copy import deepcopy
from collections import defaultdict

braces_regex = re.compile('\<(.+)\>')

data = [x.rstrip() for x in sys.stdin.readlines()]

# dict containing tuples, (value, bool) - bool value determines whether the symbol is terminal (True) or nonterminal (False)
grammar_dict = dict()
nonterminals = [braces_regex.search(x).group(1) for x in data[0].split(' ')[1:]]
terminals = data[1].split(' ')[1:] + ['#']
first_state = '%'
grammar_dict[(first_state, 0)] = [(nonterminals[0], True)]

index = 0
for element in data[3:]:
    if element[0] == ' ':
        grammar_dict[(latest_key, index := index + 1)] = [
            (match.group(1), True) if (match := braces_regex.search(x)) else (x, False)
            for x in element[1:].split(' ')]
    else:
        latest_key = braces_regex.findall(element)[0]

# print(grammar_dict)
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
begins_directly = deepcopy(begins)

while True:
    for key in begins_directly:
        for symbol in begins_directly[key]:
            if symbol[1] and begins_directly.get(symbol[0]) is not None:
                for transitive_symbol in begins_directly[symbol[0]]:
                    begins[key].add(transitive_symbol)
    if begins == begins_directly:
        break
    else:
        begins_directly = deepcopy(begins)

# remove nonterminals from begins
for k, v in begins.items():
    remove_set = set()
    for symbol in v:
        if symbol[1]:
            remove_set.add(symbol)
    begins[k] -= remove_set

for k, v in begins.items():
    begins[k] = {x[0] for x in v}
print(begins)

sequence_end = {'#'}
last_point_index = -1  # easier to check for reduction later
enka_dict = defaultdict(set)
# (production_index, after_set, point_index, input_symbol) -> (production_index, after_set, point_index)
# create epsilon nka
after_set = frozenset(sequence_end)
nonterminals_to_process = [((first_state, 0), after_set)]
processed_nonterminals = list()

while len(nonterminals_to_process) > 0:
    current_nonterminal = nonterminals_to_process.pop(0)
    processed_nonterminals.append(current_nonterminal)
    production = grammar_dict.get(current_nonterminal[0])
    for index, symbol in enumerate(production):
        last = False
        point_on_last_index = False
        if symbol == ('$', False):
            point_on_last_index = True
        try:
            production[index + 1]
        except IndexError:
            last = True
        if not point_on_last_index:
            enka_dict[(current_nonterminal[0], frozenset(current_nonterminal[1]), index, symbol)] \
                .add((current_nonterminal[0], frozenset(current_nonterminal[1]), -1 if last else (index + 1)))
        if production[index][1]:  # nonterminal is after point
            enka_dict_key = ((current_nonterminal[0]), frozenset(current_nonterminal[1]), index, ('$', False))
            for key in grammar_dict:
                if key[0] == production[index][0]:  # symbol in grammar dict is equeal to nonterminal after point
                    new_state_index = 0
                    if grammar_dict[key][0] == ('$', False):
                        print(key)
                        new_state_index = -1
                    if last:
                        after_set = frozenset(current_nonterminal[1])
                        enka_dict[enka_dict_key].add((key, after_set, new_state_index))
                    else:  # not last
                        after_set = set()
                        in_index = index + 1
                        while True:
                            if not production[in_index][1]:  # if next symbol is terminal add it to set and break
                                after_set.add(production[in_index][0])
                                break
                            else:
                                after_set = after_set | begins[production[in_index][0]]
                                if (production[in_index][0], True) in void_nonterminals:
                                    in_index += 1
                                    if len(production) <= in_index:
                                        after_set = after_set | current_nonterminal[1]
                                        break
                                else:
                                    break
                        after_set = frozenset(after_set)
                        enka_dict[enka_dict_key].add((key, after_set, new_state_index))

                    if (key, after_set) not in processed_nonterminals and (key, after_set) not in nonterminals_to_process:
                        nonterminals_to_process.append((key, after_set))

for k, v in enka_dict.items():
    print(f'{k} : {v}')
# +++++++++++++++++++++ do ovdje sve radi

# find all enka_states
enka_states = set()
for k, v in enka_dict.items():
    enka_states.add(k[:3])
    enka_states = enka_states | v

print(len(enka_states))

# create NKA from ENKA
# nadji epsilon okruzenja svakog stanja
epsilon_okruzenja = dict()

for state in enka_states:
    if enka_dict.get(state + (('$', False),)) is not None:
        epsilon_okruzenja[state] = {state} | enka_dict.get(state + (('$', False),))
        while True:
            old_epsilons = deepcopy(epsilon_okruzenja[state])
            for state1 in old_epsilons:
                if enka_dict.get(state1 + (('$', False),)) is not None:
                    epsilon_okruzenja[state] |= enka_dict[state1 + (('$', False),)]
            if len(epsilon_okruzenja[state] - old_epsilons) == 0:
                break
    else:
        epsilon_okruzenja[state] = {state}

print(len(epsilon_okruzenja))  # OK

nka_dict = defaultdict(set)
for k, v in enka_dict.items():
    if k[3] == ('$', False):
        continue
    else:
        for state in v:
            nka_dict[k] |= epsilon_okruzenja[state]

print(len(nka_dict))
dka_dict = {}
# example frozenset({produkcije...}), ('A', True) -> frozenset({produkcije...})
# ===== dka_dict[(frozenset({produkcije...}), ('A', True))] = frozenset({produkcije...})
state_key_dict = {0: frozenset(epsilon_okruzenja[((first_state, 0), frozenset({'#'}), 0)])}
state_key_dict_reversed = {frozenset(epsilon_okruzenja[((first_state, 0), frozenset({'#'}), 0)]): 0}
states_to_process = [0]
states_num = 0
processed_states = []
while len(states_to_process) > 0:
    state_num = states_to_process.pop(0)
    processed_states.append(state_num)
    find_transitions_for = state_key_dict[state_num]
    for state in find_transitions_for:
        for k, v in nka_dict.items():
            if k[:3] == state:
                if not frozenset(v) in state_key_dict.values():
                    states_num += 1
                    state_key_dict[states_num] = frozenset(v)
                    state_key_dict_reversed[frozenset(v)] = states_num
                    if states_num not in states_to_process and states_num not in processed_states:
                        states_to_process.append(states_num)
                dka_dict[(state_num, k[3])] = state_key_dict_reversed[frozenset(v)]

for k, v in dka_dict.items():
    print(k, ':', v)

# make transitions
# for k, v in dka_states_dict.items():
#     for production in v:
#         for k1, v1 in enka_dict.items():
#             if k1[:3] == production and k1[3:][0][0] != '$':
#                 for k2, v2 in dka_states_dict.items():
#                     if v1 <= v2:
#                         dka_dict[(k, k1[3:][0])] = k2
#                         break

# print(len(dka_dict))
# create tables action and new_state
# Pomakni/Reduciraj proturjeˇcje izgradeni generator treba razrijeˇsiti u korist akcije Pomakni. Reduciraj/Reduciraj
# proturječje potrebno je razrijeˇsiti u korist one akcije koja reducira produkciju zadanu ranije u Ulaznoj Datoteci

# actions = {}  # (0, ('a', False)) -> (1, 'move' or 'reduce', production ('A', 1) -> only needed for reduce)
# new_state = {}  # (0, ('A', True)) -> 4
# for k, v in dka_dict.items():
#     if not k[1][1]:  # transition is for nonterminal, add to action table
#         for nonterminal in nonterminals:
#             if k[1][0] == nonterminal:
#                 # provjeri treba li izvsiti akciju pomakni, ako ne pogledaj moze li se reducrati. Uzmi prvu akciju reduciraj
#                 pass
#
#     else:  # add to new_state table
#         pass
