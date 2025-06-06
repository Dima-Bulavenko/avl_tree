from random import randint

from scr.avl_tree import AVLTree, Node


def print_tree(root: Node | None):
    if not root:
        print("[empty tree]")
        return

    # Calculate tree height to determine display width
    def get_height(node):
        if not node:
            return 0
        return 1 + max(get_height(node.left), get_height(node.right))

    height = get_height(root)
    max_width = 2**height

    # Level-order traversal with position
    queue = [(root, 0, max_width // 2)]
    prev_level = 0
    line = ""

    positions = {}
    while queue:
        node, level, pos = queue.pop(0)
        if level != prev_level:
            print(line)
            line = ""
            prev_level = level

        positions[(level, pos)] = str(node.value)
        line += " " * (pos * 2 - len(line)) + str(node.value)

        spacing = 2 ** (height - level - 2)
        if node.left:
            queue.append((node.left, level + 1, pos - spacing))
        if node.right:
            queue.append((node.right, level + 1, pos + spacing))

    if line:
        print(line)


def main():
    t = AVLTree()

    tree_values = {randint(1, 100) for i in range(randint(1, 15))}

    for value in tree_values:
        t.insert(value)
    print("based on values:", tree_values)
    print_tree(t.root)

    # This code randomly delete values from tree
    # for index in range(randint(0, len(tree_values) - 1)):
    #     deleted_value = tree_values.pop()
    #     print("delete:", deleted_value, "from:")
    #     t.remove(deleted_value)
    #     print_tree(t.root)


if __name__ == "__main__":
    main()
