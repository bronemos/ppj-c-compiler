from __future__ import annotations

import sys
from collections import defaultdict

from DataTypes import *


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

    def __init__(self, parent: Node = None, ):
        self.parent = parent
        self.children = []
        self.vars = {}  # ime -> tip
        self.declarations = {}  # ime -> ([arg1, arg2, ...] ili void, povratna_vr)
        if parent is None:
            self.definitions = {}  # ime -> ([arg1, arg2, ...] ili void, povratna_vr)
        self.function = ()  # ako je djelokrug za funkciju treba znati tip fje (identifikator, [lista_arg], pov_vr)

    def search(self, identifier):
        node = self
        x = None
        while node is not None:
            if x := node.vars.get(identifier) is not None:
                break
            if x := node.declarations.get(identifier) is not None:
                break
            node = node.parent
        return x


data_table = TableNode()
all_declarations = defaultdict(list)


# ime -> [([arg1, arg2, ...] ili void, povratna_vr), ...] jedna deklaracija moze imati vise tipova (radi provjere fje kasnije)

def terminate(name: str, children: list):
    print(f'{name} ::= {" ".join(children)}')
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
                parent.children.append(Node(tuple(node_data.split(' ')), parent, True))
            parent = parent.children[-1]
        else:
            while space_count <= previous_space_count:
                parent = parent.parent
                previous_space_count -= 1
            if non_terminal.match(node_data):
                parent.children.append(Node(node_data, parent))
            else:
                parent.children.append(Node(tuple(node_data.split(' ')), parent, True))
            parent = parent.children[-1]

        previous_space_count = space_count


def primarni_izraz(node: Node):
    name = '<primarni_izraz>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == 'IDN':
        child = node.children[0]
        if data := data_table.search(child.data[2]) is None:
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
        return Type.char, False

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
        if len(function_type[0]) != len(arg_types):
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
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == 'PLUS':
        pass
    elif right == 'MINUS':
        pass
    elif right == 'OP_TILDA':
        pass
    elif right == 'OP_NEG':
        pass
    else:
        pass


def cast_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<unarni_izraz>':
        return unarni_izraz(node.children[0])
    elif right == 'L_ZAGRADA <ime_tipa> D_ZAGRADA <cast_izraz>':
        ime_tipa(node.children[1])
        cast_izraz(node.children[3])
        # todo return
    else:
        pass


def ime_tipa(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<specifikator_tipa>':
        return specifikator_tipa(node.children[0])
    elif right == 'KR_CONST <specifikator_tipa>':
        pass
    else:
        pass


def specifikator_tipa(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == 'KR_VOID':
        pass
    elif right == 'KR_CHAR':
        pass
    elif right == 'KR_INT':
        pass
    else:
        pass


def multiplikativni_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<cast_izraz>':
        pass
    elif right == '<multiplikativni_izraz> OP_PUTA <cast_izraz>':
        pass
    elif right == '<multiplikativni_izraz> OP_DIJELI <cast_izraz>':
        pass
    elif right == '<multiplikativni_izraz> OP_MOD <cast_izraz>':
        pass


def aditivni_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<multiplikativni_izraz>':
        pass
    elif right == '<aditivni_izraz> PLUS <multiplikativni_izraz>':
        pass
    elif right == '<aditivni_izraz> MINUS <multiplikativni_izraz>':
        pass
    else:
        pass


def odnosni_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<aditivni_izraz>':
        pass
    elif right == '<odnosni_izraz> OP_LT <aditivni_izraz>':
        pass
    elif right == '<odnosni_izraz> OP_GT <aditivni_izraz>':
        pass
    elif right == '<odnosni_izraz> OP_LTE <aditivni_izraz>':
        pass
    elif right == '<odnosni_izraz> OP_GTE <aditivni_izraz>':
        pass
    else:
        pass


def jednakosni_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<odnosni_izraz>':
        pass
    elif right == '<jednakosni_izraz> OP_EQ <odnosni_izraz>':
        pass
    elif right == '<jednakosni_izraz> OP_NEQ <odnosni_izraz>':
        pass


def bin_i_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<jednakosni_izraz>':
        pass
    elif right == '<bin_i_izraz> OP_BIN_I <jednakosni_izraz>':
        pass
    else:
        pass


def bin_xili_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<bin_i_izraz>':
        pass
    elif right == '<bin_xili_izraz> OP_BIN_XILI <bin_i_izraz>':
        pass
    else:
        pass


def bin_ili_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<bin_xili_izraz>':
        pass
    elif right == '<bin_ili_izraz> OP_BIN_ILI <bin_xili_izraz>':
        pass
    else:
        pass


def log_i_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<bin_ili_izraz>':
        pass
    elif right == '<log_i_izraz> OP_I <bin_ili_izraz>':
        pass
    else:
        pass


def log_ili_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<log_i_izraz>':
        pass
    elif right == '<log_ili_izraz> OP_ILI <log_i_izraz>':
        pass
    else:
        pass


def izraz_pridruzivanja(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<log_ili_izraz>':
        pass
    elif right == '<postfiks_izraz> OP_PRIDRUZI <izraz_pridruzivanja>':
        pass


def izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<izraz_pridruzivanja>':
        pass
    elif right == '<izraz> ZAREZ <izraz_pridruzivanja>':
        pass
    else:
        pass


def slozena_naredba(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == 'L_VIT_ZAGRADA <lista_naredbi> D_VIT_ZAGRADA':
        pass
    elif right == 'L_VIT_ZAGRADA <lista_deklaracija> <lista_naredbi> D_VIT_ZAGRADA':
        pass
    else:
        pass


def lista_naredbi(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<naredba>':
        pass
    elif right == '<lista_naredbi> <naredba>':
        pass
    else:
        pass


def naredba(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<slozena_naredba>':
        pass
    elif right == '<izraz_naredba>':
        pass
    elif right == '<naredba_grananja>':
        pass
    elif right == '<naredba_petlje>':
        pass
    elif right == '<naredba_skoka>':
        pass
    else:
        pass


def izraz_naredba(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == 'TOCKAZAREZ':
        pass
    elif right == '<izraz> TOCKAZAREZ':
        pass
    else:
        pass


def naredba_grananja(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == 'KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba>':
        pass
    elif right == 'KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba> KR_ELSE <naredba>':
        pass
    else:
        pass


def naredba_petlje(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == 'KR_WHILE L_ZAGRADA <izraz> D_ZAGRADA <naredba>':
        pass
    elif right == 'KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> D_ZAGRADA <naredba>':
        pass
    elif right == 'KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> <izraz> D_ZAGRADA <naredba>':
        pass
    else:
        pass


def naredba_skoka(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == 'KR_CONTINUE TOCKAZAREZ':
        pass
    elif right == 'KR_BREAK TOCKAZAREZ':
        pass
    elif right == 'KR_RETURN TOCKAZAREZ':
        pass
    elif right == 'KR_RETURN <izraz> TOCKAZAREZ':
        pass
    else:
        pass


def prijevodna_jedinica(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<vanjska_deklaracija>':
        pass
    elif right == '<prijevodna_jedinica> <vanjska_deklaracija>':
        pass
    else:
        pass


def vanjska_deklaracija(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<definicija_funkcije>':
        pass
    elif right == '<deklaracija>':
        pass
    else:
        pass


def definicija_funkcije(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<ime_tipa> IDN L_ZAGRADA KR_VOID D_ZAGRADA <slozena_naredba>':
        pass
    elif right == '<ime_tipa> IDN L_ZAGRADA <lista_parametara> D_ZAGRADA <slozena_naredba>':
        pass
    else:
        pass


def lista_parametara(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<deklaracija_parametra>':
        pass
    elif right == '<lista_parametara> ZAREZ <deklaracija_parametra>':
        pass
    else:
        pass


def deklaracija_parametra(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<ime_tipa> IDN':
        pass
    elif right == '<ime_tipa> IDN L_UGL_ZAGRADA D_UGL_ZAGRADA':
        pass
    else:
        pass


def lista_deklaracija(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<deklaracija>':
        pass
    elif right == '<lista_deklaracija> <deklaracija>':
        pass
    else:
        pass


def deklaracija(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<ime_tipa> <lista_init_deklaratora> TOCKAZAREZ':
        pass
    else:
        pass


def lista_init_deklaratora(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<init_deklarator>':
        pass
    elif right == '<lista_init_deklaratora> ZAREZ <init_deklarator>':
        pass
    else:
        pass


def init_deklarator(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<izravni_deklarator>':
        pass
    elif right == '<izravni_deklarator> OP_PRIDRUZI <inicijalizator>':
        pass
    else:
        pass


def izravni_deklarator(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == 'IDN':
        pass
    elif right == 'IDN L_UGL_ZAGRADA BROJ D_UGL_ZAGRADA':
        pass
    elif right == 'IDN L_ZAGRADA KR_VOID D_ZAGRADA':
        pass
    elif right == 'IDN L_ZAGRADA <lista_parametara> D_ZAGRADA':
        pass
    else:
        pass


def inicijalizator(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<izraz_pridruzivanja>':
        pass
    elif right == 'L_VIT_ZAGRADA <lista_izraza_pridruzivanja> D_VIT_ZAGRADA':
        pass
    else:
        pass


def lista_izraza_pridruzivanja(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    if right == '<izraz_pridruzivanja>':
        pass
    elif right == '<lista_izraza_pridruzivanja> ZAREZ <izraz_pridruzivanja>':
        pass


tree_list = sys.stdin.read().splitlines()

root = Node(tree_list[0])

fill_tree(root, tree_list)

dfs_print(root)
