# Makefile for CS4348 Project 3 – Sahas Sharma

.PHONY: test clean

all:
	@echo "Available commands:"
	@echo "  make test     Run full project test"
	@echo "  make clean    Remove all generated files"

test:
	@echo "[TEST] Creating index file..."
	python3 index.py test.idx create
	@echo "[TEST] Inserting key-value pairs..."
	python3 index.py test.idx insert 10 100
	python3 index.py test.idx insert 20 200
	python3 index.py test.idx insert 5 50
	@echo "[TEST] Printing index contents..."
	python3 index.py test.idx print
	@echo "[TEST] Searching for key 10..."
	python3 index.py test.idx search 10
	@echo "[TEST] Extracting to output.csv..."
	python3 index.py test.idx extract output.csv
	@echo "[TEST] Contents of output.csv:"
	cat output.csv

clean:
	rm -f test.idx output.csv