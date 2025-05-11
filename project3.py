import sys
import struct
import csv
import os
from functools import lru_cache

BLOCK_SIZE = 512
MAGIC = b"4348PRJ3"
DEGREE = 10  # minimal degree t

class BlockIO:
    def __init__(self, filename, mode):
        self.file = open(filename, mode + 'b')

    def read_block(self, block_id):
        self.file.seek(block_id * BLOCK_SIZE)
        data = self.file.read(BLOCK_SIZE)
        if len(data) < BLOCK_SIZE:
            data += b"\x00" * (BLOCK_SIZE - len(data))
        return data

    def write_block(self, block_id, data):
        assert len(data) == BLOCK_SIZE
        self.file.seek(block_id * BLOCK_SIZE)
        self.file.write(data)
        self.file.flush()

class Node:
    def __init__(self, node_id, is_leaf=True):
        self.id = node_id
        self.parent = 0
        self.is_leaf = is_leaf
        self.nkeys = 0
        self.keys = [0] * (2*DEGREE - 1)
        self.values = [0] * (2*DEGREE - 1)
        self.children = [0] * (2*DEGREE)

    @classmethod
    def from_bytes(cls, data):
        is_leaf = bool(data[0])
        node_id = struct.unpack_from('>Q', data, 1)[0]
        parent = struct.unpack_from('>Q', data, 9)[0]
        nkeys = struct.unpack_from('>I', data, 17)[0]
        node = cls(node_id, is_leaf)
        node.parent = parent
        node.nkeys = nkeys
        offset = 21
        for i in range(2*DEGREE - 1):
            node.keys[i] = struct.unpack_from('>Q', data, offset + i*8)[0]
        offset += (2*DEGREE - 1)*8
        for i in range(2*DEGREE - 1):
            node.values[i] = struct.unpack_from('>Q', data, offset + i*8)[0]
        offset += (2*DEGREE - 1)*8
        for i in range(2*DEGREE):
            node.children[i] = struct.unpack_from('>Q', data, offset + i*8)[0]
        return node

    def to_bytes(self):
        data = bytearray(BLOCK_SIZE)
        data[0] = 1 if self.is_leaf else 0
        struct.pack_into('>Q', data, 1, self.id)
        struct.pack_into('>Q', data, 9, self.parent)
        struct.pack_into('>I', data, 17, self.nkeys)
        offset = 21
        for i in range(2*DEGREE - 1):
            struct.pack_into('>Q', data, offset + i*8, self.keys[i])
        offset += (2*DEGREE - 1)*8
        for i in range(2*DEGREE - 1):
            struct.pack_into('>Q', data, offset + i*8, self.values[i])
        offset += (2*DEGREE - 1)*8
        for i in range(2*DEGREE):
            struct.pack_into('>Q', data, offset + i*8, self.children[i])
        return bytes(data)

class Header:
    def __init__(self):
        self.root_id = 0
        self.next_free_id = 1

    @classmethod
    def from_bytes(cls, data):
        magic = data[:8]
        if magic != MAGIC:
            raise ValueError("Invalid index file: magic mismatch")
        hdr = cls()
        hdr.root_id = struct.unpack_from('>Q', data, 8)[0]
        hdr.next_free_id = struct.unpack_from('>Q', data, 16)[0]
        return hdr

    def to_bytes(self):
        data = bytearray(BLOCK_SIZE)
        data[:8] = MAGIC
        struct.pack_into('>Q', data, 8, self.root_id)
        struct.pack_into('>Q', data, 16, self.next_free_id)
        return bytes(data)

class BTree:
    def __init__(self, filename, mode='r+'):
        self.io = BlockIO(filename, mode)
        self.header = Header.from_bytes(self.io.read_block(0))

    @classmethod
    def create(cls, filename):
        if os.path.exists(filename):
            sys.exit("Error: File already exists.")
        with open(filename, 'wb') as f:
            f.truncate(BLOCK_SIZE * 4)
        tree = cls(filename, 'r+')
        tree.header.root_id = 1
        tree.header.next_free_id = 2
        tree.io.write_block(0, tree.header.to_bytes())
        root = Node(1, is_leaf=True)
        tree.io.write_block(1, root.to_bytes())
        return tree

    def close(self):
        self.io.file.close()

    def _write_header(self):
        self.io.write_block(0, self.header.to_bytes())

    def _write_node(self, node):
        self.load_node.cache_clear()
        self.io.write_block(node.id, node.to_bytes())

    @lru_cache(maxsize=3)
    def load_node(self, node_id):
        return Node.from_bytes(self.io.read_block(node_id))

    def search(self, key, node_id=None):
        if node_id is None:
            node_id = self.header.root_id
        node = self.load_node(node_id)
        i = 0
        while i < node.nkeys and key > node.keys[i]:
            i += 1
        if i < node.nkeys and key == node.keys[i]:
            return node.values[i]
        if node.is_leaf:
            return None
        return self.search(key, node.children[i])

    def insert(self, key, value):
        root = self.load_node(self.header.root_id)
        if root.nkeys == 2*DEGREE - 1:
            new_root = Node(self.header.next_free_id, is_leaf=False)
            self.header.next_free_id += 1
            new_root.children[0] = root.id
            root.parent = new_root.id
            self._write_node(root)
            new_root.nkeys = 0
            self.header.root_id = new_root.id
            self._write_header()
            self._write_node(new_root)
            self._split_child(new_root, 0)
            self._insert_nonfull(new_root, key, value)
        else:
            self._insert_nonfull(root, key, value)

    def _split_child(self, parent, idx):
        t = DEGREE
        child = self.load_node(parent.children[idx])
        new = Node(self.header.next_free_id, is_leaf=child.is_leaf)
        self.header.next_free_id += 1
        new.nkeys = t - 1
        for j in range(t - 1):
            new.keys[j] = child.keys[j + t]
            new.values[j] = child.values[j + t]
        if not child.is_leaf:
            for j in range(t):
                new.children[j] = child.children[j + t]
        child.nkeys = t - 1
        for j in range(parent.nkeys, idx, -1):
            parent.children[j + 1] = parent.children[j]
        parent.children[idx + 1] = new.id
        for j in range(parent.nkeys - 1, idx - 1, -1):
            parent.keys[j + 1] = parent.keys[j]
            parent.values[j + 1] = parent.values[j]
        parent.keys[idx] = child.keys[t - 1]
        parent.values[idx] = child.values[t - 1]
        parent.nkeys += 1
        self._write_node(child)
        self._write_node(new)
        self._write_node(parent)
        self._write_header()

    def _insert_nonfull(self, node, key, value):
        i = node.nkeys - 1
        if node.is_leaf:
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1] = key
            node.values[i + 1] = value
            node.nkeys += 1
            self._write_node(node)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            child = self.load_node(node.children[i])
            if child.nkeys == 2*DEGREE - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_nonfull(self.load_node(node.children[i]), key, value)

    def inorder(self, node_id=None):
        if node_id is None:
            node_id = self.header.root_id
        node = self.load_node(node_id)
        result = []
        for i in range(node.nkeys):
            if not node.is_leaf:
                result += self.inorder(node.children[i])
            result.append((node.keys[i], node.values[i]))
        if not node.is_leaf:
            result += self.inorder(node.children[node.nkeys])
        return result

    def print_tree(self):
        for k, v in self.inorder():
            print(f"{k},{v}")

    def extract(self, output_path):
        if os.path.exists(output_path):
            sys.exit("Error: Output file already exists.")
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for k, v in self.inorder():
                writer.writerow([k, v])

    def load(self, csv_path):
        if not os.path.exists(csv_path):
            sys.exit("Error: CSV input file not found.")
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                key, val = int(row[0]), int(row[1])
                self.insert(key, val)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 index.py <indexfile> <command> [args]")
        sys.exit(1)
    fn, cmd, *args = sys.argv[1:]
    if cmd == 'create':
        BTree.create(fn)
    elif not os.path.exists(fn):
        sys.exit("Error: Index file does not exist.")
    else:
        try:
            tree = BTree(fn, 'r+')
        except Exception as e:
            sys.exit(f"Error loading index file: {e}")
        if cmd == 'insert' and len(args) == 2:
            k, v = int(args[0]), int(args[1])
            tree.insert(k, v)
        elif cmd == 'search' and len(args) == 1:
            res = tree.search(int(args[0]))
            if res is None:
                print("Error: Key not found")
            else:
                print(f"{args[0]},{res}")
        elif cmd == 'load' and len(args) == 1:
            tree.load(args[0])
        elif cmd == 'print':
            tree.print_tree()
        elif cmd == 'extract' and len(args) == 1:
            tree.extract(args[0])
        else:
            print(f"Unknown or malformed command: {cmd}")
        tree.close()
