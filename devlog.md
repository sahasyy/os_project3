# DevLog – CS4348 Project 3  
**Author:** Sahas sharma (SXS210541)

## [05/09/2025] Friday – Initial Setup
- Read the full spec from the PDF and noted key components.
- Understood B-Tree degree 10, block layout, 512-byte I/O constraint.
- Noted Python's suitability due to built-in `to_bytes`, `struct`, and `lru_cache`.
- Planned to start implementation Saturday.
- made github repo

---

## [05/10/2025] Saturday – start coding

### 11:00 AM
- Initialized Python project and basic file structure.
- created `BlockIO`, `Header`, and `Node` classes.
- Handled `to_bytes` and `from_bytes` for node serialization
- made push to github repo

### 3:08 PM
- finished `BTree.create`, `insert`, and header syncing
- implemented split logic, minimal insert for leaf only case

### 7:33 PM
- Added `load_node` LRU cache (max 3 nodes).
- Confirmed cache works by counting evictions
- First test with a few `insert` and `print` commands.

---

## [05/11/2025] Sunday – Full Feature Finish

### 9:05 AM
- Completed `search`, `print_tree`, `extract`, and `load`
- Added error handling: file not found, malformed, duplcate output
- Added `os.path.exists` and graceful exits.

### 1:15 PM ?
- Created `README.md`, `Makefile`, and `test.sh`.
- Verified all edge cases: full node split, CSV load, output overwite error

### 10:35 PM
- Final testing completed
- Project passes all logical and spec checks
- Ready to submit
- Everything up to date on github repo

---
