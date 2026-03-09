"""
Rocket Chemical Equilibrium Analysis (CEA) Module.

This module provides a simplified interface for performing chemical equilibrium
calculations with rocket performance parameters using Cantera and 
Rocketry_formulas.

Classes:
    Species: Represents a chemical species with mass and temperature.
    Results: Stores equilibrium calculation results and rocket performance.
    CEA: Main calculator for chemical equilibrium analysis.

Example:
    >>> from pycea.core.rocket_cea import CEA, Species
    >>> 
    >>> # Initialize CEA calculator
    >>> cea = CEA(
    ...     thermo_file="gri30.yaml",
    ...     chamber_pressure=30e5,  # 30 bar
    ...     ambient_pressure=101325  # 1 atm
    ... )
    >>> 
    >>> # Add reactants
    >>> cea.add_reactants([
    ...     Species("H2", mass=1.0, temperature=298.15),
    ...     Species("O2", mass=8.0, temperature=298.15)
    ... ])
    >>> 
    >>> # Calculate equilibrium
    >>> results = cea.equilibrate()
    >>> cea.print_results()
"""

from typing import List, Optional
import numpy as np
import cantera as ct
from scipy.constants import R
import Rocketry_formulas as rf

from .constants import ELEMENTAL_MOLAR_MASS


class Species:
    """
    Represents a chemical species with mass and temperature.
    
    This class is used to define reactants for equilibrium calculations,
    allowing specification of different temperatures for different species
    (e.g., cryogenic oxidizer and ambient fuel).
    
    Attributes:
        name (str): Chemical formula or species name (e.g., 'H2O', 'O2', 'CH4').
        mass (float): Mass of the species in kg. Default is 1.0.
        temperature (float): Temperature of the species in Kelvin. Default is 298.15 K.
    
    Example:
        >>> lox = Species("O2", mass=8.0, temperature=90.0)  # Liquid oxygen
        >>> fuel = Species("CH4", mass=1.0, temperature=298.15)  # Methane at ambient
    """
    
    def __init__(self, name: str, mass: float = 1.0, temperature: float = 298.15) -> None:
        """
        Initialize a chemical species.
        
        Args:
            name: Chemical formula or species name.
            mass: Mass of the species in kg.
            temperature: Temperature of the species in Kelvin.
        
        Raises:
            ValueError: If mass is negative or temperature is below absolute zero.
        """
        if mass < 0:
            raise ValueError(f"Mass must be non-negative, got {mass}")
        if temperature < 0:
            raise ValueError(f"Temperature must be non-negative, got {temperature} K")
        
        self.name: str = name
        self.mass: float = mass
        self.temperature: float = temperature
    
    def __repr__(self) -> str:
        return f"Species(name='{self.name}', mass={self.mass}, temperature={self.temperature})"


class Results:
    """
    Stores equilibrium calculation results and rocket performance parameters.
    
    This class encapsulates all thermodynamic properties and rocket performance
    metrics calculated from a combustion equilibrium analysis.
    
    Attributes:
        solution (ct.Solution): Cantera solution object at equilibrium.
        T (float): Adiabatic flame temperature in K.
        k (float): Isentropic exponent (gamma = Cp/Cv).
        M (float): Mean molecular weight in kg/mol.
        Rs (float): Specific gas constant in J/(kg·K).
        p_ch (float): Chamber pressure in Pa.
        p_a (float): Ambient pressure in Pa.
        c_star (float): Characteristic velocity in m/s.
        exp_ratio (float): Expansion ratio (dimensionless).
        Cf (float): Thrust coefficient (dimensionless).
        v_e (float): Exhaust velocity in m/s.
        isp (float): Specific impulse in seconds.
    """
    
    def __init__(
        self,
        solution: ct.Solution,
        chamber_pressure: float,
        ambient_pressure: float
    ) -> None:
        """
        Initialize results from equilibrium solution.
        
        Args:
            solution: Cantera Solution object at equilibrium state.
            chamber_pressure: Chamber pressure in Pa.
            ambient_pressure: Ambient/atmospheric pressure in Pa.
        """
        self.solution = solution
        
        # Thermodynamic properties
        self.T: float = solution.T  # Adiabatic flame temperature (K)
        self.k: float = solution.cp_mass / solution.cv_mass  # Isentropic exponent
        self.M: float = solution.mean_molecular_weight / 1000  # Molecular weight (kg/mol)
        self.p_ch: float = chamber_pressure  # Chamber pressure (Pa)
        self.p_a: float = ambient_pressure  # Ambient pressure (Pa)
        
        # Rocket performance parameters
        self.c_star: float = self._calculate_c_star()  # Characteristic velocity (m/s)
        self.exp_ratio: float = (self.p_ch / self.p_a) ** ((self.k - 1) / self.k)
        self.Cf: float = self._calculate_thrust_coefficient()  # Thrust coefficient
        self.v_e: float = self._calculate_exhaust_velocity()  # Exhaust velocity (m/s)
        self.isp: float = self._calculate_isp()  # Specific impulse (s)
    
    @property
    def Rs(self) -> float:
        """Specific gas constant in J/(kg·K)."""
        return R / self.M
    
    def _calculate_c_star(self) -> float:
        """
        Calculate characteristic velocity (c*) in m/s.
        
        c* is a measure of combustion efficiency independent of nozzle design.
        
        Returns:
            Characteristic velocity in m/s.
        """
        return rf.calculate_cstar_ideal(self.k, self.Rs, self.T)
    
    def _calculate_exhaust_velocity(self) -> float:
        """
        Calculate ideal exhaust velocity in m/s.
        
        The exhaust velocity depends on chamber conditions, ambient pressure,
        and thermodynamic properties of the exhaust gases.
        
        Returns:
            Exhaust velocity in m/s.
        """
        return rf.calculate_velocity_exhaust(
            self.k, self.Rs, self.T, self.p_ch, self.p_a
        )
    
    def _calculate_thrust_coefficient(self) -> float:
        """
        Calculate thrust coefficient (Cf).
        
        Cf relates thrust to chamber pressure and throat area.
        
        Returns:
            Thrust coefficient (dimensionless).
        """
        return rf.calculate_Cf_ideal(self.k, self.p_ch, self.p_a)
    
    def _calculate_isp(self) -> float:
        """
        Calculate specific impulse (Isp) in seconds.
        
        Isp is the most important performance metric for rocket engines,
        representing thrust per unit weight flow rate.
        
        Returns:
            Specific impulse in seconds.
        """
        return rf.calculate_isp_ideal(
            self.k, self.Rs, self.T, self.p_ch, self.p_a
        )
    
    def get_top_products(self, n: int = 10) -> List[tuple]:
        """
        Get the top n combustion products by mass fraction.
        
        Args:
            n: Number of top products to return.
        
        Returns:
            List of (species_name, mass_fraction) tuples.
        """
        sorted_idx = np.argsort(self.solution.Y)[::-1]
        return [
            (self.solution.species_names[idx], self.solution.Y[idx])
            for idx in sorted_idx[:n]
        ]
    
    def get_all_products(self) -> dict:
        """
        Get all combustion products with non-zero mass fractions.
        
        Returns:
            Dictionary mapping species names to mass fractions.
        """
        return {
            name: self.solution.Y[i]
            for i, name in enumerate(self.solution.species_names)
            if self.solution.Y[i] > 1e-10
        }


class CEA:
    """
    Chemical Equilibrium Analysis (CEA) calculator using Cantera.
    
    This class provides a simplified interface for rocket combustion equilibrium
    calculations, including thermodynamic properties and performance parameters.
    
    The calculator:
    - Loads species from a thermodynamic database (YAML format)
    - Accepts multiple reactants with different temperatures
    - Performs equilibrium calculation at constant enthalpy and pressure (HP)
    - Calculates rocket performance metrics (c*, Isp, Cf, etc.)
    
    Attributes:
        thermo_file (str): Path to thermodynamic database file.
        chamber_pressure (float): Chamber pressure in Pa.
        ambient_pressure (float): Ambient pressure in Pa.
        species_all (list): List of all available species from database.
        reactants (list): List of Species objects representing reactants.
        results (Results): Results object after equilibration (None before).
    
    Example:
        >>> cea = CEA(
        ...     thermo_file="gri30.yaml",
        ...     chamber_pressure=30e5,
        ...     ambient_pressure=101325
        ... )
        >>> cea.add_reactants([
        ...     Species("H2", mass=1.0),
        ...     Species("O2", mass=8.0)
        ... ])
        >>> results = cea.equilibrate()
        >>> print(f"Isp: {results.isp:.1f} s")
    """
    
    def __init__(
        self,
        chamber_pressure: float = 10e5,
        ambient_pressure: float = 101325,
        thermo_file: str = "../data/thermo.yaml"
    ) -> None:
        """
        Initialize Chemical Equilibrium Analysis calculator.
        
        Args:
            thermo_file: Path to thermodynamic database in YAML format.
            chamber_pressure: Chamber (combustion) pressure in Pa.
            ambient_pressure: Ambient/atmospheric pressure in Pa.
        
        Raises:
            FileNotFoundError: If thermo_file does not exist.
            ValueError: If pressures are not positive.
        """
        if chamber_pressure <= 0:
            raise ValueError(f"Chamber pressure must be positive, got {chamber_pressure} Pa")
        if ambient_pressure <= 0:
            raise ValueError(f"Ambient pressure must be positive, got {ambient_pressure} Pa")
        
        self.thermo_file: str = thermo_file
        self.chamber_pressure: float = chamber_pressure
        self.ambient_pressure: float = ambient_pressure
        
        # Load all available species from thermodynamic database
        try:
            self.species_all: List = ct.Species.list_from_file(thermo_file)
        except Exception as e:
            raise FileNotFoundError(
                f"Could not load thermodynamic database '{thermo_file}': {e}"
            )
        
        self.reactants: List[Species] = []
        self.results: Optional[Results] = None
    
    def add_reactant(self, species: Species) -> None:
        """
        Add a single reactant species.
        
        Args:
            species: Species object to add as reactant.
        """
        self.reactants.append(species)
    
    def add_reactants(self, species_list: List[Species]) -> None:
        """
        Add multiple reactant species.
        
        Args:
            species_list: List of Species objects to add as reactants.
        """
        self.reactants.extend(species_list)
    
    def clear_reactants(self) -> None:
        """Clear all reactants from the calculator."""
        self.reactants = []
    
    def _get_molar_mass(self, species_name: str) -> Optional[float]:
        """
        Calculate molar mass of a species from its elemental composition.
        
        Args:
            species_name: Name of the species.
        
        Returns:
            Molar mass in g/mol, or None if species not found.
        """
        for sp in self.species_all:
            if sp.name == species_name:
                mass = 0.0
                for element, count in sp.composition.items():
                    mass += ELEMENTAL_MOLAR_MASS.get(element, 0.0) * count
                return mass
        return None
    
    def equilibrate(self) -> Results:
        """
        Perform equilibrium calculation at constant enthalpy and pressure.
        
        The calculation:
        1. Determines elements present in all reactants
        2. Filters species database to only relevant species
        3. Creates an ideal gas solution with filtered species
        4. Sets initial composition from reactant masses
        5. Equilibrates at constant H and P
        6. Calculates rocket performance parameters
        
        Returns:
            Results object containing all equilibrium properties and 
            rocket performance parameters.
        
        Raises:
            ValueError: If no reactants have been added or no compatible 
                       species are found.
        """
        if not self.reactants:
            raise ValueError("No reactants added. Use add_reactant() or add_reactants().")
        
        # Determine elemental composition from all reactants
        elements = set()
        for reactant in self.reactants:
            species_found = False
            for sp in self.species_all:
                if sp.name == reactant.name:
                    for element in sp.composition:
                        elements.add(element)
                    species_found = True
                    break
            
            if not species_found:
                print(f"Warning: Reactant '{reactant.name}' not found in database")
        
        if not elements:
            raise ValueError("No valid elements found in reactants")
        
        # Filter species to only those containing reactant elements
        possible_species = [
            sp for sp in self.species_all
            if set(sp.composition) <= elements
        ]
        
        if not possible_species:
            raise ValueError(
                "No compatible species found for equilibrium calculation. "
                "Check that your thermodynamic database contains species "
                "with the elements in your reactants."
            )
        
        # Create ideal gas phase solution
        gas = ct.Solution(
            thermo="ideal-gas",
            species=possible_species
        )
        
        # Set up species composition from reactants (convert mass to moles)
        species_moles = np.zeros(gas.n_species)
        for reactant in self.reactants:
            try:
                species_idx = gas.species_index(reactant.name)
                molar_mass = self._get_molar_mass(reactant.name)
                
                if molar_mass and molar_mass > 0:
                    moles = reactant.mass / molar_mass
                    species_moles[species_idx] = moles
                else:
                    print(
                        f"Warning: Could not calculate molar mass for '{reactant.name}'"
                    )
            except ValueError:
                print(f"Warning: '{reactant.name}' not in filtered species list")
        
        if np.sum(species_moles) == 0:
            raise ValueError("Total moles of reactants is zero. Check species names and masses.")
        
        # Set initial state
        gas.X = species_moles
        avg_temp = np.mean([r.temperature for r in self.reactants])
        gas.TP = avg_temp, self.chamber_pressure
        
        # Equilibrate at constant enthalpy and pressure
        try:
            gas.equilibrate("HP")
        except Exception as e:
            raise RuntimeError(
                f"Equilibration failed: {e}. "
                "This may be due to invalid species, extreme conditions, "
                "or numerical convergence issues."
            )
        
        # Create and store results
        self.results = Results(gas, self.chamber_pressure, self.ambient_pressure)
        return self.results
    
    def print_results(self, n_products: int = 10) -> None:
        """
        Print formatted equilibrium results and rocket performance.
        
        Args:
            n_products: Number of top products to display by mass fraction.
        
        Raises:
            ValueError: If equilibrate() has not been called yet.
        """
        if self.results is None:
            raise ValueError(
                "No equilibrium calculation performed yet. Call equilibrate() first."
            )
        
        res = self.results
        
        print("=" * 70)
        print("CHEMICAL EQUILIBRIUM ANALYSIS RESULTS")
        print("=" * 70)
        print()
        print("THERMODYNAMIC PROPERTIES:")
        print(f"  Adiabatic Flame Temperature:  {res.T:.2f} K")
        print(f"  Chamber Pressure:             {res.p_ch:.2e} Pa ({res.p_ch/1e5:.1f} bar)")
        print(f"  Ambient Pressure:             {res.p_a:.2e} Pa ({res.p_a/1e5:.1f} bar)")
        print(f"  Isentropic Exponent (γ):      {res.k:.4f}")
        print(f"  Molecular Weight:             {res.M*1000:.2f} g/mol")
        print(f"  Specific Gas Constant (Rs):   {res.Rs:.2f} J/(kg·K)")
        print()
        print("ROCKET PERFORMANCE:")
        print(f"  Characteristic Velocity (c*): {res.c_star:.2f} m/s")
        print(f"  Exhaust Velocity (ve):        {res.v_e:.2f} m/s")
        print(f"  Thrust Coefficient (Cf):      {res.Cf:.4f}")
        print(f"  Specific Impulse (Isp):       {res.isp:.1f} s")
        print(f"  Expansion Ratio:              {res.exp_ratio:.2f}")
        print("=" * 70)
        
        # Show top products by mass fraction
        top_products = res.get_top_products(n_products)
        print(f"\nTop {n_products} Products by Mass Fraction:")
        for i, (name, mass_frac) in enumerate(top_products, 1):
            print(f"  {i:2d}. {name:15s}  {mass_frac:.6e}")
        print()
    
    def get_mixture_ratio(self) -> Optional[float]:
        """
        Calculate oxidizer-to-fuel mass ratio (O/F ratio).
        
        This is a simplified calculation that assumes the first reactant
        is fuel and subsequent reactants are oxidizers.
        
        Returns:
            O/F ratio, or None if fewer than 2 reactants.
        """
        if len(self.reactants) < 2:
            return None
        
        fuel_mass = self.reactants[0].mass
        oxidizer_mass = sum(r.mass for r in self.reactants[1:])
        
        return oxidizer_mass / fuel_mass if fuel_mass > 0 else None


__all__ = ["Species", "Results", "CEA"]
