"""
Physical and chemical constants for PyPep calculations.

This module contains fundamental constants used throughout the package,
including elemental molar masses for composition calculations.
"""

from typing import Dict

# Elemental molar masses in g/mol
# Source: IUPAC Periodic Table of the Elements (2021)
ELEMENTAL_MOLAR_MASS: Dict[str, float] = {
    "H": 1.008,    # Hydrogen
    "He": 4.003,   # Helium
    "Li": 6.941,   # Lithium
    "Be": 9.012,   # Beryllium
    "B": 10.81,    # Boron
    "C": 12.01,    # Carbon
    "N": 14.01,    # Nitrogen
    "O": 16.00,    # Oxygen
    "F": 19.00,    # Fluorine
    "Ne": 20.18,   # Neon
    "Na": 22.99,   # Sodium
    "Mg": 24.31,   # Magnesium
    "Al": 26.98,   # Aluminum
    "Si": 28.09,   # Silicon
    "P": 30.97,    # Phosphorus
    "S": 32.06,    # Sulfur
    "Cl": 35.45,   # Chlorine
    "Ar": 39.95,   # Argon
    "K": 39.10,    # Potassium
    "Ca": 40.08,   # Calcium
    "Sc": 44.96,   # Scandium
    "Ti": 47.87,   # Titanium
    "V": 50.94,    # Vanadium
    "Cr": 52.00,   # Chromium
    "Mn": 54.94,   # Manganese
    "Fe": 55.85,   # Iron
    "Co": 58.93,   # Cobalt
    "Ni": 58.69,   # Nickel
    "Cu": 63.55,   # Copper
    "Zn": 65.39,   # Zinc
    "Ga": 69.72,   # Gallium
    "Ge": 72.64,   # Germanium
    "As": 74.92,   # Arsenic
    "Se": 78.96,   # Selenium
    "Br": 79.90,   # Bromine
    "Kr": 83.80,   # Krypton
    "Rb": 85.47,   # Rubidium
    "Sr": 87.62,   # Strontium
    "Y": 88.91,    # Yttrium
    "Zr": 91.22,   # Zirconium
    "Nb": 92.91,   # Niobium
    "Mo": 95.94,   # Molybdenum
    "Tc": 98.00,   # Technetium
    "Ru": 101.07,  # Ruthenium
    "Rh": 102.91,  # Rhodium
    "Pd": 106.42,  # Palladium
    "Ag": 107.87,  # Silver
    "Cd": 112.41,  # Cadmium
    "In": 114.82,  # Indium
    "Sn": 118.71,  # Tin
    "Sb": 121.76,  # Antimony
    "Te": 127.60,  # Tellurium
    "I": 126.90,   # Iodine
    "Xe": 131.29,  # Xenon
    "E": 0.0,      # Electron (for plasma calculations)
}

__all__ = ["ELEMENTAL_MOLAR_MASS"]
