#!/usr/bin/env python3
import os

# Call normalization of names with properties fetching and create Compounds.xlsx
print("Executing normalization")
os.system("python3 compound_normalization.py input_molecules.txt")

print("Executing molecules rating")
os.system("python3 compounds_ranking.py")
