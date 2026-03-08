#!/usr/bin/env python
"""Test loading AL(cr) directly from nasa databases."""

import cantera as ct
import yaml

# Test 1: Load directly from nasa_condensed.yaml
print("Test 1: Loading AL(cr) directly from nasa_condensed.yaml")
print("=" * 70)
try:
    al_species = ct.Species.list_from_file(
        r'c:\PWr in Space\Programming\Python\PyPep\data\cantera\nasa_condensed.yaml'
    )
    al_cr = None
    for sp in al_species:
        if sp.name == 'AL(cr)':
            al_cr = sp
            break
    
    if al_cr:
        print(f"✓ Found AL(cr) species")
        print(f"  Composition: {al_cr.composition}")
        print(f"  Thermo model: {al_cr.thermo}")
        
        # Try to create a fixed-stoichiometry phase with AL(cr)
        print("\nCreating fixed-stoichiometry phase with AL(cr)...")
        phase = ct.Solution(thermo='fixed-stoichiometry', species=[al_cr])
        print(f"✓ Successfully created phase: {phase.name}")
        print(f"  Species in phase: {phase.species_names}")
    else:
        print("✗ AL(cr) not found in species list")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Check what species the combustion_equilibrium class loads
print("\n" + "=" * 70)
print("Test 2: Check species loaded by CombustionEquilibrium")
print("=" * 70)

import sys
sys.path.insert(0, r'c:\PWr in Space\Programming\Python\PyPep\src')

from pycea.core.combustion_equilibrium import CombustionEquilibrium

combustor = CombustionEquilibrium(
    gas_database=r'c:\PWr in Space\Programming\Python\PyPep\data\cantera\nasa_gas.yaml',
    condensed_database=r'c:\PWr in Space\Programming\Python\PyPep\data\cantera\nasa_condensed.yaml'
)

print(f"Total species in solution: {combustor.solution.n_species}")
print(f"Species names: {combustor.solution.species_names}")

# Check if AL(cr) is in the combined YAML
if hasattr(combustor, '_combined_yaml_data'):
    yaml_species = combustor._combined_yaml_data.get('species', [])
    print(f"\nTotal species in combined YAML: {len(yaml_species)}")
    
    # Find AL(cr) in the YAML
    al_cr_yaml = None
    for sp in yaml_species:
        if sp.get('name') == 'AL(cr)':
            al_cr_yaml = sp
            break
    
    if al_cr_yaml:
        print(f"✓ AL(cr) is in combined YAML")
        print(f"  Keys: {al_cr_yaml.keys()}")
    else:
        print(f"✗ AL(cr) NOT in combined YAML")
        
        # List condensed species in YAML
        condensed_in_yaml = [sp.get('name', 'UNKNOWN') for sp in yaml_species 
                             if sp.get('thermo') and 'fixed' in sp.get('thermo', '')]
        print(f"\nCondensed species in YAML: {condensed_in_yaml}")
