import sys
import pickle as serializer


class Node:

    def __init__(self, data):
        self.data = data
        self.children = []


def dfs_print(root: Node, prefix='', is_root=True):
    if root:
        if not is_root:
            if root.data[1] is True:
                print(prefix + '<' + root.data[0] + '>')
            else:
                print(prefix + ' '.join(root.data))
            prefix = prefix + ' '
        for child in root.children:
            dfs_print(child, prefix, is_root=False)


with open('actions.txt', 'rb') as f:
    action: dict = serializer.load(f)
with open('new_state.txt', 'rb') as f:
    new_state: dict = serializer.load(f)
with open('synchronization.txt', 'rb') as f:
    synchronization_symbols: list = serializer.load(f)

# print(synchronization_symbols)
# print(action)

# input_list - tuple (symbol, row,
input_list = [(x[0], x[1], ' '.join(x[2:])) for x in [row.strip().split(' ') for row in sys.stdin.readlines()]]
input_list.append(('#'))
# print(input_list)
# print(f'action: {action}')
# print(f'new_state: {new_state}')
generative_tree = dict()

stack = [0]
current_symbol = input_list.pop(0)
while True:
    # print(current_symbol)
    current_state = stack[len(stack) - 1]
    if type(current_state) == Node and current_state.data == ('%', True):
        break

    # error handling
    try:
        action[(current_state, current_symbol[0])]
    except KeyError:
        # TODO poboljsati ispis greske, popraviti generativno stablo prilikom greske
        print(f'Error!\n{current_symbol}', file=sys.stderr)
        current_symbol = input_list.pop(0)
        while len(input_list) > 0 and input_list[0][0] not in synchronization_symbols:
            current_symbol = input_list.pop(0)
        # potential issue with stack being empty
        while (current_state, current_symbol[0]) not in action:
            current_state = stack[len(stack) - 1]
            if (current_state, current_symbol[0]) not in action:
                stack.pop()
                stack.pop()
        if len(input_list) == 0:
            break
        continue

    # move and reduce
    if action[(current_state, current_symbol[0])][0]:
        # print(action[(current_state, current_symbol[0])])

        # adds current symbol to stack
        stack.append(Node(current_symbol))
        # adds state to stack
        stack.append(action[(current_state, current_symbol[0])][1])
        current_symbol = input_list.pop(0)
        # print('moving')
    elif not action[(current_state, current_symbol[0])][0]:
        children = list()
        for x in reversed(action[(current_state, current_symbol[0])][2]):
            if len(stack) > 1:
                stack.pop()
                children.append(stack.pop())
        # print(children)
        new_current_state = stack[len(stack) - 1]
        # adds nonterminal to stack
        non_terminal = Node(action[(current_state, current_symbol[0])][1])
        non_terminal.children = children[::-1]
        stack.append(non_terminal)
        if (new_current_state, action[(current_state, current_symbol[0])][1][0]) != (0, '%'):
            stack.append(new_state[(new_current_state, action[(current_state, current_symbol[0])][1][0])])
        elif current_symbol[0] == '#':
            pass
            # print('accepted')
        # print('reducing')
# print(stack)

# dfs preorder generative tree
dfs_print(stack[1])

# print(f'generative tree:', generative_tree)
