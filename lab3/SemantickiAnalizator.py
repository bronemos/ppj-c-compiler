from __future__ import annotations

import sys
import re
from collections import defaultdict

from DataTypes import *

string_re = re.compile(r'^\".*\"')
char_array_re = re.compile(r'^{\s(\'.*\'(\s|,\s))*}$')
int_re = re.compile(r'^{\s(\d*(\s|,\s))*}$')


class Node:

    def __init__(self, data, parent: Node = None, is_terminal: bool = False):
        self.is_terminal = is_terminal
        self.parent = parent
        self.data = data
        self.children = []

    def __str__(self):
        if self.is_terminal:
            return f'{self.data[0]}({self.data[1]},{self.data[2]})'
        else:
            return self.data


class TableNode:

    def __init__(self, parent: TableNode = None):
        self.parent = parent
        self.children = []
        self.vars = {}  # ime -> tip
        self.declarations = {}  # ime -> ([arg1, arg2, ...] ili void, povratna_vr)
        if parent is None:
            self.definitions = {}  # ime -> ([arg1, arg2, ...] ili void, povratna_vr)
        self.function = None  # ako je djelokrug za funkciju treba znati tip fje (identifikator, [lista_arg], pov_vr)

    def search(self, identifier):
        node = self
        x = None
        while node is not None:
            if (x := node.vars.get(identifier)) is not None:
                break
            if (x := node.declarations.get(identifier)) is not None:
                break
            node = node.parent
        return x


data_table = global_data_table = TableNode()
all_declarations = defaultdict(list)


# ime -> [([arg1, arg2, ...] ili void, povratna_vr), ...] jedna deklaracija moze imati vise tipova (radi provjere fje kasnije)

def terminate(name: str, children: list):
    string = f'{name} ::='
    for child in children:
        if type(child.data) is tuple:
            string += f' {child.data[0]}({child.data[1]},{child.data[2]})'
        else:
            string += f' {child.data}'
    print(string)
    exit(0)


def dfs_print(root_: Node, prefix=''):
    if root_:
        if root_.is_terminal:
            print(prefix + ' '.join(root_.data))
        else:
            print(prefix + root_.data)
        prefix = prefix + ' '
    for child in root_.children:
        dfs_print(child, prefix)


def fill_tree(parent: Node, tree_list: list):
    previous_space_count = -1
    pattern = re.compile(r'^(\s*)(.*)$')
    non_terminal = re.compile(r'^<(.*)>$')

    for node in tree_list[1:]:
        match = pattern.match(node)
        space_count = len(match.group(1))
        node_data = match.group(2)
        if space_count > previous_space_count:
            if non_terminal.match(node_data):
                parent.children.append(Node(node_data, parent))
            else:
                node_data_tuple = (node_data.split(' ')[0], node_data.split(' ')[1], ' '.join(node_data.split(' ')[2:]))
                parent.children.append(Node(node_data_tuple, parent, True))
            parent = parent.children[-1]
        else:
            while space_count <= previous_space_count:
                parent = parent.parent
                previous_space_count -= 1
            if non_terminal.match(node_data):
                parent.children.append(Node(node_data, parent))
            else:
                node_data_tuple = (node_data.split(' ')[0], node_data.split(' ')[1], ' '.join(node_data.split(' ')[2:]))
                parent.children.append(Node(node_data_tuple, parent, True))
            parent = parent.children[-1]

        previous_space_count = space_count


def primarni_izraz(node: Node):
    name = '<primarni_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == 'IDN':
        child = node.children[0]
        if (data := data_table.search(child.data[2])) is None:
            terminate(name, node.children)
        # data: (tip za var, za fju touple ([lista_argumenata], povratna_vrijednost)}
        return data, is_l_expression(data)

    elif right == 'BROJ':
        child = node.children[0]
        if not is_int(child.data[2]):
            terminate(name, node.children)
        return Type.int, False

    elif right == 'ZNAK':
        child = node.children[0]
        if not is_char(child.data[2]):
            terminate(name, node.children)
        return Type.char, False

    elif right == 'NIZ_ZNAKOVA':
        child = node.children[0]
        if not is_const_char_array(child.data[2]):
            terminate(name, node.children)
        return Type.const_char_array, False

    elif right == 'L_ZAGRADA <izraz> D_ZAGRADA':
        return izraz(node.children[1])

    else:
        pass


def postfiks_izraz(node: Node):
    name = '<postfiks_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<primarni_izraz>':
        return primarni_izraz(node.children[0])

    elif right == '<postfiks_izraz> L_UGL_ZAGRADA <izraz> D_UGL_ZAGRADA':
        type_postfix, _ = postfiks_izraz(node.children[0])
        if 'array' not in type_postfix.value:
            terminate(name, node.children)
        type_izraz, _ = izraz(node.children[2])
        if not is_castable(type_izraz, Type.int):
            terminate(name, node.children)
        type_ = array_to_single(type_postfix)
        return type_, is_l_expression(type_)

    elif right == '<postfiks_izraz> L_ZAGRADA D_ZAGRADA':
        function_type, _ = postfiks_izraz(node.children[0])
        if function_type[0] != Type.void:
            terminate(name, node.children)
        return function_type[1], False

    elif right == '<postfiks_izraz> L_ZAGRADA <lista_argumenata> D_ZAGRADA':
        function_type, _ = postfiks_izraz(node.children[0])
        arg_types = lista_argumenata(node.children[2])
        if function_type[0] == Type.void or len(function_type[0]) != len(arg_types):
            terminate(name, node.children)
        for index, arg_type in enumerate(arg_types):
            if not is_castable(arg_type, function_type[0][index]):
                terminate(name, node.children)
        return function_type[1], False

    elif right == '<postfiks_izraz> OP_INC' or right == '<postfiks_izraz> OP_DEC':
        type_, l_expression = postfiks_izraz(node.children[0])
        if not (is_castable(type_, Type.int) and l_expression):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def lista_argumenata(node: Node):
    name = '<lista_argumenata>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<izraz_pridruzivanja>':
        return [izraz_pridruzivanja(node.children[0])[0]]

    elif right == '<lista_argumenata> ZAREZ <izraz_pridruzivanja>':
        return lista_argumenata(node.children[0]) + [izraz_pridruzivanja(node.children[2])[0]]

    else:
        pass


def unarni_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    name = '<unarni_izraz>'

    if right == '<postfiks_izraz>':
        return postfiks_izraz(node.children[0])

    elif right == 'OP_INC <unarni_izraz>' or right == 'OP_DEC <unarni_izraz>':
        type_, l_expression = unarni_izraz(node.children[1])
        if not (l_expression and is_castable(type_, Type.int)):
            terminate(name, node.children)
        return Type.int, False

    elif right == '<unarni_operator> <cast_izraz>':
        type_, _ = cast_izraz(node.children[1])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def unarni_operator(node: Node):
    return


def cast_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    name = '<cast_izraz>'

    if right == '<unarni_izraz>':
        return unarni_izraz(node.children[0])

    elif right == 'L_ZAGRADA <ime_tipa> D_ZAGRADA <cast_izraz>':
        cast_type = ime_tipa(node.children[1])  # vraca samo tip
        expression_to_cast_type, _ = cast_izraz(node.children[3])
        if type(expression_to_cast_type) is tuple:
            terminate(name, node.children)
        if not (('int' in expression_to_cast_type.value or 'char' in expression_to_cast_type.value) and
                ('int' in cast_type.value or 'char' in cast_type.value)) or \
                'array' in expression_to_cast_type.value or 'array' in cast_type.value:
            terminate(name, node.children)
        return cast_type, False

    else:
        pass


def ime_tipa(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    name = '<ime_tipa>'

    if right == '<specifikator_tipa>':
        return specifikator_tipa(node.children[0])

    elif right == 'KR_CONST <specifikator_tipa>':
        type_ = specifikator_tipa(node.children[1])
        if type_ == Type.void:
            terminate(name, node.children)
        return convert_to_const(type_)

    else:
        pass


def specifikator_tipa(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == 'KR_VOID':
        return Type.void
    elif right == 'KR_CHAR':
        return Type.char
    elif right == 'KR_INT':
        return Type.int
    else:
        pass


def multiplikativni_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    name = '<multiplikativni_izraz>'

    if right == '<cast_izraz>':
        return cast_izraz(node.children[0])

    elif (right == '<multiplikativni_izraz> OP_PUTA <cast_izraz>'
          or right == '<multiplikativni_izraz> OP_DIJELI <cast_izraz>'
          or right == '<multiplikativni_izraz> OP_MOD <cast_izraz>'):

        type_m, _ = multiplikativni_izraz(node.children[0])
        type_c, _ = cast_izraz(node.children[2])
        if not (is_castable(type_m, Type.int) and is_castable(type_c, Type.int)):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def aditivni_izraz(node: Node):
    name = '<aditivni_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<multiplikativni_izraz>':
        return multiplikativni_izraz(node.children[0])

    elif (right == '<aditivni_izraz> PLUS <multiplikativni_izraz>'
          or right == '<aditivni_izraz> MINUS <multiplikativni_izraz>'):
        type_, _ = aditivni_izraz(node.children[0])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        type_, _ = multiplikativni_izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def odnosni_izraz(node: Node):
    name = '<odnosni_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<aditivni_izraz>':
        return aditivni_izraz(node.children[0])

    elif (right == '<odnosni_izraz> OP_LT <aditivni_izraz>'
          or right == '<odnosni_izraz> OP_GT <aditivni_izraz>'
          or right == '<odnosni_izraz> OP_LTE <aditivni_izraz>'
          or right == '<odnosni_izraz> OP_GTE <aditivni_izraz>'):
        type_, _ = odnosni_izraz(node.children[0])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        type_, _ = aditivni_izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def jednakosni_izraz(node: Node):
    name = '<jednakosni_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<odnosni_izraz>':
        return odnosni_izraz(node.children[0])

    elif (right == '<jednakosni_izraz> OP_EQ <odnosni_izraz>'
          or right == '<jednakosni_izraz> OP_NEQ <odnosni_izraz>'):
        type_, _ = jednakosni_izraz(node.children[0])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        type_, _ = odnosni_izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def bin_i_izraz(node: Node):
    name = '<bin_i_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<jednakosni_izraz>':
        return jednakosni_izraz(node.children[0])

    elif right == '<bin_i_izraz> OP_BIN_I <jednakosni_izraz>':
        type_, _ = bin_i_izraz(node.children[0])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        type_, _ = jednakosni_izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def bin_xili_izraz(node: Node):
    name = '<bin_xili_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<bin_i_izraz>':
        return bin_i_izraz(node.children[0])

    elif right == '<bin_xili_izraz> OP_BIN_XILI <bin_i_izraz>':
        type_, _ = bin_xili_izraz(node.children[0])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        type_, _ = bin_i_izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def bin_ili_izraz(node: Node):
    name = '<bin_ili_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<bin_xili_izraz>':
        return bin_xili_izraz(node.children[0])

    elif right == '<bin_ili_izraz> OP_BIN_ILI <bin_xili_izraz>':
        type_, _ = bin_ili_izraz(node.children[0])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        type_, _ = bin_xili_izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def log_i_izraz(node: Node):
    name = '<log_i_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<bin_ili_izraz>':
        return bin_ili_izraz(node.children[0])

    elif right == '<log_i_izraz> OP_I <bin_ili_izraz>':
        type_, _ = log_i_izraz(node.children[0])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        type_, _ = bin_ili_izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def log_ili_izraz(node: Node):
    name = '<log_ili_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<log_i_izraz>':
        return log_i_izraz(node.children[0])

    elif right == '<log_ili_izraz> OP_ILI <log_i_izraz>':
        type_, _ = log_ili_izraz(node.children[0])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        type_, _ = log_i_izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        return Type.int, False

    else:
        pass


def izraz_pridruzivanja(node: Node):
    name = '<izraz_pridruzivanja>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<log_ili_izraz>':
        return log_ili_izraz(node.children[0])

    elif right == '<postfiks_izraz> OP_PRIDRUZI <izraz_pridruzivanja>':
        type_post, l_expression = postfiks_izraz(node.children[0])
        if not l_expression:
            terminate(name, node.children)
        type_prid, _ = izraz_pridruzivanja(node.children[2])
        if not is_castable(type_prid, type_post):
            terminate(name, node.children)
        return type_post, False


def izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<izraz_pridruzivanja>':
        return izraz_pridruzivanja(node.children[0])

    elif right == '<izraz> ZAREZ <izraz_pridruzivanja>':
        izraz(node.children[0])
        type_, _ = izraz_pridruzivanja(node.children[2])
        return type_, False

    else:
        pass


def slozena_naredba(node: Node, function=None, params_types=None, params_names=None):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    global data_table
    old_function = data_table.function
    new_node = TableNode(parent=data_table)
    data_table.children.append(new_node)
    data_table = new_node

    if function is not None:
        data_table.function = function
    else:
        data_table.function = old_function

    if params_names is not None:
        for index, name in enumerate(params_names):
            data_table.vars[name] = params_types[index]

    if right == 'L_VIT_ZAGRADA <lista_naredbi> D_VIT_ZAGRADA':
        lista_naredbi(node.children[1])
        data_table = data_table.parent

    elif right == 'L_VIT_ZAGRADA <lista_deklaracija> <lista_naredbi> D_VIT_ZAGRADA':
        lista_deklaracija(node.children[1])
        lista_naredbi(node.children[2])
        data_table = data_table.parent

    else:
        pass


def lista_naredbi(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<naredba>':
        naredba(node.children[0])

    elif right == '<lista_naredbi> <naredba>':
        lista_naredbi(node.children[0])
        naredba(node.children[1])

    else:
        pass


def naredba(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<slozena_naredba>':
        slozena_naredba(node.children[0])

    elif right == '<izraz_naredba>':
        izraz_naredba(node.children[0])

    elif right == '<naredba_grananja>':
        naredba_grananja(node.children[0])

    elif right == '<naredba_petlje>':
        naredba_petlje(node.children[0])

    elif right == '<naredba_skoka>':
        naredba_skoka(node.children[0])

    else:
        pass


def izraz_naredba(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == 'TOCKAZAREZ':
        return Type.int

    elif right == '<izraz> TOCKAZAREZ':
        type_, _ = izraz(node.children[0])
        return type_

    else:
        pass


def naredba_grananja(node: Node):
    name = '<naredba_grananja>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == 'KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba>':
        type_, _ = izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        naredba(node.children[4])

    elif right == 'KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba> KR_ELSE <naredba>':
        type_, _ = izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        naredba(node.children[4])
        naredba(node.children[6])

    else:
        pass


def naredba_petlje(node: Node):
    name = '<naredba_petlje>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == 'KR_WHILE L_ZAGRADA <izraz> D_ZAGRADA <naredba>':
        type_, _ = izraz(node.children[2])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        naredba(node.children[4])

    elif right == 'KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> D_ZAGRADA <naredba>':
        izraz_naredba(node.children[2])
        type_ = izraz_naredba(node.children[3])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        naredba(node.children[4])

    elif right == 'KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> <izraz> D_ZAGRADA <naredba>':
        izraz_naredba(node.children[2])
        type_ = izraz_naredba(node.children[3])
        if not is_castable(type_, Type.int):
            terminate(name, node.children)
        izraz(node.children[4])
        naredba(node.children[6])

    else:
        pass


def naredba_skoka(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    name = '<naredba_skoka>'

    if right == 'KR_CONTINUE TOCKAZAREZ' or right == 'KR_BREAK TOCKAZAREZ':
        help_node = node
        while help_node.parent is not None:
            help_node = help_node.parent
            if help_node.data == '<naredba_petlje>':
                return
        terminate(name, node.children)
        return

    elif right == 'KR_RETURN TOCKAZAREZ':
        function = data_table.function
        if not (function is not None and function[2] == Type.void):
            terminate(name, node.children)
        return

    elif right == 'KR_RETURN <izraz> TOCKAZAREZ':
        type_, _ = izraz(node.children[1])
        function = data_table.function
        if not (function is not None and is_castable(type_, function[2])):
            terminate(name, node.children)
        return

    else:
        pass


def prijevodna_jedinica(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<vanjska_deklaracija>':
        vanjska_deklaracija(node.children[0])

    elif right == '<prijevodna_jedinica> <vanjska_deklaracija>':
        prijevodna_jedinica(node.children[0])
        vanjska_deklaracija(node.children[1])

    else:
        pass


def vanjska_deklaracija(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<definicija_funkcije>':
        definicija_funkcije(node.children[0])

    elif right == '<deklaracija>':
        deklaracija(node.children[0])

    else:
        pass


def definicija_funkcije(node: Node):
    name = '<definicija_funkcije>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<ime_tipa> IDN L_ZAGRADA KR_VOID D_ZAGRADA <slozena_naredba>':
        type_ = ime_tipa(node.children[0])
        if global_data_table.vars.get(node.children[1].data[2]) is not None:
            terminate(name, node.children)

        x = global_data_table.declarations.get(node.children[1].data[2])
        if ('const' in type_.value
                or node.children[1].data[2] in global_data_table.definitions.keys()
                or x is not None and
                not (x[0] == Type.void and x[1] == type_)):
            terminate(name, node.children)

        global_data_table.definitions[node.children[1].data[2]] = (Type.void, type_)
        if x is None:
            global_data_table.declarations[node.children[1].data[2]] = (Type.void, type_)
        # all_declarations[node.children[1].data[2]].append((Type.void, type_))
        # ne treba jer je tu sigurno i definirana

        slozena_naredba(node.children[5], function=(node.children[1].data[2], Type.void, type_))

    elif right == '<ime_tipa> IDN L_ZAGRADA <lista_parametara> D_ZAGRADA <slozena_naredba>':
        type_ = ime_tipa(node.children[0])
        if ('const' in type_.value
                or node.children[1].data[2] in global_data_table.definitions.keys()):
            terminate(name, node.children)

        types, names = lista_parametara(node.children[3])

        if global_data_table.vars.get(node.children[1].data[2]) is not None:
            terminate(name, node.children)

        x = global_data_table.declarations.get(node.children[1].data[2])
        if x is not None:
            if not (x[0] == types and x[1] == type_):
                terminate(name, node.children)

        global_data_table.definitions[node.children[1].data[2]] = (types, type_)
        if x is None:
            global_data_table.declarations[node.children[1].data[2]] = (types, type_)
        # all_declarations[node.children[1].data[2]].append((types, type_))
        # ne treba jer je tu sigurno i definirana

        slozena_naredba(
            node.children[5],
            function=(node.children[1].data[2], types, type_),
            params_types=types,
            params_names=names
        )

    else:
        pass


def lista_parametara(node: Node):
    name = '<lista_parametara>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<deklaracija_parametra>':
        type_, name_ = deklaracija_parametra(node.children[0])
        return [type_, ], [name_, ]

    elif right == '<lista_parametara> ZAREZ <deklaracija_parametra>':
        types, names = lista_parametara(node.children[0])
        type_, name_ = deklaracija_parametra(node.children[2])
        if name_ in names:
            terminate(name, node.children)
        return types + [type_, ], names + [name_, ]

    else:
        pass


def deklaracija_parametra(node: Node):
    name = '<deklaracija_parametra>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<ime_tipa> IDN':
        type_ = ime_tipa(node.children[0])
        if type_ == Type.void:
            terminate(name, node.children)
        return type_, node.children[1].data[2]

    elif right == '<ime_tipa> IDN L_UGL_ZAGRADA D_UGL_ZAGRADA':
        type_ = ime_tipa(node.children[0])
        if type_ == Type.void:
            terminate(name, node.children)
        return convert_to_array(type_), node.children[1].data[2]

    else:
        pass


def lista_deklaracija(node: Node):
    name = '<lista_deklaracija>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<deklaracija>':
        deklaracija(node.children[0])

    elif right == '<lista_deklaracija> <deklaracija>':
        lista_deklaracija(node.children[0])
        deklaracija(node.children[1])

    else:
        pass


def deklaracija(node: Node):
    name = '<deklaracija>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<ime_tipa> <lista_init_deklaratora> TOCKAZAREZ':
        type_ = ime_tipa(node.children[0])
        lista_init_deklaratora(node.children[1], type_)

    else:
        pass


def lista_init_deklaratora(node: Node, inh_property):
    name = '<lista_init_deklaratora>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<init_deklarator>':
        init_deklarator(node.children[0], inh_property)

    elif right == '<lista_init_deklaratora> ZAREZ <init_deklarator>':
        lista_init_deklaratora(node.children[0], inh_property)
        init_deklarator(node.children[2], inh_property)

    else:
        pass


def init_deklarator(node: Node, inh_property):
    name = '<init_deklarator>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<izravni_deklarator>':
        type_, _ = izravni_deklarator(node.children[0], inh_property)
        if type(
                type_) is not tuple and 'const' in type_.value:  # TODO treba vidjeti sto s tupleom i na jos dosta mjesta
            terminate(name, node.children)

    elif right == '<izravni_deklarator> OP_PRIDRUZI <inicijalizator>':
        type_d, el_count_d = izravni_deklarator(node.children[0], inh_property)
        type_i, el_count_i = inicijalizator(node.children[2])  # ako je array vraca listu tipova inace samo tip
        if type(type_d) is tuple:  # ako je fja vratit ce tuple
            terminate(name, node.children)
        if 'array' not in type_d.value and type_d != Type.void:
            if not is_castable(type_i, type_d):
                terminate(name, node.children)
        else:  # 'array' in type_d.value:
            if el_count_i is None:
                terminate(name, node.children)
            if not (el_count_i <= el_count_d):
                terminate(name, node.children)
            for type_inicijalizator in type_i:
                if not is_castable(type_inicijalizator, array_to_single(type_d)):
                    terminate(name, node.children)

    else:
        pass


def izravni_deklarator(node: Node, inh_property):
    name = '<izravni_deklarator>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == 'IDN':
        if inh_property == Type.void:
            terminate(name, node.children)
        if not (data_table.vars.get(node.children[0].data[2]) is None and
                data_table.declarations.get(node.children[0].data[2]) is None):
            terminate(name, node.children)
        data_table.vars[node.children[0].data[2]] = inh_property
        return inh_property, None

    elif right == 'IDN L_UGL_ZAGRADA BROJ D_UGL_ZAGRADA':
        if inh_property == Type.void:
            terminate(name, node.children)
        if not (data_table.vars.get(node.children[0].data[2]) is None and
                data_table.declarations.get(node.children[0].data[2]) is None):
            terminate(name, node.children)
        if not (0 < int(node.children[2].data[2]) <= 1024):
            terminate(name, node.children)
        data_table.vars[node.children[0].data[2]] = convert_to_array(inh_property)
        return convert_to_array(inh_property), int(node.children[2].data[2])

    elif right == 'IDN L_ZAGRADA KR_VOID D_ZAGRADA':
        if data_table.vars.get(node.children[0].data[2]) is not None:
            terminate(name, node.children)
        if x := data_table.declarations.get(node.children[0].data[2]) is not None:
            if x != (Type.void, inh_property):
                terminate(name, node.children)
        else:
            data_table.declarations[node.children[0].data[2]] = (Type.void, inh_property)
            all_declarations[node.children[0].data[2]].append((Type.void, inh_property))
        return (Type.void, inh_property), None

    elif right == 'IDN L_ZAGRADA <lista_parametara> D_ZAGRADA':
        types, names = lista_parametara(node.children[2])
        if data_table.vars.get(node.children[0].data[2]) is not None:
            terminate(name, node.children)
        if (x := data_table.declarations.get(node.children[0].data[2])) is not None:
            if x != (types, inh_property):
                terminate(name, node.children)
        else:
            data_table.declarations[node.children[0].data[2]] = (types, inh_property)
            all_declarations[node.children[0].data[2]].append((types, inh_property))
        return (types, inh_property), None

    else:
        pass


def inicijalizator(node: Node):
    name = '<inicijalizator>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<izraz_pridruzivanja>':
        type_, _ = izraz_pridruzivanja(node.children[0])
        help_node = node
        while len(help_node.children) != 0:
            help_node = help_node.children[0]
            if type(help_node.data) is tuple:
                if help_node.data[0] == 'NIZ_ZNAKOVA':
                    string = help_node.data[2]

                    if (str_matched := char_array_re.match(string)) or int_re.match(string):
                        array = eval('[' + string[1:len(string) - 1] + ']')
                        el_count = len(array)
                        if str_matched:
                            if array[-1] != '\\0':
                                el_count += 1

                    elif string_re.match(string):
                        el_count = 0
                        is_prefixed = False
                        for char in string[1:-1]:
                            if char == '\\':
                                is_prefixed = True
                            elif is_prefixed:
                                el_count += 1
                                is_prefixed = False
                            else:
                                el_count += 1

                    else:
                        terminate(name, node.children)

                    types = [Type.char] * el_count
                    return types, el_count
        return type_, None

    elif right == 'L_VIT_ZAGRADA <lista_izraza_pridruzivanja> D_VIT_ZAGRADA':
        return lista_izraza_pridruzivanja(node.children[1])

    else:
        pass


def lista_izraza_pridruzivanja(node: Node):
    name = '<lista_izraza_pridruzivanja>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<izraz_pridruzivanja>':
        return [izraz_pridruzivanja(node.children[0])[0]], 1

    elif right == '<lista_izraza_pridruzivanja> ZAREZ <izraz_pridruzivanja>':
        list_, num = lista_izraza_pridruzivanja(node.children[0])
        new_element = izraz_pridruzivanja(node.children[2])[0]
        return list_ + [new_element], num + 1

    else:
        pass


tree_list = sys.stdin.read().splitlines()

root = Node(tree_list[0])

fill_tree(root, tree_list)

prijevodna_jedinica(root)

if (x := global_data_table.definitions.get('main')) is not None:
    if x != (Type.void, Type.int):
        print('main')
        exit(0)
else:
    print('main')
    exit(0)

for function_name, declaration_list in all_declarations.items():
    x = None
    if (x := global_data_table.definitions.get(function_name)) is None:
        print('funkcija')
        exit(0)
    for declaration in declaration_list:
        if x != declaration:
            print('funkcija')
            exit(0)
