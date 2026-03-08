"""
Example usage of the PyPep CEA (Chemical Equilibrium Analysis) module.

This script demonstrates various combustion calculations for rocket propulsion,
including common propellant combinations and custom mixtures.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pycea import CEA, Species


def example_hydrogen_oxygen():
    """Example: Hydrogen + Oxygen combustion (LH2/LOX)."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Hydrogen + Oxygen (LH2/LOX)")
    print("="*70)
    
    # Initialize CEA with chamber pressure of 30 bar
    cea = CEA(
        thermo_file="data/thermo.yaml",
        chamber_pressure=30e5,  # 30 bar = 3 MPa
        ambient_pressure=101325  # 1 atm sea level
    )
    
    # Add reactants with optimal O/F ratio ~8:1
    cea.add_reactants([
        Species("H2", mass=1.0, temperature=20.0),    # Liquid hydrogen at 20 K
        Species("O2", mass=8.0, temperature=90.0)     # Liquid oxygen at 90 K
    ])
    
    # Calculate and display results
    results = cea.equilibrate()
    cea.print_results(n_products=10)
    
    # Access specific results
    print(f"\nMixture ratio (O/F): {cea.get_mixture_ratio():.2f}")
    print(f"Expected Isp: ~450 s (Ideal: {results.isp:.1f} s)")


def example_methane_oxygen():
    """Example: Methane + Oxygen combustion (CH4/LOX)."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Methane + Oxygen (CH4/LOX)")
    print("="*70)
    
    cea = CEA(
        thermo_file="data/thermo.yaml",
        chamber_pressure=30e5,
        ambient_pressure=101325
    )
    
    # Methane/LOX with O/F ratio ~3.5:1
    cea.add_reactants([
        Species("CH4", mass=1.0, temperature=111.0),   # Liquid methane
        Species("O2", mass=3.5, temperature=90.0)      # Liquid oxygen
    ])
    
    results = cea.equilibrate()
    cea.print_results(n_products=10)
    
    print(f"\nMixture ratio (O/F): {cea.get_mixture_ratio():.2f}")
    print(f"Expected Isp: ~350 s (Ideal: {results.isp:.1f} s)")


def example_abs_n2o():
    """Example: ABS (plastic) + Nitrous Oxide hybrid rocket."""
    print("\n" + "="*70)
    print("EXAMPLE 3: ABS + N2O Hybrid Rocket")
    print("="*70)
    
    cea = CEA(
        thermo_file="data/thermo.yaml",
        chamber_pressure=10e5,  # 10 bar - typical for hybrids
        ambient_pressure=101325
    )
    
    # ABS plastic fuel with N2O oxidizer, O/F ratio ~6:1
    cea.add_reactants([
        Species("ABS", mass=1.0, temperature=298.15),  # ABS at room temp
        Species("N2O", mass=6.0, temperature=298.15)   # Nitrous oxide at room temp
    ])
    
    results = cea.equilibrate()
    cea.print_results(n_products=10)
    
    print(f"\nMixture ratio (O/F): {cea.get_mixture_ratio():.2f}")
    print(f"Typical hybrid Isp: ~250 s (Ideal: {results.isp:.1f} s)")


def example_aluminum_oxygen():
    """Example: Aluminum + Oxygen combustion (solid rocket booster)."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Aluminum + Oxygen (Metallized Propellant)")
    print("="*70)
    
    cea = CEA(
        thermo_file="data/thermo.yaml",
        chamber_pressure=50e5,  # 50 bar - high pressure solid rocket
        ambient_pressure=101325
    )
    
    # Aluminum powder with oxygen
    cea.add_reactants([
        Species("AL", mass=1.0, temperature=298.15),
        Species("O2", mass=1.5, temperature=298.15)
    ])
    
    results = cea.equilibrate()
    cea.print_results(n_products=10)
    
    print(f"\nNote: Aluminum combustion produces very high temperatures")
    print(f"and can form condensed phase products (Al2O3 particles).")


def example_pressure_study():
    """Example: Study effect of chamber pressure on performance."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Chamber Pressure Study (H2/O2)")
    print("="*70)
    
    pressures = [10e5, 20e5, 30e5, 50e5, 100e5]  # 10, 20, 30, 50, 100 bar
    
    print("\nPressure (bar) | Isp (s) | c* (m/s) | Cf")
    print("-" * 50)
    
    for p in pressures:
        cea = CEA(
            thermo_file="data/thermo.yaml",
            chamber_pressure=p,
            ambient_pressure=101325
        )
        
        cea.add_reactants([
            Species("H2", mass=1.0, temperature=20.0),
            Species("O2", mass=8.0, temperature=90.0)
        ])
        
        results = cea.equilibrate()
        
        print(f"{p/1e5:13.0f} | {results.isp:7.1f} | {results.c_star:8.1f} | {results.Cf:.4f}")


def example_custom_propellant():
    """Example: Custom multi-component propellant."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Custom Multi-Component Propellant")
    print("="*70)
    
    cea = CEA(
        thermo_file="data/thermo.yaml",
        chamber_pressure=30e5,
        ambient_pressure=101325
    )
    
    # Triple-base propellant with multiple components
    cea.add_reactants([
        Species("C3H8", mass=0.5, temperature=298.15),    # Propane
        Species("NH3", mass=0.3, temperature=298.15),     # Ammonia
        Species("O2", mass=2.0, temperature=90.0),        # Oxygen
        Species("N2O", mass=1.0, temperature=298.15)      # Nitrous oxide
    ])
    
    results = cea.equilibrate()
    cea.print_results(n_products=15)


def main():
    """Run all examples."""
    print("\n" + "█"*70)
    print("pycea - Chemical Equilibrium Analysis Examples")
    print("█"*70)
    
    # Run examples
    example_hydrogen_oxygen()
    example_methane_oxygen()
    example_abs_n2o()
    example_aluminum_oxygen()
    example_pressure_study()
    example_custom_propellant()
    
    print("\n" + "█"*70)
    print("All examples completed!")
    print("█"*70 + "\n")


if __name__ == "__main__":
    main()
