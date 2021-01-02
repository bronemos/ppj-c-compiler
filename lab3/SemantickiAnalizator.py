from __future__ import annotations

import sys
import re


class Node:

    def __init__(self, data, parent: Node = None, is_terminal: bool = False):
        self.is_terminal = is_terminal
        self.parent = parent
        self.data = data
        self.children = []


def dfs_print(root: Node, prefix=''):
    if root:
        if root.is_terminal:
            print(prefix + ' '.join(root.data))
        else:
            print(prefix + root.data)
        prefix = prefix + ' '
    for child in root.children:
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


def primarni_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == 'IDN':
        pass
    elif right == 'BROJ':
        pass
    elif right == 'ZNAK':
        pass
    elif right == 'NIZ_ZNAKOVA':
        pass
    elif right == 'L_ZAGRADA <izraz> D_ZAGRADA':
        pass
    else:
        pass


def postfiks_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<primarni_izraz>':
        pass
    elif right == '<postfiks_izraz> L_UGL_ZAGRADA <izraz> D_UGL_ZAGRADA':
        pass
    elif right == '<postfiks_izraz> L_ZAGRADA D_ZAGRADA':
        pass
    elif right == '<postfiks_izraz> L_ZAGRADA <lista_argumenata> D_ZAGRADA':
        pass
    elif right == '<postfiks_izraz> OP_INC':
        pass
    elif right == '<postfiks_izraz> OP_DEC':
        pass
    else:
        pass


def lista_argumenata(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<izraz_pridruzivanja>':
        pass
    elif right == '<lista_argumenata> ZAREZ <izraz_pridruzivanja>':
        pass
    else:
        pass


def unarni_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<postfiks_izraz>':
        pass
    elif right == 'OP_INC <unarni_izraz>':
        pass
    elif right == 'OP_DEC <unarni_izraz>':
        pass
    elif right == '<unarni_operator> <cast_izraz>':
        pass
    else:
        pass


def unarni_operator(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
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


def cast_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<unarni_izraz>':
        pass
    elif right == 'L_ZAGRADA <ime_tipa> D_ZAGRADA <cast_izraz>':
        pass
    else:
        pass


def ime_tipa(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<specifikator_tipa>':
        pass
    elif right == 'KR_CONST <specifikator_tipa>':
        pass
    else:
        pass


def specifikator_tipa(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == 'KR_VOID':
        pass
    elif right == 'KR_CHAR':
        pass
    elif right == 'KR_INT':
        pass
    else:
        pass


def multiplikativni_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<cast_izraz>':
        pass
    elif right == '<multiplikativni_izraz> OP_PUTA <cast_izraz>':
        pass
    elif right == '<multiplikativni_izraz> OP_DIJELI <cast_izraz>':
        pass
    elif right == '<multiplikativni_izraz> OP_MOD <cast_izraz>':
        pass


def aditivni_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<multiplikativni_izraz>':
        pass
    elif right == '<aditivni_izraz> PLUS <multiplikativni_izraz>':
        pass
    elif right == '<aditivni_izraz> MINUS <multiplikativni_izraz>':
        pass
    else:
        pass


def odnosni_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
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


def jednakosni_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<odnosni_izraz>':
        pass
    elif right == '<jednakosni_izraz> OP_EQ <odnosni_izraz>':
        pass
    elif right == '<jednakosni_izraz> OP_NEQ <odnosni_izraz>':
        pass


def bin_i_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<jednakosni_izraz>':
        pass
    elif right == '<bin_i_izraz> OP_BIN_I <jednakosni_izraz>':
        pass
    else:
        pass


def bin_xili_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<bin_i_izraz>':
        pass
    elif right == '<bin_xili_izraz> OP_BIN_XILI <bin_i_izraz>':
        pass
    else:
        pass


def bin_ili_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<bin_xili_izraz>':
        pass
    elif right == '<bin_ili_izraz> OP_BIN_ILI <bin_xili_izraz>':
        pass
    else:
        pass


def log_i_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<bin_ili_izraz>':
        pass
    elif right == '<log_i_izraz> OP_I <bin_ili_izraz>':
        pass
    else:
        pass


def log_ili_izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<log_i_izraz>':
        pass
    elif right == '<log_ili_izraz> OP_ILI <log_i_izraz>':
        pass
    else:
        pass


def izraz_pridruzivanja(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<log_ili_izraz>':
        pass
    elif right == '<postfiks_izraz> OP_PRIDRUZI <izraz_pridruzivanja>':
        pass


def izraz(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<izraz_pridruzivanja>':
        pass
    elif right == '<izraz> ZAREZ <izraz_pridruzivanja>':
        pass
    else:
        pass


def slozena_naredba(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == 'L_VIT_ZAGRADA <lista_naredbi> D_VIT_ZAGRADA':
        pass
    elif right == 'L_VIT_ZAGRADA <lista_deklaracija> <lista_naredbi> D_VIT_ZAGRADA':
        pass
    else:
        pass


def lista_naredbi(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<naredba>':
        pass
    elif right == '<lista_naredbi> <naredba>':
        pass
    else:
        pass


def naredba(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
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


def izraz_naredba(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == 'TOCKAZAREZ':
        pass
    elif right == '<izraz> TOCKAZAREZ':
        pass
    else:
        pass


def naredba_grananja(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == 'KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba>':
        pass
    elif right == 'KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba> KR_ELSE <naredba>':
        pass
    else:
        pass


def naredba_petlje(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == 'KR_WHILE L_ZAGRADA <izraz> D_ZAGRADA <naredba>':
        pass
    elif right == 'KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> D_ZAGRADA <naredba>':
        pass
    elif right == 'KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> <izraz> D_ZAGRADA <naredba>':
        pass
    else:
        pass


def naredba_skoka(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
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


def prijevodna_jedinica(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<vanjska_deklaracija>':
        pass
    elif right == '<prijevodna_jedinica> <vanjska_deklaracija>':
        pass
    else:
        pass


def vanjska_deklaracija(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<definicija_funkcije>':
        pass
    elif right == '<deklaracija>':
        pass
    else:
        pass


def definicija_funkcije(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<ime_tipa> IDN L_ZAGRADA KR_VOID D_ZAGRADA <slozena_naredba>':
        pass
    elif right == '<ime_tipa> IDN L_ZAGRADA <lista_parametara> D_ZAGRADA <slozena_naredba>':
        pass
    else:
        pass


def lista_parametara(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<deklaracija_parametra>':
        pass
    elif right == '<lista_parametara> ZAREZ <deklaracija_parametra>':
        pass
    else:
        pass


def deklaracija_parametra(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<ime_tipa> IDN':
        pass
    elif right == '<ime_tipa> IDN L_UGL_ZAGRADA D_UGL_ZAGRADA':
        pass
    else:
        pass


def lista_deklaracija(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<deklaracija>':
        pass
    elif right == '<lista_deklaracija> <deklaracija>':
        pass
    else:
        pass


def deklaracija(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<ime_tipa> <lista_init_deklaratora> TOCKAZAREZ':
        pass
    else:
        pass


def lista_init_deklaratora(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<init_deklarator>':
        pass
    elif right == '<lista_init_deklaratora> ZAREZ <init_deklarator>':
        pass
    else:
        pass


def init_deklarator(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<izravni_deklarator>':
        pass
    elif right == '<izravni_deklarator> OP_PRIDRUZI <inicijalizator>':
        pass
    else:
        pass


def izravni_deklarator(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
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


def inicijalizator(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<izraz_pridruzivanja>':
        pass
    elif right == 'L_VIT_ZAGRADA <lista_izraza_pridruzivanja> D_VIT_ZAGRADA':
        pass
    else:
        pass


def lista_izraza_pridruzivanja(nonterminal: Node):
    right = ' '.join([child.data[0] if child.is_terminal else child.data for child in nonterminal.children])
    if right == '<izraz_pridruzivanja>':
        pass
    elif right == '<lista_izraza_pridruzivanja> ZAREZ <izraz_pridruzivanja>':
        pass


tree_list = sys.stdin.read().splitlines()

root = Node(tree_list[0])

fill_tree(root, tree_list)

dfs_print(root)
