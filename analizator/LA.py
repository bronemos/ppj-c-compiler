import sys


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
            for newState in transitions[(state, '$')]:
                wasInSet = newState in states_set
                if not wasInSet:
                    states_set.add(newState)
                    helper_list.append(newState)
        index += 1
    states_set.discard('#')
    if len(states_set) == 0:
        states_set.add('#')
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
        input_char = data[i].split('->')[0].split(',')[1]
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
actions = {}
# for i in range(actions_start_index, len(data)):
#     pass
#     # TODO: read actions

# variables taken from book
start_pointer = 0
last_found_pointer = 0
current_reading_pointer = 0
input_stream = '0xaaa'  # ''.join(sys.stdin.readlines())
analyzer_current_state = analyzer_starting_state
machine_in_acceptable_state_index_set = set()  # set that contains index for every machine that is in acceptable state

# list containing set of states for each machine
current_states = []
for i in range(len(machine_list)):
    current_states.append(set())
    current_states[i].add(machine_list[i].first_state)
    current_states[i] = updateSetE(current_states[i], machine_list[i].transitions)
starting_states = current_states

while current_reading_pointer < len(input_stream):
    new_states = [set() for x in range(len(machine_list))]
    new_states_is_empty = True

    for i in range(len(machine_list)):
        for state in current_states[i]:
            if (state, input_stream[current_reading_pointer]) in machine_list[i].transitions:
                for new_state in machine_list[i].transitions[(state, input_stream[current_reading_pointer])]:
                    new_states_is_empty = False
                    new_states[i].add(new_state)
        new_states[i] = updateSetE(new_states[i], machine_list[i].transitions)

    if not new_states_is_empty:
        # if new states were added check which machines are in acceptable state
        for i in range(len(machine_list)):
            for state in new_states[i]:
                if state == machine_list[i].acceptable_state:
                    machine_in_acceptable_state_index_set.add(i)
        # TODO: check which action is first for analyzer_current_state and any of machines in set
        # if action_exists:
        #     last_found_pointer = current_reading_pointer
        current_reading_pointer += 1
        current_states = new_states
    else:
        if start_pointer >= last_found_pointer:
            print(input_stream[start_pointer], end='')
            start_pointer += 1
            current_reading_pointer = start_pointer
        else:
            found_sequence = input_stream[start_pointer: last_found_pointer + 1]
            # TODO: start action and maybe change pointers below in action
            start_pointer = last_found_pointer + 1
            current_reading_pointer = start_pointer
        current_states = starting_states
