from __future__ import annotations

import sys
import re


class Node:

    def __init__(self, data: str, parent: Node = None):
        self.parent = parent
        self.data = data
        self.children = []


def dfs_print(root: Node, prefix=''):
    if root:
        print(prefix + root.data)
        prefix = prefix + ' '
    for child in root.children:
        dfs_print(child, prefix)


def fill_tree(parent: Node, tree_list: list):
    previous_space_count = -1
    pattern = re.compile(r'^(\s*)(.*)$')

    for node in tree_list[1:]:
        match = pattern.match(node)
        space_count = len(match.group(1))
        node_data = match.group(2)
        if space_count > previous_space_count:
            parent.children.append(Node(node_data, parent))
            parent = parent.children[-1]
        else:
            while space_count <= previous_space_count:
                parent = parent.parent
                previous_space_count -= 1
            parent.children.append(Node(node_data, parent))
            parent = parent.children[-1]

        previous_space_count = space_count


tree_list = sys.stdin.read().splitlines()

root = Node(tree_list[0])

fill_tree(root, tree_list)

dfs_print(root)
