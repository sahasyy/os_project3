#!/bin/bash
# test.sh – CS4348 Project 3 Test Script by Sahas Sharma

set -e

echo "[1] Creating index file: test.idx"
python3 index.py test.idx create

echo "[2] Inserting 3 key-value pairs"
python3 index.py test.idx insert 25 250
python3 index.py test.idx insert 10 100
python3 index.py test.idx insert 40 400

echo "[3] Verifying print output:"
python3 index.py test.idx print

echo "[4] Searching for key 10:"
python3 index.py test.idx search 10

echo "[5] Trying to extract to output.csv"
python3 index.py test.idx extract output.csv

echo "[6] Verifying contents of output.csv:"
cat output.csv

echo "[✓] All tests completed successfully."
