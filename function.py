import sys
import re

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


