import sys
import pickle as serializer


class Machine:
    def __init__(self, name, first, acceptable, transitions):
        self.name = name
        self.first_state = first
        self.acceptable_state = acceptable
        self.transitions = transitions

    def __str__(self):
        return f'name: {self.name}\nfirst, acceptable: {self.first}, {self.acceptable}\ntransitions: {self.transitions}'


def updateSetE(states_set, transitions):
    helper_list = sorted(states_set)
    index = 0
    while True:
        if index > len(helper_list) - 1:
            break
        state = helper_list[index]
        if (state, '$') in transitions:
            for new_state in transitions[(state, '$')]:
                was_in_set = new_state in states_set
                if not was_in_set:
                    states_set.add(new_state)
                    helper_list.append(new_state)
        index += 1
    return states_set


data = open('table.txt', 'r').readlines()
analyzer_starting_state = data[0].rstrip()

# read machines data from table.txt
machine_list = []
transitions = {}
next_line_is_name = True
machine_name = ''
actions_start_index = 0
for i in range(1, len(data)):
    data[i] = data[i].rstrip()
    if data[i] == '-' * 80:
        actions_start_index = i + 1
        break  # lines with actions will start from next line
    elif next_line_is_name:
        next_line_is_name = False
        machine_name = data[i]  # name of machine is equal to regex
        transitions = {}
    elif data[i][:5] == 'start':  # last line with start and acceptable state
        next_line_is_name = True
        start_state = data[i].split(',')[0].split(':')[1]
        acceptable_state = data[i].split(',')[1].split(':')[1]
        machine_list.append(Machine(machine_name, start_state, acceptable_state, transitions))
    else:
        current_state = data[i].split('->')[0].split(',')[0]
        input_char_idx = data[i].split('->')[0].find(',') + 1
        input_char = data[i].split('->')[0][input_char_idx]
        if input_char == '\\n':  # change //n to /n
            input_char = '\n'
        key = (current_state, input_char)
        nextState = data[i].split('->')[1]
        if transitions.get(key) is not None:
            transitions[key].append(nextState)
        else:
            transitions[key] = []
            transitions[key].append(nextState)

# check data
# for machine in machine_list:
#     print(machine)

# read machines data from table.txt
# reads actions dict from test.txt
with open('test.txt', 'rb') as f:
    actions: dict = serializer.load(f)

# variables taken from book
start_pointer = 0
last_found_pointer = -1
current_reading_pointer = 0
input_stream = ''.join(sys.stdin.readlines())
analyzer_current_state = analyzer_starting_state
machine_in_acceptable_state_index_set = set()  # set that contains index for every machine that is in acceptable state

# list containing set of states for each machine
current_states = []
for i in range(len(machine_list)):
    current_states.append(set())
    current_states[i].add(machine_list[i].first_state)
    current_states[i] = updateSetE(current_states[i], machine_list[i].transitions)
starting_states = current_states

action_key = None
line = 1
while current_reading_pointer < len(input_stream):
    current_char = input_stream[current_reading_pointer]
    new_states = [set() for x in range(len(machine_list))]
    new_states_is_empty = True

    for i in range(len(machine_list)):
        for state in current_states[i]:
            if (state, input_stream[current_reading_pointer]) in machine_list[i].transitions:
                for new_state in machine_list[i].transitions[(state, input_stream[current_reading_pointer])]:
                    new_states_is_empty = False
                    new_states[i].add(new_state)
        new_states[i] = updateSetE(new_states[i], machine_list[i].transitions)

    machine_in_acceptable_state_index_set = set()
    if not new_states_is_empty:
        # if new states were added check which machines are in acceptable state
        for i in range(len(machine_list)):
            for state in new_states[i]:
                if state == machine_list[i].acceptable_state:
                    machine_in_acceptable_state_index_set.add(i)
        # TODO: check which action is first for analyzer_current_state and any of machines in set
        # trazim u dictionariju par stanje_analizator i ime automata (machine in acceptable state index set je index u listi automata) - machine_list lista automata
        # if action_exists:
        #     last_found_pointer = current_reading_pointer
        action_found = False
        for k, v in actions.items():
            for state_idx in machine_in_acceptable_state_index_set:
                if k == (analyzer_current_state, machine_list[state_idx].name):
                    last_found_pointer = current_reading_pointer
                    action_key = (analyzer_current_state, machine_list[state_idx].name)
                    action_found = True
                    break
            if action_found:
                break
        current_reading_pointer += 1
        current_states = new_states
    if new_states_is_empty or current_reading_pointer == len(input_stream):
        if start_pointer > last_found_pointer:
            print(input_stream[start_pointer], file=sys.stderr, end='')
            start_pointer += 1
            current_reading_pointer = start_pointer
        else:
            action = actions.get(action_key)
            number_of_chars = None
            current_line = line
            for argument in action:
                if argument == 'NOVI_REDAK':
                    line += 1
                elif 'UDJI_U_STANJE' in argument:
                    analyzer_current_state = argument.split(' ')[1]
                elif 'VRATI_SE' in argument:
                    number_of_chars = int(argument.split(' ')[1])
            if number_of_chars is None:
                found_sequence = input_stream[start_pointer: last_found_pointer + 1]
                start_pointer = last_found_pointer + 1
                current_reading_pointer = start_pointer
            else:
                found_sequence = input_stream[start_pointer: start_pointer + number_of_chars]
                start_pointer = start_pointer + number_of_chars
                last_found_pointer = start_pointer - 1
                current_reading_pointer = start_pointer
            if action[0] != '-':
                print(f'{action[0]} {line} {found_sequence}')
        current_states = starting_states
