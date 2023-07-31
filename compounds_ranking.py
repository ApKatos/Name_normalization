#!/usr/bin/env python3

import pandas as pd
import numpy as np
from compound_normalization import export_to_excel

def check_range(value, ranges: tuple):
    (range_low, range_up)=ranges
    if range_low<=value<=range_up:
        return True
    else:
        return False

def check_criteria(name, thr, df: pd.DataFrame, rules: dict):
    df_sub = df[list(rules.keys())]

    # Check if observed property value is in allowed range
    df[f"{name}_score"] = df_sub.apply(lambda row: sum(list(map(check_range, row, rules.values()))), axis=1)

    # Classify according to allowed threshold
    df[f"{name}_approved"] = np.where(df[f'{name}_score'] >= thr, True, False)
    return df

def lipinski_rule(df: pd.DataFrame):
    # Parameter names and the allowed range
    lipinski_rules = {"molecular_weight": (0, 500),
                      "xlogp": (0, 5),
                      "h_bond_acceptor_count": (0, 10),
                      "h_bond_donor_count": (0, 5)
                      }

    # Create rating for molecules according to RO5 with at least 3 parameters in allowed range
    df = check_criteria("lipinski_rule", 3, df, lipinski_rules)
    return df

def evaluate_compounds():
    # Excel file with compounds properties
    excel_file = "Compounds.xlsx"
    df = pd.read_excel(excel_file)

    # Evaluating compounds according to Lipinski rule of 5
    df = lipinski_rule(df)

    df_export = df[["cid", "normalized_name", "lipinski_rule_score", "lipinski_rule_approved"]].drop_duplicates() \
        .sort_values(by="lipinski_rule_score", ascending=False) \
        .reset_index(drop=True)
    export_to_excel(df_export, "Compounds_ranking.xlsx", "Ranking")

def main():
    evaluate_compounds()

if __name__ == '__main__':
    main()