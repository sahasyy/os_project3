# Project: sahas-os-project3 : B Tree Index File Manager

This project implments an on disk BTree using Python with block-based I/O and a strict 3 node memory limit. it suports commands to create, insert, search, load, print, and extract key value pairs from a index file.

## folder layout
```
sahas-os-project3/
├── index.py # main python script with all commands impemented
├── devlog.md # development log with notes per milestone
├── test.sh # test script to validate core functionaity
├── Makefile # shortcuts to build/test/clean
├── README.md # this file
└── sample.csv # sample input file
```

## Program Description

### `index.py`
- Implements a BTree with minimal degree 10 (19 keys, 20 children).
- Each node and the header occupy a 512-byte block on disk.
- Uses big-endian byte encoding and `struct` packing
- Commands:
  - `create <indexfile>`: create a new index
  - `insert <indexfile> <key> <val>`: add a key-value pair
  - `search <indexfile> <key>`: lookup key and print result
  - `load <indexfile> <csvfile>`: load key,value pairs from a CSV file
  - `print <indexfile>`: print all key,value pairs in order
  - `extract <indexfile> <output.csv>`: save all entries to a CSV (if file doesn't exist)

### `devlog.md`
- Logs design decisions, LRU cache implementation, bugs and fixes
- Reflects the project evolution from initial planning to final polish

### `test.sh`
- Runs a complete test:
  - Creates a new indx.
  - Inserts 3 values
  - Prints, searches, and extracts output.
  - Confirms correctness with visible output.

### `Makefile`
- `make test`: run the test script
- `make clean`: remove generated files

## getting started

1. ensure you have Python 3.7+ installed.
2. make sure your terminal is in the project folder.
3. Run the test:

```bash
make test
