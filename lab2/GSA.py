import re
import sys
from copy import deepcopy
from collections import defaultdict

braces_regex = re.compile('\<(.+)\>')

data = [x.rstrip() for x in sys.stdin.readlines()]

# dict containing tuples, (value, bool) - bool value determines whether the symbol is terminal (True) or nonterminal (False)
grammar_dict = dict()
nonterminals = [braces_regex.search(x).group(1) for x in data[0].split(' ')[1:]]
terminals = data[1].split(' ')[1:] + ['_|_']
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
# print(begins)

sequence_end = {'_|_'}
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
        try:
            production[index + 1]
        except IndexError:
            last = True
        enka_dict[(current_nonterminal[0], frozenset(current_nonterminal[1]), index, symbol)] \
            .add((current_nonterminal[0], frozenset(current_nonterminal[1]), -1 if last else index + 1))
        if production[index][1]:  # nonterminal is after point
            enka_dict_key = ((current_nonterminal[0]), frozenset(current_nonterminal[1]), index, ('$', False))
            for key in grammar_dict:
                if key[0] == production[index][0]:  # symbol in grammar dict is equeal to nonterminal after point
                    if last:
                        after_set = frozenset(current_nonterminal[1])
                        enka_dict[enka_dict_key].add((key, after_set, 0))
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
                        enka_dict[enka_dict_key].add((key, after_set, 0))

                    if (key, after_set) not in processed_nonterminals and (key, after_set) not in nonterminals_to_process:
                        nonterminals_to_process.append((key, after_set))

# for k, v in enka_dict.items():
#     print(f'{k} : {v}')

nka_states = set()
for k, v in enka_dict.items():
    nka_states.add(k[:3])
    nka_states = nka_states | v

# create DKA from ENKA
dka_states_dict = defaultdict(set)  # example dka_states_dict[0] = {(('S', 0), {'_|_'}, 0), ...}
number_of_states = 0
# group states
while len(nka_states) > 0:
    state = nka_states.pop()
    # provjeri sve epsilon prijelaze iz tog stanja u neko drugo, ista stvar za svako njegovo dijete, pop iz seta za sve
    group_children_from_states = {state}
    grouped_states = set()
    while len(group_children_from_states) > 0:
        state_to_check_children = group_children_from_states.pop()
        grouped_states.add(state_to_check_children)
        for k, v in enka_dict.items():
            if (state_to_check_children[0], state_to_check_children[1], state_to_check_children[2], ('$', False)) == k:
                for child_state in v:
                    if child_state not in group_children_from_states and child_state not in grouped_states:
                        try:
                            nka_states.remove(child_state)
                        except KeyError:
                            pass
                        finally:
                            group_children_from_states.add(child_state)

    # dobili smo skup stanja koji je epsilon okruzenje neke produkcije
    superset_from = set()
    already_exists = False
    for k, v in dka_states_dict.items():
        # ako postoji stanje u dka koje je podskup dobivenom skupu stanja, nadopuni to stanje, tj stavi nadskup unutra
        if grouped_states > v:
            already_exists = True
            superset_from.add(k)
        # ako postoji stanje u dka koje je nadskup dobivenom skupu stanja, continue while
        elif grouped_states < v:
            already_exists = True
            break

    # dodaj skup stanja u novo stanje
    if not already_exists:
        dka_states_dict[number_of_states] = grouped_states
        number_of_states += 1
    elif len(superset_from) > 0:
        for key in superset_from:
            del dka_states_dict[key]
        dka_states_dict[number_of_states] = grouped_states
        number_of_states += 1

print(len(dka_states_dict))

for k, v in dka_states_dict.items():
    if len(v) > 1:
        print(k, ':', v)

# make transitions
dka_dict = {}  # example 0, ('A', True) -> 1 ===== dka_dict[(0, ('A', True))] = 1
for k, v in dka_states_dict.items():
    for production in v:
        for k1, v1 in enka_dict.items():
            if k1[:3] == production and k1[3:][0][0] != '$':
                for k2, v2 in dka_states_dict.items():
                    if v1 <= v2:
                        dka_dict[(k, k1[3:][0])] = k2
                        break


print(len(dka_dict))
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
