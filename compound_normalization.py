#!/usr/bin/env python3

import pubchempy as pcp
import pandas as pd
import sys
import os

class PropertiesList:
    class AvailableProperties:
        # Acquired from keys in pcp.Compound.to_dict()
        _availableProps=['atom_stereo_count', 'atoms', 'bond_stereo_count', 'bonds', 'cactvs_fingerprint', 'canonical_smiles', 'charge', 'cid', 'complexity', 'conformer_id_3d', 'conformer_rmsd_3d', 'coordinate_type', 'covalent_unit_count', 'defined_atom_stereo_count', 'defined_bond_stereo_count', 'effective_rotor_count_3d', 'elements', 'exact_mass', 'feature_selfoverlap_3d', 'fingerprint', 'h_bond_acceptor_count', 'h_bond_donor_count', 'heavy_atom_count', 'inchi', 'inchikey', 'isomeric_smiles', 'isotope_atom_count', 'iupac_name', 'mmff94_energy_3d', 'mmff94_partial_charges_3d', 'molecular_formula', 'molecular_weight', 'monoisotopic_mass', 'multipoles_3d', 'pharmacophore_features_3d', 'rotatable_bond_count', 'shape_fingerprint_3d', 'shape_selfoverlap_3d', 'tpsa', 'undefined_atom_stereo_count', 'undefined_bond_stereo_count', 'volume_3d', 'xlogp']
        def getAvailableProps(self):
            return self._availableProps

    _propList=[]
    _availableProps=AvailableProperties()
    def __init__(self, prop: list = [], allProps=False):
        if allProps:
            # All available properties are to be saved for each compound
            self._propList = self._availableProps.getAvailableProps()
        else:
            self._propList=prop
        self._current_index = 0
        self._class_size = len(self._propList)
    def appendProp(self, prop: str):
        # Enables adding props into list of wanted properties (checks if they are defined on the pcp.Compound object)
        availableProps = self._availableProps.getAvailableProps()
        try:
            i = [x.lower().strip() for x in availableProps].index(prop.lower().strip())
            if availableProps[i] not in self._propList:
                self._propList.append(availableProps[i])
                self._class_size+=1
        except ValueError:
            print("Property to append invalid")
    def getList(self):
        return self._propList
    def __iter__(self):
        return self
    def __next__(self):
        if self._current_index < self._class_size:
            item = self._propList[self._current_index]
            self._current_index+=1
            return item
        raise StopIteration

class Compounds:
    _properties: list = []
    _compounds: list = []
    def __init__(self, compoundsname: list, properties: list):
        # Initiates each compound ( every molecule has data fetched stored in internal variable )
        for compound in compoundsname:
            self._compounds.append(Molecule(compound))

        self._properties=properties
    def getCompounds(self):
        # Returns list of compounds
        return self._compounds
    def getCompoundsPropertiesData(self):
        df=pcp.compounds_to_frame([c.getCompound() for c in self._compounds], properties=self._properties) # Gets the properties about compounds
        df = pd.concat([self.getNamesDataframe(),df], axis=1)   # Joins info about the compound names and properties
        df.reset_index(inplace=True)    # Transforms CID index into separate column
        print(df)
        return df
    def getNamesDataframe(self):
        df = pd.DataFrame(data=[[c.getCid(),c.getOriginalName(), c.getNormalizedName()] for c in self._compounds],
                          columns=["cid","original_name","normalized_name"]).set_index("cid")
        return df

class Molecule:
    compound: pcp.Compound
    def __init__(self, name: str):
        self.name = name
        for c in pcp.get_compounds(name, "name"):
            self.compound = c
        self.cid = self.compound.cid
        self.normalizedName = self.compound.synonyms[0]
    def getCompound(self):
        return self.compound
    def getNormalizedName(self):
        return self.normalizedName.title()
    def getOriginalName(self):
        return self.name
    def getCid(self):
        return self.cid

def export_to_excel(df, file_name, sheet_name):
    # Saves df with molecules and properties into excel table with formatting and number types
    def columns_table_format(df):
        # Prepares column names in acceptable format for the excel table
        output_list = []
        for i, col in enumerate(df.columns):
            dictt = {}
            dictt['header'] = str(col)
            output_list.append(dictt)
        return output_list

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    file_name_path = os.path.join(os.getcwd(),file_name)
    writer = pd.ExcelWriter(f'{file_name_path}', engine='xlsxwriter',
                            engine_kwargs={'options': {'strings_to_numbers': True}})
    df.to_excel(writer, index=False, sheet_name=sheet_name)

    # Get access to the workbook and sheet
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    numbers_int = workbook.add_format()
    numbers_int.set_num_format(1)

    numbers_float = workbook.add_format()
    numbers_float.set_num_format(2)

    text_allign = workbook.add_format()
    text_allign.set_align("center")

    for i,col in enumerate(df.columns):
        col_type=df.dtypes[col]
        if col_type=="object":
            worksheet.set_column(i,i, None,text_allign)
        elif col_type=="float64":
            worksheet.set_column(i,i,None,numbers_float)
        elif col_type=="int64":
            worksheet.set_column(i,i,None,numbers_int)
    worksheet.add_table(0, 0, len(df.index), len(df.columns)-1, {'header_row': True,
                                                                 'first_column': True,
                                                                 'columns': columns_table_format(df)
                                                                 })
    worksheet.autofit()
    writer.close()
def process_molecules(compounds_list):
    #  ['molecular_formula', 'molecular_weight', 'canonical_smiles', 'isomeric_smiles','xlogp','h_bond_donor_count', 'h_bond_acceptor_count']
    proplist = PropertiesList(allProps=True, prop=["xlogp", "isomeric_smiles","h_bond_acceptor_count","molecular_weight","canonical_smiles",
                                    "rotatable_bond_count","molecular_formula","h_bond_donor_count"])
    comp = Compounds(compounds_list,
                     properties=proplist)
    df =comp.getCompoundsPropertiesData()
    export_to_excel(df,file_name="Compounds.xlsx", sheet_name='Properties')
def read_and_save_molecules():

    if len(sys.argv)!=2:
        print("Usage: use input_molecules.txt input file to read compound names or pass argument X to read molecules from script variable")
        sys.exit(1)
    else:
        input_a = sys.argv[1]
        if input_a=="input_molecules.txt":
            try:
                with open(input_a, 'r') as file:
                    lines = file.readlines()
                    # Optional: Remove newline characters from each line and strip leading/trailing whitespaces
                    molecules = [line.strip() for line in lines]
                    process_molecules(molecules)
            except FileNotFoundError:
                print(f"Error: File '{input_a}' not found.")
                sys.exit(1)
        elif input_a.lower()=="x":
            molecules=["Adenosine","Adenocard","BG8967","Bivalirudin","BAYT006267","diflucan","ibrutinib","PC-32765"]
            process_molecules(molecules)
        else:
            print(f"Invalid call of python script. Usage: use input_molecules.txt input file to read compound names or pass argument X to read molecules from script variable")
            sys.exit(1)


def main():
    read_and_save_molecules()

if __name__=="__main__":
    main()