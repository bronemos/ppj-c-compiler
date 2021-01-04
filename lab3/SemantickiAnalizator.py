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
        self.function = None  # ako je djelokrug za funkciju treba znati tip fje (identifikator, [lista_arg], pov_vr)

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
    return


def cast_izraz(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])
    name = '<cast_izraz>'

    if right == '<unarni_izraz>':
        return unarni_izraz(node.children[0])

    elif right == 'L_ZAGRADA <ime_tipa> D_ZAGRADA <cast_izraz>':
        cast_type = ime_tipa(node.children[1])  # vraca samo tip
        expression_to_cast_type, _ = cast_izraz(node.children[3])
        if not ('int' in expression_to_cast_type.value or 'char' in expression_to_cast_type.value and
                'int' in cast_type.value or 'char' in cast_type.value):
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


def slozena_naredba(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == 'L_VIT_ZAGRADA <lista_naredbi> D_VIT_ZAGRADA':
        lista_naredbi(node.children[1])

    elif right == 'L_VIT_ZAGRADA <lista_deklaracija> <lista_naredbi> D_VIT_ZAGRADA':
        lista_deklaracija(node.children[1])
        lista_naredbi(node.children[2])

    else:
        pass


def lista_naredbi(node: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<naredba>':
        naredba(node.children[0])

    elif right == '<lista_naredbi> <naredba>':
        lista_naredbi(node.children[0])
        lista_naredbi(node.children[1])

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
    name = '<naredba_skoka'

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
        if 'const' in type_.value:
            terminate(name, node.children)
        # todo
        '''todo 3. ne postoji prije definirana funkcija imena IDN.ime
            4. ako postoji deklaracija imena IDN.ime u globalnom djelokrugu onda je pripadni
            tip te deklaracije funkcija(void → <ime_tipa>.tip)
            5. zabiljeˇzi definiciju i deklaraciju funkcije'''
        slozena_naredba(node.children[5])


    elif right == '<ime_tipa> IDN L_ZAGRADA <lista_parametara> D_ZAGRADA <slozena_naredba>':
        type_ = ime_tipa(node.children[0])
        if 'const' in type_.value:
            terminate(name, node.children)
        # todo
        '''todo 3. ne postoji prije definirana funkcija imena IDN.ime
            4. provjeri(<lista_parametara>)
            5. ako postoji deklaracija imena IDN.ime u globalnom djelokrugu onda je pripadni
            tip te deklaracije funkcija(<lista_parametara>.tipovi → <ime_tipa>.tip)
            6. zabiljeˇzi definiciju i deklaraciju funkcije
            7. provjeri(<slozena_naredba>) uz parametre funkcije koriste´ci <lista_parametara>.tipovi
            i <lista_parametara>.imena.
'''

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
        return type_, #todo provjeriti return

    elif right == '<ime_tipa> IDN L_UGL_ZAGRADA D_UGL_ZAGRADA':
        pass

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
        type_ = izravni_deklarator(node.children[0], inh_property)
        if 'const' in type_.value:
            terminate(name, node.children)

    elif right == '<izravni_deklarator> OP_PRIDRUZI <inicijalizator>':
        type_d, el_count_d = izravni_deklarator(node.children[0], inh_property)
        type_i, el_count_i = inicijalizator(node.children[2])
        if 'array' not in type_d.value and type_d != Type.void:
            if not is_castable(type_i, type_d):
                terminate(name, node.children)
        elif 'array' in type_d.value:
            if not el_count_i <= el_count_d:
                terminate(name, node.children)
            #todo za svaki U iz <inicijalizator>.tipovi vrijedi U ∼ T
        else:
            terminate(name, node.children)

    else:
        pass


def izravni_deklarator(node: Node, inh_property):
    #todo
    name = '<izravni_deklarator>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == 'IDN':
        if inh_property == Type.void:
            terminate(name, node.children)

    elif right == 'IDN L_UGL_ZAGRADA BROJ D_UGL_ZAGRADA':
        if inh_property == Type.void:
            terminate(name, node.children)
        pass

    elif right == 'IDN L_ZAGRADA KR_VOID D_ZAGRADA':
        pass

    elif right == 'IDN L_ZAGRADA <lista_parametara> D_ZAGRADA':
        pass

    else:
        pass


def inicijalizator(node: Node):
    name = '<inicijalizator>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<izraz_pridruzivanja>':
        pass

    elif right == 'L_VIT_ZAGRADA <lista_izraza_pridruzivanja> D_VIT_ZAGRADA':
        pass

    else:
        pass


def lista_izraza_pridruzivanja(node: Node):
    name = '<lista_izraza_pridruzivanja>'
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children])

    if right == '<izraz_pridruzivanja>':
        pass

    elif right == '<lista_izraza_pridruzivanja> ZAREZ <izraz_pridruzivanja>':
        pass

    else:
        pass


tree_list = sys.stdin.read().splitlines()

root = Node(tree_list[0])

fill_tree(root, tree_list)

dfs_print(root)
