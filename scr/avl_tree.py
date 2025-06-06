from dataclasses import dataclass, field
from typing import cast


#  The `order=True` and `compare=True/False` make the `Node` class to be comparable only by value
# Docs links:
# https://docs.python.org/3/library/dataclasses.html?module-contents=#dataclasses.dataclass
# https://docs.python.org/3/library/dataclasses.html?module-contents=#dataclasses.field
@dataclass(order=True)
class Node:
    value: int = field(compare=True)
    parent: "Node | None" = field(default=None, compare=False)
    left: "Node | None" = field(default=None, compare=False)
    right: "Node | None" = field(default=None, compare=False)
    height: int = field(default=0, compare=False)

    @property
    def balance_factor(self) -> int:
        right_child_height = -1 if self.right is None else self.right.height
        left_child_height = -1 if self.left is None else self.left.height
        return right_child_height - left_child_height


@dataclass
class NodeSearchResult:
    searched_node: Node | None = None
    insert_place: Node | None = None

    @property
    def is_found(self) -> bool:
        return isinstance(self.searched_node, Node)


class AVLTree:
    def __init__(self, root: Node | None = None) -> None:
        self.root = root
        self.__size = 0 if root is None else 1

    @property
    def size(self):
        return self.__size

    def find(self, value: int) -> Node | None:
        node = self.__create_node_from_value(value=value)
        search_result = self.__search_node(node)

        result = search_result.searched_node if search_result.is_found else None
        return result

    def insert(self, value: int | Node) -> bool:
        new_node = self.__create_node_from_value(value)
        is_inserted = self.__bst_insert(new_node)

        if not is_inserted:
            return False

        self.__balance(new_node)
        return True

    def remove(self, value: int | Node) -> bool:
        node = self.__create_node_from_value(value=value)
        deleted_node = self.__bst_remove(node)

        if deleted_node is None:
            return False

        if deleted_node.parent is not None:
            self.__balance(deleted_node.parent)

        return True

    def __search_node(self, searched_node: Node) -> NodeSearchResult:
        current = self.root
        result = NodeSearchResult()

        while current is not None:
            if current == searched_node:
                result.searched_node = current
                break
            next_node = current.left if searched_node < current else current.right
            if next_node is None:
                result.insert_place = current
            current = next_node

        return result

    def __bst_insert(self, node: Node) -> bool:
        search_result = self.__search_node(node)

        if search_result.is_found:
            return False

        parent = search_result.insert_place

        if parent is None:
            self.root = node
        else:
            node.parent = parent
            if node < parent:
                parent.left = node
            else:
                parent.right = node

        self.__size += 1
        return True

    def __update_height(self, node: Node) -> None:
        left_height = node.left.height if node.left is not None else -1
        right_height = node.right.height if node.right is not None else -1
        
        node.height = max(left_height, right_height) + 1

    def __rotate_right(self, node: Node) -> None:
        left_child = node.left

        if left_child is None:
            raise TypeError("node must have left child")

        right_grandchild = left_child.right

        # Perform rotation
        left_child.right = node
        node.left = right_grandchild

        # Update parents
        left_child.parent = node.parent
        node.parent = left_child
        if right_grandchild is not None:
            right_grandchild.parent = node

        if left_child.parent is None:
            self.root = left_child
        elif left_child.parent.left is node:
            left_child.parent.left = left_child
        else:
            left_child.parent.right = left_child

        self.__update_height(node)
        self.__update_height(left_child)

    def __rotate_left(self, node: Node) -> None:
        right_child = node.right

        if right_child is None:
            raise TypeError("node must have right child")

        left_grandchild = right_child.left

        # Perform rotation
        right_child.left = node
        node.right = left_grandchild

        # Update parents
        right_child.parent = node.parent
        node.parent = right_child
        if left_grandchild is not None:
            left_grandchild.parent = node

        # Update parent link
        if right_child.parent is None:
            self.root = right_child
        elif right_child.parent.left is node:
            right_child.parent.left = right_child
        else:
            right_child.parent.right = right_child

        self.__update_height(node)
        self.__update_height(right_child)

    def __balance(self, node: Node) -> None:
        current = node
        while current is not None:
            self.__update_height(current)
            bf = current.balance_factor
            if bf < -1:
                if current.left is not None and current.left.balance_factor > 0:
                    self.__rotate_left(current.left)
                self.__rotate_right(current)
            elif bf > 1:
                if current.right is not None and current.right.balance_factor < 0:
                    self.__rotate_right(current.right)
                self.__rotate_left(current)

            current = current.parent

    def __bst_remove_leaf(self, node: Node) -> Node | None:
        if not (node.left is None and node.right is None):
            return None

        if node.parent is None:
            self.root = None
        elif node is node.parent.left:
            node.parent.left = None
        else:
            node.parent.right = None

        self.__size -= 1
        return node

    def __bst_remove_one_child_node(self, node: Node) -> Node | None:
        if (node.left is None) == (node.right is None):
            return None

        child = cast("Node", node.left if node.right is None else node.right)
        if node.parent is None:
            self.root = child
            child.parent = None
        elif node.parent.left is node:
            node.parent.left = child
            child.parent = node.parent
        else:
            node.parent.right = child
            child.parent = node.parent

        self.__size -= 1
        return node

    def __bst_remove_two_child_node(self, node: Node) -> Node | None:
        if node.left is None or node.right is None:
            return None

        successor = node.right
        while successor.left is not None:
            successor = successor.left

        node.value = successor.value
        # The node wasn't actually deleted, its value was only replaced with successor's one
        # So now we need to deleted successor.
        # The successor now can only be a leaf or one-chid node so we use methods for this.
        for case in (self.__bst_remove_one_child_node, self.__bst_remove_leaf):
            deleted_node = case(successor)
            if isinstance(deleted_node, Node):
                break

        # According to the fact that successor is either leaf or one-chide node we can be certain
        # that it will be deleted.
        # As we need to make rebalance starting from actually deleted node parent, we return the successor
        # instead of node
        return successor

    def __bst_remove(self, node: Node) -> Node | None:
        search_result = self.__search_node(node)
        node_to_remove = search_result.searched_node
        if not node_to_remove:
            return None

        # Here's three possible removal scenarios in BST. And If the runtime reach this point it granites that
        # one of this methods return deleted node because the node_to_delete is already in this tree.
        cases = [
            self.__bst_remove_leaf,
            self.__bst_remove_one_child_node,
            self.__bst_remove_two_child_node,
        ]
        for case in cases:
            deleted_node = case(node_to_remove)
            if isinstance(deleted_node, Node):
                break
        else:
            # One of the cases must return a Node type. if it's not there's an error in logic
            raise RuntimeError("The loop with removal scenarios must hit break")

        return deleted_node

    @staticmethod
    def __create_node_from_value(value: int | Node) -> Node:
        if not isinstance(value, (int, Node)):
            message = f"value parameter must be type int or Node but you provide type {type(value)}"
            raise TypeError(message)
        if isinstance(value, Node):
            return value
        return Node(value)
