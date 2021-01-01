from __future__ import annotations
from collections import defaultdict

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


def primarni_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def postfiks_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def lista_argumenata(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def unarni_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def unarni_operator(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def cast_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def ime_tipa(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def specifikator_tipa(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def multiplikativni_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def aditivni_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def odnosni_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def jednakosni_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def bin_i_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def bin_xili_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def bin_ili_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def log_i_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def log_ili_izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def izraz_pridruzivanja(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def izraz(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def slozena_naredba(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def lista_naredbi(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def naredba(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def izraz_naredba(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def naredba_grananja(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def naredba_petlje(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def naredba_skoka(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def prijevodna_jedinica(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def vanjska_deklaracija(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def definicija_funkcije(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def lista_parametara(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def deklaracija_parametra(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def lista_deklaracija(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def deklaracija(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def lista_init_deklaratora(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def init_deklarator(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def izravni_deklarator(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def inicijalizator(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


def lista_izraza_pridruzivanja(nonterminal: Node, fun_dict):
    for child in nonterminal.children:
        pass


function_dict = {'<primarni_izraz>': primarni_izraz,
                 '<postfiks_izraz>': postfiks_izraz,
                 '<lista_argumenata>': lista_argumenata,
                 '<unarni_izraz>': unarni_izraz,
                 '<unarni_operator>': unarni_operator,
                 '<cast_izraz>': cast_izraz,
                 '<ime_tipa>': ime_tipa,
                 '<specifikator_tipa>': specifikator_tipa,
                 '<multiplikativni_izraz>': multiplikativni_izraz,
                 '<aditivni_izraz>': aditivni_izraz,
                 '<odnosni_izraz>': odnosni_izraz,
                 '<jednakosni_izraz>': jednakosni_izraz,
                 '<bin_i_izraz>': bin_i_izraz,
                 '<bin_xili_izraz>': bin_xili_izraz,
                 '<bin_ili_izraz>': bin_ili_izraz,
                 '<log_i_izraz>': log_i_izraz,
                 '<log_ili_izraz>': log_ili_izraz,
                 '<izraz_pridruzivanja>': izraz_pridruzivanja,
                 '<izraz>': izraz,
                 '<slozena_naredba>': slozena_naredba,
                 '<lista_naredbi>': lista_naredbi,
                 '<naredba>': naredba,
                 '<izraz_naredba>': izraz_naredba,
                 '<naredba_grananja>': naredba_grananja,
                 '<naredba_petlje>': naredba_petlje,
                 '<naredba_skoka>': naredba_skoka,
                 '<prijevodna_jedinica>': prijevodna_jedinica,
                 '<vanjska_deklaracija>': vanjska_deklaracija,
                 '<definicija_funkcije>': definicija_funkcije,
                 '<lista_parametara>': lista_parametara,
                 '<deklaracija_parametra>': deklaracija_parametra,
                 '<lista_deklaracija>': lista_deklaracija,
                 '<deklaracija>': deklaracija,
                 '<lista_init_deklaratora>': lista_init_deklaratora,
                 '<init_deklarator>': init_deklarator,
                 '<izravni_deklarator>': izravni_deklarator,
                 '<inicijalizator>': inicijalizator,
                 '<lista_izraza_pridruzivanja>': lista_izraza_pridruzivanja,
                 }

fun_dict = defaultdict(lambda: False, function_dict)

print(fun_dict)

tree_list = sys.stdin.read().splitlines()

root = Node(tree_list[0])

fill_tree(root, tree_list)

dfs_print(root)
