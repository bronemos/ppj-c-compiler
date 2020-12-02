import re
import sys
from copy import deepcopy
from collections import defaultdict
import time
import pickle as serializer

start_time = time.time()
braces_regex = re.compile('\<(.+)\>')
data = [x.rstrip() for x in sys.stdin.readlines()]

# dict containing tuples, (value, bool) - bool value determines whether the symbol is terminal (True) or nonterminal (False)
grammar_dict = dict()
nonterminals = [braces_regex.search(x).group(1) for x in data[0].split(' ')[1:]]
terminals = data[1].split(' ')[1:] + ['#']
synchronization_symbols = data[2].split(' ')[1:]
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
# print(begins)

sequence_end = {'#'}
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
        last_symbol = index == len(production) - 1
        if not symbol == ('$', False):
            enka_dict[(current_nonterminal[0], frozenset(current_nonterminal[1]), index, symbol)] \
                .add((current_nonterminal[0], frozenset(current_nonterminal[1]), -1 if last_symbol else (index + 1)))
        if production[index][1]:  # nonterminal is after point
            enka_dict_key = ((current_nonterminal[0]), frozenset(current_nonterminal[1]), index, ('$', False))
            for key in grammar_dict:
                if key[0] == production[index][0]:  # symbol in grammar dict is equeal to nonterminal after point
                    new_state_index = -1 if grammar_dict[key][0] == ('$', False) else 0
                    if last_symbol:
                        after_set = frozenset(current_nonterminal[1])
                        enka_dict[enka_dict_key].add((key, after_set, new_state_index))
                    else:  # not last_symbol
                        after_set = set()
                        index_to_check = index + 1
                        while True:
                            if not production[index_to_check][1]:  # if next symbol is terminal add it to set and break
                                after_set.add(production[index_to_check][0])
                                break
                            else:
                                after_set = after_set | begins[production[index_to_check][0]]
                                if (production[index_to_check][0], True) in void_nonterminals:
                                    index_to_check += 1
                                    if len(production) <= index_to_check:
                                        after_set = after_set | current_nonterminal[1]
                                        break
                                else:
                                    break
                        after_set = frozenset(after_set)
                        enka_dict[enka_dict_key].add((key, after_set, new_state_index))

                    if (key, after_set) not in processed_nonterminals and (
                            key, after_set) not in nonterminals_to_process:
                        nonterminals_to_process.append((key, after_set))

# for k, v in enka_dict.items():
#     print(f'{k} : {v}')

# find all enka_states
counter = 0
enka_states = set()
for k, v in enka_dict.items():
    enka_states.add(k[:3])
    enka_states = enka_states | v
    counter += len(v)

print(f'Broj stanja u eNKA: {len(enka_states)}')
print(f'Broj prijelaza u eNKA: {counter}')

# create NKA from ENKA
# nadji epsilon okruzenja svakog stanja
epsilon_closures = dict()

for state in enka_states:
    if enka_dict.get(state + (('$', False),)) is not None:
        epsilon_closures[state] = {state} | enka_dict.get(state + (('$', False),))
        while True:
            old_epsilons = deepcopy(epsilon_closures[state])
            for state1 in old_epsilons:
                if epsilon_closures.get(state1) is not None:
                    epsilon_closures[state] |= epsilon_closures.get(state1)
                    continue
                if enka_dict.get(state1 + (('$', False),)) is not None:
                    epsilon_closures[state] |= enka_dict[state1 + (('$', False),)]
            if len(epsilon_closures[state] - old_epsilons) == 0:
                break
    else:
        epsilon_closures[state] = {state}

nka_transitions = defaultdict(set)
for k, v in enka_dict.items():
    if k[3] == ('$', False):
        continue
    else:
        for state in v:
            nka_transitions[k] |= epsilon_closures[state]

# print(len(nka_transitions))
nka_dict = defaultdict(set)
# example frozenset({produkcije...}), ('A', True) -> {frozenset({produkcije...}), frozenset()}
# ===== nka_dict[(frozenset({produkcije...}), ('A', True))] = {frozenset({produkcije...}), fs()}
nka_states = {0: frozenset(epsilon_closures[((first_state, 0), frozenset({'#'}), 0)])}
nka_states_reversed = {frozenset(epsilon_closures[((first_state, 0), frozenset({'#'}), 0)]): 0}
states_to_process = [0]
states_num = 0
while len(states_to_process) > 0:
    state_num = states_to_process.pop(0)
    find_transitions_for = nka_states[state_num]
    for state in find_transitions_for:
        for k, v in nka_transitions.items():
            if k[:3] == state:
                if not frozenset(v) in nka_states.values():  # nka_states_reversed.keys()
                    states_num += 1
                    nka_states[states_num] = frozenset(v)
                    nka_states_reversed[frozenset(v)] = states_num
                    states_to_process.append(states_num)
                nka_dict[(state_num, k[3])].add(nka_states_reversed[frozenset(v)])

counter = 0
for k, v in nka_dict.items():
    counter += len(v)
print(f'Broj stanja u NKA: {len(nka_states)}')
print(f'Broj prijelaza u NKA: {counter}')
# for k, v in nka_states.items():
#     print(f'{k} : {v}')
# print('--' * 10)

state_num = 0
dka_dict = {}  # 0, a -> 2
dka_states = {}  # 0 -> frozenset()
dka_states_reversed = {}  # frozenset() -> 0


# Finally create DKA from NKA
def add_dka_state(snka):
    global state_num
    global dka_dict
    global dka_states
    global dka_states_reversed
    #     ako DKA već sadrži stanje koje odgovara skupu:
    #         vrati to stanje;
    if dka_states_reversed.get(frozenset(snka)) is not None:
        return dka_states_reversed.get(frozenset(snka))

    #     prijelazi = nova mapa(znak -> skup stanja NKA);
    transitions = defaultdict(set)  # a -> {1, 3, 5, 7}

    #     za svako stanje s u snka:
    #         za svaki prijelaz (znak k prelazi u skup stanja NKA p) od s:
    #             dodaj sva stanja iz p u prijelazi[k];
    for state in snka:
        for k, v in nka_dict.items():
            if state == k[0]:
                transitions[k[1]] = transitions[k[1]] | v

    #     U DKA stvori novo stanje sdka koje odgovara skupu snka;
    key = state_num
    dka_states[key] = frozenset(snka)
    dka_states_reversed[frozenset(snka)] = key
    state_num += 1
    #
    #     za svaki prijelaz (znak z prelazi u skup stanja NKA p) iz prijelazi:
    #         U DKA dodaj prijelaz iz sdka u dohvatiStanje(p) za znak z;
    for k, v in transitions.items():
        dka_dict[(key, k)] = add_dka_state(v)

    #     Vrati sdka;
    return key


add_dka_state({0})

# for k, v in dka_dict.items():
#     print(f'{k} : {v}')
# for k, v in dka_states.items():
#     print(f'{k} : {v}')
print(f'Broj stanja u DKA: {len(dka_states)}')
print(f'Broj prijelaza u DKA: {len(dka_dict)}')

# check productions associated with each state in DKA
reduction_for_dka_state = {}
# only reductions are needed here
for k, v in dka_states.items():  # za sva stanja u dka
    reductions = set()
    for nka_state in v:  # za sva nka stanja koja se nalaze u dka stanju
        for production in nka_states[nka_state]:  # za svaku produkciju koju sadrzi nka stanje
            if production[2] == -1:  # tocka je na kraju
                reductions.add(production)  # dodaj redukciju u set
    if len(reductions) > 0:
        reduction_for_dka_state[k] = reductions  # dodaj set redukcija za staje

# print(reduction_for_dka_state)
# create tables action and new_state
# analizatoru treba proslijediti action, new_state i grammar_dict
actions = {}  # (0, ('a', False)) -> (1, 'move' == True or 'reduce', production ('A', 1) -> only needed for reduce)
new_state = {}  # (0, ('A', True)) -> 4
for k in dka_states.keys():
    # provjeri treba li izvsiti akciju pomakni, ako ne pogledaj moze li se reducrati. Uzmi prvu akciju reduciraj
    for nonterminal in nonterminals:
        if dka_dict.get((k, (nonterminal, True))) is not None:
            new_state[(k, nonterminal)] = dka_dict.get((k, (nonterminal, True)))

    # provjeri treba li izvsiti akciju pomakni, ako ne pogledaj moze li se reducrati. Uzmi prvu akciju reduciraj
    for terminal in terminals:
        reduction = None
        if reduction_for_dka_state.get(k) is not None:
            reduction = None
            for reduction_for_state in frozenset(reduction_for_dka_state.get(k)):
                if terminal in reduction_for_state[1]:
                    if reduction is None:
                        reduction = reduction_for_state[0]
                    else:
                        print(f'reduciraj - reduciraj proturječje stanje: {k}, znak: {terminal}', file=sys.stderr, end='')
                        if reduction_for_state[0][1] < reduction[1]:
                            reduction = reduction_for_state[0]
        if dka_dict.get((k, (terminal, False))) is not None:
            actions[(k, terminal)] = (True, dka_dict.get((k, (terminal, False))))
            if reduction is not None:
                print(f'pomakni - reduciraj proturječje stanje: {k}, znak: {terminal}, pomakni: {dka_dict.get((k, (terminal, False)))}, reduciraj {reduction}', file=sys.stderr, end='')
        elif reduction is not None:
            actions[(k, terminal)] = (False, (reduction[0], True), grammar_dict.get(reduction))

# print('----------NEW_STATE----------')
# for k, v in new_state.items():
#     print(f'{k} : {v}')
# print(new_state)
# print('----------ACTIONS----------')
# for k, v in actions.items():
#     print(f'{k} : {v}')
# print(actions)

with open('analizator/new_state.txt', 'wb') as f:
    serializer.dump(new_state, f)

with open('analizator/actions.txt', 'wb') as f:
    serializer.dump(actions, f)

with open('analizator/synchronization.txt', 'wb') as f:
    serializer.dump(synchronization_symbols, f)


# print(f'Time: {time.time() -  start_time}')
