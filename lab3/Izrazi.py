from lab3.SemantickiAnalizator import Node


def provjeri_primarni_izraz(node: Node):
    if ' '.join([child.data[0] if child.is_terminal else child.data for child in node.children]) == 'IDN':
        child = node.children[0]
        # provjeri je li child u tablici znakova
        # ako nije ispisi gresku f'<primarni_izraz> ::= {child.data[0]}(child.data[1], child.data[2])
