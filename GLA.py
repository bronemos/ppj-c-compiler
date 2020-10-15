import sys
import re


def new_state(machine):
    machine.states_number = machine.states_number + 1
    return machine.states_number - 1


def is_operator(expression, position):
    num = 0
    while position - 1 >= 0 and expression[position - 1] == '\\':
        num = num + 1
        position = position - 1
    return num % 2 == 0


def convert_expression_to_machine(expression, machine):
    choices = []
    brackets_num = 0
    last_choice_operator_index = -1
    for i in range(0, len(expression)):
        if expression[i] == '(' and is_operator(expression, i):
            brackets_num = brackets_num + 1
        elif expression[i] == ')' and is_operator(expression, i):
            brackets_num = brackets_num - 1
        elif brackets_num == 0 and expression[i] == '|' and is_operator(expression, i):
            choices += expression[last_choice_operator_index + 1: i]
            last_choice_operator_index = i
            # grupiraj lijevi negrupirani dio niza znakova expression u niz izbori

    left_state = new_state(machine)
    right_state = new_state(machine)
    if last_choice_operator_index != -1:
        choices += expression[last_choice_operator_index + 1:]
        for i in range(0, len(choices)):
            temporary = convert_expression_to_machine(choices[i], machine)
            # dodaj_epsilon_prijelaz(machine, left_state, temporary[0])
            print('{},$->{}'.format(left_state, temporary[0]))
            # dodaj_epsilon_prijelaz(machine, temporary[1], right_state)
            print('{},$->{}'.format(temporary[1], right_state))

    else:
        prefixed = False
        last_state = left_state
        i = 0
        while i < len(expression):
            if prefixed:
                prefixed = False
                if expression[i] == 't':
                    transition_char = '\t'
                elif expression[i] == 'n':
                    transition_char = '\n'
                elif expression[i] == '_':
                    transition_char = ' '
                else:
                    transition_char = expression[i]

                a = new_state(machine)
                b = new_state(machine)
                # dodaj_prijelaz(machine, a, b, transition_char)
                print('{},{}->{}'.format(a, transition_char, b))
            else:
                if expression[i] == '\\':
                    prefixed = True
                    continue
                if expression[i] != '(':
                    a = new_state(machine)
                    b = new_state(machine)
                    if expression[i] == '$':
                        # dodaj_epsilon_prijelaz(machine, a, b)
                        print('{},{}->{}'.format(a, '$', b))
                    else:
                        # dodaj_prijelaz(machine, a, b, expression[i])
                        print('{},{}->{}'.format(a, expression[i], b))
                else:
                    # *pronađi odgovarajuću zatvorenu zagradu*
                    brackets_num = 1
                    j = i + 1
                    for k in range(i + 1, len(expression)):
                        if expression[k] == '(' and is_operator(expression, k):
                            brackets_num = brackets_num + 1
                        elif expression[k] == ')' and is_operator(expression, k):
                            brackets_num = brackets_num - 1
                        if brackets_num == 0:
                            j = k
                            break
                    temporary = convert_expression_to_machine(expression[i + 1: j], machine)
                    a = temporary[0]
                    b = temporary[1]
                    i = j

            # check repeat operator
            if i + 1 < len(expression) and expression[i + 1] == '*':
                x = a
                y = b
                a = new_state(machine)
                b = new_state(machine)
                # dodaj_epsilon_prijelaz(machine, a, x)
                print('{},{}->{}'.format(a, '$', x))
                # dodaj_epsilon_prijelaz(machine, y, b)
                print('{},{}->{}'.format(y, '$', b))
                # dodaj_epsilon_prijelaz(machine, a, b)
                print('{},{}->{}'.format(a, '$', b))
                # dodaj_epsilon_prijelaz(machine, y, x)
                print('{},{}->{}'.format(y, '$', x))
                i = i + 1

            # connect to the machine
            # dodaj_epsilon_prijelaz(machine, last_state, a)
            print('{},{}->{}'.format(last_state, '$', a))
            last_state = b
            i += 1
        # dodaj_epsilon_prijelaz(machine, last_state, right_state)
        print('{},{}->{}'.format(last_state, '$', right_state))

    return left_state, right_state


class Machine:
    def __init__(self, name):
        self.name = name
        self.states_number = 0


# filtriramo regexe
# for petlja po svim regexima
# pozove se convert_expression_to_machine za expression (on odmah pise u datoteku)
# nakon svih prijelaza napise se prvo pocetno pa prihvatljivo stanje u datoteku
# u datoteku se upise i ime automata (regex) da bi se moglo prepoznati kojem automatu pripada akcija

# akcije u dict: key: (ime automata (regex), stanje leksera) value: akcija

std_input = sys.stdin.readlines()
data = [x.strip() for x in std_input]
regexes = dict()
passed = False
after_whitespace = re.compile('\\s(.*)')
curly_braces = re.compile('{(.+?)}')

# extract regexes into dict
for x in data:
    if re.search('%X', x):
        break
    try:
        name = curly_braces.search(x).group(1)
        regex = after_whitespace.search(x).group(1)
        for key in regexes.keys():
            regex = regex.replace(f'{{{key}}}', f'({regexes[key]})')
        regexes[name] = regex
    except AttributeError:
        pass

# replaces regexes

passed = False
for idx, x in enumerate(data):
    if re.search('%X', x):
        passed = True
    if not passed:
        try:
            former = after_whitespace.search(x).group(1)
            latter = regexes[curly_braces.search(x).group(1)]
            data[idx] = x.replace(former, latter)
        except AttributeError:
            pass

    elif passed:
        try:
            matches = curly_braces.findall(x)
            for match in matches:
                x = x.replace(f'{{{key}}}', f'({regexes[key]})')
            data[idx] = x
        except AttributeError:
            pass

for x in data:
    print(x)

# m = Machine('(a|b)*abb')
# a = convert_expression_to_machine('(a|b)*abb', m)
# print('{}, {}, {}'.format(a[0], a[1], m.states_number))
