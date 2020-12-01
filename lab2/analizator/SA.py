import sys
import pickle as serializer

testing = True

if not testing:
    with open('actions.txt', 'rb') as f:
        action: dict = serializer.load(f)
    with open('new_state.txt', 'rb') as f:
        new_state: dict = serializer.load(f)

input_list = [(x[0], int(x[1]), ' '.join(x[2:])) for x in [row.strip().split(' ') for row in sys.stdin.readlines()]]

stack = [0]
current_symbol = input_list.pop(0)
while len(input_list) > 0:
    current_state = stack[len(stack) - 1]
    if action[(current_state, current_symbol)][0]:
        stack.append((current_symbol, False))
        stack.append(action[(current_state, current_symbol)][1])
        current_symbol = input_list.pop(0)
    elif not action[(current_state, current_symbol)][0]:
        pass

print(input_list)
