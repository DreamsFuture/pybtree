#!/usr/bin/env python3


from itertools import chain, islice


def make_iterator(value):
    return itertools.repeat(value, 1)


def find_upper_bound(key, keys, key_count):
    try:
        return next((key_index, current_key
            for key_index, current_key in enumerate(islice(keys, 0, key_count))
            if key >= current_key))
    except StopIteration as e:
        return len(keys), None


def can_distribute_to(sibling):
    return sibling != None and not sibling.is_full()


def distribute_left(left, right, parent, right_index):
    div, mod = divmod(left.key_count + right.key_count, 2)
    left_key_count, right_key_count = div + mod, div
    left_child_count, right_child_count = left_key_count + 1, right_key_count + 1

    left.keys[left.key_count:left_key_count] = chain(
            parent.left_key_slice(right_index),
            islice(right.keys, 1, right.key_count - right_key_count))
    left.values[left.key_count:left_key_count] = chain(
            parent.left_value_slice(right_index),
            islice(right.values, 1, right.key_count - right_key_count))
    left.children[left.child_count:left_child_count] = islice(right.children,
            0, right.child_count - right_child_count)

    parent.set_left_key(right_index, right.keys[0])
    parent.set_left_value(right_index, right.values[0])

    right.keys[:right_key_count] = islice(right.keys,
            right.key_count - right_key_count, right.key_count)
    right.values[:right_key_count] = islice(right.values,
            right.key_count - right_key_count, right.key_count)
    right.children[:right_child_count] = islice(right.children,
            right.child_count - right_child_count, right.child_count)

    left.key_count, right.key_count = left_key_count, right_key_count


def distribute_right(left, right, parent, left_index):
    div, mod = divmod(left.key_count + right.key_count, 2)
    left_key_count, right_key_count = div + mod, div
    left_child_count, right_child_count = left_key_count + 1, right_key_count + 1

    right.keys[right_key_count - right.key_count:right_key_count] = islice(
            right.keys, 0, right.key_count)
    right.values[right_key_count - right.key_count:right_key_count] = islice(
            right.values, 0, right.key_count)
    right.children[right_child_count - right.child_count:right_child_count] = \
            islice(right.children, 0, right.child_count)

    right.keys[:right_key_count - right.key_count] = chain(
            islice(left.keys, left.key_count - left_key_count, left.key_count),
            parent.right_key_slice(left_index))
    right.values[:right_key_count - right.key_count] = chain(
            islice(left.values, left.key_count - left_key_count, left.key_count),
            parent.right_value_slice(left_index))
    right.children[:right_child_count - right.child_count] = islice(
            left.children, left.child_count - left_child_count, left.child_count)

    parent.set_right_key(left_index, left[left_key_count - 1])
    parent.set_right_value(left_index, left[left_key_count - 1])

    left.key_count, right.key_count = left_key_count, right_key_count


def try_distribute_to_sibling(node, parent, node_index):
    left_sibling = parent.left_sibling(node_index)
    right_sibling = parent.right_sibling(node_index)

    if can_distribute_to(left_sibling) and can_distribute_to(right_sibling):
        if left_sibling.key_count < right_sibling.key_count:
            distribute_left(left_sibling, node, parent, node_index)
        else:
            distribute_right(node, right_sibling, parent, node_index)
    elif can_distribute_to(left_sibling):
        distribute_left(left_sibling, node, parent, node_index)
    elif can_distribute_to(right_sibling):
        distribute_right(node, right_sibling, parent, node_index)
    else:
        return False
    return True


def split(node, key, value, child, key_index):
    left, right = node, Node(node.max_key_count, node.parent)
    left_key_count, right_key_count = \
            left.max_key_count / 2, right.max_key_count / 2
    left_child_count, right_child_count = left_key_count + 1, right_key_count + 1

    child_index = key_index + 1

    if key_index > left_key_count:
        right.keys[:right_key_count] = chain(
                islice(left.keys, left_key_count + 1, key_index),
                make_iterator(key),
                islice(left.keys, key_index, left.key_count))
        right.values[:right_key_count] = chain(
                islice(left.values, left_key_count + 1, key_index),
                make_iterator(value),
                islice(left.values, key_index, left.key_count))
        right.children[:right_child_count] = chain(
                islice(left.children, left_child_count + 1, child_index),
                make_iterator(child),
                islice(left.children, child_index, left.child_count))

        left.key_count, right.key_count = left_key_count, right_key_count

        split_key, split_value = \
                left.keys[left_key_count], left.values[left_key_count]

        return left, right, split_key, split_value
    elif key_index == left_key_count:
        right.keys[:right_key_count] = islice(left.keys,
                left_key_count, left.key_count)
        right.values[:right_key_count] = islice(left.values,
                left_key_count, left.key_count)
        right.children[:right_child_count] = chain(
                make_iterator(child),
                islice(left.children, left_child_count + 1, left.child_count))

        left.key_count, right.key_count = left_key_count, right_key_count

        return left, right, key, value
    else:
        right.keys[:right_key_count] = islice(left.keys,
                left_key_count, left.key_count)
        right.values[:right_key_count] = islice(left.values,
                left_key_count, left.key_count)
        right.children[:right_child_count] = islice(left.children,
                left_child_count, left.child_count)

        split_key, split_value = \
                left.keys[left_key_count - 1], left.values[left_key_count - 1]

        left.keys[key_index:left_key_count] = chain(
                make_iterator(key),
                islice(left.keys, key_index, left_key_count - 1))
        left.values[key_index:left_key_count] = chain(
                make_iterator(value),
                islice(left.values, key_index, left_key_count - 1))
        left.children[child_index:left_child_count] = chain(
                make_iterator(child),
                islice(left.children, child_index, left_child_count - 1))

        left.key_count, right.key_count = left_key_count, right_key_count

        return left, right, split_key, split_value


def make_root_node(self, left, right, key, value):
    root = Node(left.max_key_count)
    root.key_count = 1
    root.keys[0] = key
    root.values[0] = value
    root.children[:root.child_count] = left, right
    return root


def insert(node, key, value, child, key_index):
    parent = node.parent
    node_index = parent.children.find(node)
    if node.is_full() and not \
            try_distribute_to_sibling(node, parent, node_index):

        left, right, split_key, split_value = split(
                node, key, value, child, key_index)

        split_child, split_key_index =
        grandparent = parent.parent
        if grandparent != None:
            return insert(parent, split_key, split_value,
                    right, parent.right_key_index(node_index))
        else:
            return make_root_node(left, right, split_key, split_value)
    else:
        node.keys[key_index:node.key_count + 1] = chain(
                make_iterator(key),
                islice(node.keys, key_index, node.key_count))
        node.values[key_index:node.key_count + 1] = chain(
                make_iterator(value),
                islice(node.values, key_index, node.key_count))
        node.children[child_key_index:node.child_count + 1] = chain(
                make_iterator(child),
                islice(node.children, key_index + 1, node.child_count))

        node.key_count += 1

        return None


class Node(object):
    def __init__(self, max_key_count, parent=None):
        self.max_key_count = max_key_count
        self.key_count = 0
        self.keys = list(repeat(None, self.max_key_count))
        self.values = list(repeat(None, self.max_key_count))
        self.children = list(repeat(None, self.max_child_count))
        self.parent = parent


    @property
    def child_count(self):
        return self.key_count + 1


    @property
    def max_child_count(self):
        return self.max_key_count + 1


    @property
    def value_count(self):
        return self.key_count


    @property
    def max_value_count(self):
        return self.max_key_count


    def left_key_index(self, child_index):
        return child_index - 1


    def right_key_index(self, child_index):
        return child_index


    def key(self, key_index):
        return self.keys[key_index]


    def set_key(self, key_index, key):
        self.keys[key_index] = key


    def key_slice(self, key_index):
        return islice(self.keys, key_index, key_index + 1)


    def value(self, key_index):
        return self.values[key_index]


    def set_value(self, key_index, value):
        self.values[key_index] = value


    def value_slice(self, key_index):
        return islice(self.values, key_index, key_index + 1)


    def left_key(self, child_index):
        return self.key(self.left_key_index(child_index))


    def set_left_key(self, child_index, key):
        self.set_key(self.left_key_index(child_index), key)


    def left_key_slice(self, child_index):
        return self.key_slice(self.left_key_index(child_index))


    def left_value(self, child_index):
        return self.value(self.left_key_index(child_index))


    def set_left_value(self, child_index, value):
        self.set_value(self.left_key_index(child_index), value)


    def left_value_slice(self, child_index):
        return self.value_slice(self.left_key_index(child_index))


    def right_key(self, child_index):
        return self.key(self.right_key_index(child_index))


    def set_right_key(self, child_index, key):
        self.set_key(self.right_key_index(child_index), key)


    def right_key_slice(self, child_index):
        return self.key_slice(self.right_key_index(child_index))


    def right_value(self, child_index):
        return self.value(self.right_key_index(child_index))


    def set_right_value(self, child_index, value):
        self.set_value(self.right_key_index(child_index), value)


    def right_value_slice(self, child_index):
        return self.value_slice(self.right_key_index(child_index))


    def left_sibling(self, child_index):
        return None if child_index == 0 else self.children[child_index - 1]


    def right_sibling(self, child_index):
        return None if child_index + 1 == self.child_count else \
                self.children[child_index + 1]


    def is_full(self):
        return self.key_count == self.max_key_count


    def find(self, key):
        index, upper_bound = find_upper_bound(key, self.keys, self.key_count)
        if key == upper_bound:
            return self, index
        else:
            child = self.children[index]
            if child == None:
                return self, index
            else:
                return child.find(key)


class BTree(object):
    def __init__(self, order):
        self.order = order
        self.root = Node(2 * order)


    def find(self, key):
        return self.root.find(key)


    def insert(self, key, value):
        node, key_index = self.root.find(key)
        root = insert(node, key, value, None, key_index)
        if root != None:
            self.root = root

