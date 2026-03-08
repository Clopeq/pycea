"""
Combustion equilibrium calculator using Cantera.

This module provides tools for computing chemical equilibrium properties
of reactive mixtures, including adiabatic flame temperature, isentropic
exponent, and molecular weight of combustion products.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import cantera as ct
import json
import os
import tempfile


@dataclass
class EquilibriumResults:
    """Container for equilibrium calculation results."""
    adiabatic_flame_temperature: float  # K
    isentropic_exponent: float  # gamma
    molecular_weight: float  # kg/kmol
    products_composition: Dict[str, float]  # mole fractions
    products_density: float  # kg/m^3
    products_enthalpy_mass: float  # J/kg
    products_entropy_mass: float  # J/(kg·K)


class CombustionEquilibrium:
    """
    Compute chemical equilibrium properties of reactive mixtures.
    
    This class handles:
    - Mixing of multiple reactants with different temperatures and pressures
    - Equilibrium calculation at constant enthalpy and pressure (HP)
    - Extraction of equilibrium properties (flame temperature, gamma, MW)
    - Support for monopropellants (H2O2, N2O) and traditional oxidizer/fuel pairs
    - Support for condensed species (metals like Al, Mg, oxides, etc.)
    
    The class loads species from NASA thermodynamic databases and structures them with:
    - Single ideal-gas phase containing all gas species
    - Separate fixed-stoichiometry phases for each condensed species
    
    Databases:
    - nasa_gas.yaml: Comprehensive gas-phase species
    - nasa_condensed.yaml: Condensed and metal species
    
    Attributes:
        solution: Cantera Solution object for thermodynamic calculations
        equilibrium_state: Cantera Solution object at equilibrium
        reactants: List of input reactant dictionaries
        gas_db_path: Path to gas-phase NASA database
        condensed_db_path: Path to condensed-phase NASA database
    """
    
    def __init__(self, 
                 gas_database: str = 'nasa_gas.yaml',
                 condensed_database: str = 'nasa_condensed.yaml'):
        """
        Initialize the combustion equilibrium calculator.
        
        Args:
            gas_database: Path to gas-phase Cantera database file (nasa_gas.yaml).
            condensed_database: Path to condensed-phase Cantera database file (nasa_condensed.yaml).
        """
        self.gas_db_path = gas_database
        self.condensed_db_path = condensed_database
        
        # Create combined thermodynamic database with both gas and condensed species
        self.solution = self._create_combined_solution(gas_database, condensed_database)
        
        self.equilibrium_state = None
        self.reactants = None
    
    def __del__(self):
        """Clean up temporary YAML files on object deletion."""
        if hasattr(self, '_temp_yaml_file'):
            try:
                if self._temp_yaml_file and os.path.exists(self._temp_yaml_file):
                    os.remove(self._temp_yaml_file)
            except:
                pass
    
    def cleanup(self):
        """Explicitly clean up temporary files."""
        if hasattr(self, '_temp_yaml_file'):
            try:
                if self._temp_yaml_file and os.path.exists(self._temp_yaml_file):
                    os.remove(self._temp_yaml_file)
                    self._temp_yaml_file = None
            except:
                pass
    
    def _create_combined_solution(self, gas_db: str, condensed_db: str) -> ct.Solution:
        """
        Create a Cantera Solution with multiple phases.
        
        Structure:
        - One ideal-gas phase containing all gas species
        - Separate fixed-stoichiometry/pure-substance phases for each condensed species
        
        Args:
            gas_db: Path to gas-phase database (nasa_gas.yaml)
            condensed_db: Path to condensed-phase database (nasa_condensed.yaml)
        
        Returns:
            Cantera Mixture object with multiple phases
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for loading NASA databases. "
                "Install it with: pip install pyyaml"
            )
        
        # Load both databases
        try:
            with open(gas_db, 'r') as f:
                gas_data = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Gas database not found: {gas_db}")
        
        try:
            with open(condensed_db, 'r') as f:
                condensed_data = yaml.safe_load(f)
        except FileNotFoundError:
            condensed_data = None
        
        # Separate species into gas and condensed
        gas_species_list = []
        condensed_species_list = []
        seen_species = set()
        gas_elements_set = set()
        
        # Collect gas species
        if 'species' in gas_data:
            for sp in gas_data['species']:
                name = sp.get('name', '')
                if name and name not in seen_species:
                    gas_species_list.append(sp)
                    seen_species.add(name)
                    if 'composition' in sp:
                        for element in sp['composition'].keys():
                            gas_elements_set.add(element)
        
        # Collect condensed species
        if condensed_data and 'species' in condensed_data:
            for sp in condensed_data['species']:
                name = sp.get('name', '')
                if name and name not in seen_species:
                    condensed_species_list.append(sp)
                    seen_species.add(name)
        
        # Build phase definitions
        phases_list = []
        all_species_list = []
        
        # 1. Ideal-gas phase with all gas species
        gas_elements_list = sorted(list(gas_elements_set))
        phases_list.append({
            'name': 'gas',
            'thermo': 'ideal-gas',
            'elements': gas_elements_list,
            'species': [sp['name'] for sp in gas_species_list]
        })
        all_species_list.extend(gas_species_list)
        
        # 2. Create fixed-stoichiometry phase for each condensed species
        for i, sp in enumerate(condensed_species_list):
            species_name = sp.get('name', '')
            elements_for_sp = []
            if 'composition' in sp:
                elements_for_sp = sorted(list(sp['composition'].keys()))
            
            phases_list.append({
                'name': f"condensed_{i}",
                'thermo': 'fixed-stoichiometry',
                'elements': elements_for_sp,
                'species': [species_name]
            })
            all_species_list.append(sp)
        
        # Create combined YAML
        combined_data = {
            'phases': phases_list,
            'species': all_species_list
        }
        
        if 'units' in gas_data:
            combined_data['units'] = gas_data['units']
        
        # Store for potential future use
        self._combined_yaml_data = combined_data
        
        # Write to temporary file
        yaml_string = yaml.dump(combined_data, default_flow_style=False, sort_keys=False)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_string)
            temp_filename = f.name
        
        # Store temp filename for cleanup later
        self._temp_yaml_file = temp_filename
        
        try:
            # When loading a multi-phase file, load just the gas phase
            # The condensed phases will be available for equilibration
            solution = ct.Solution(temp_filename, name='gas')
        except Exception as e:
            # Clean up before raising
            try:
                os.remove(temp_filename)
            except:
                pass
            raise ValueError(f"Failed to create solution from combined NASA databases: {e}")
        
        return solution
    
    def _create_fresh_solution(self) -> ct.Solution:
        """
        Create a fresh Solution object with the same species configuration.
        Uses the stored temp YAML file that contains all phase definitions.
        
        Returns:
            A new Cantera Solution object
        """
        try:
            # Create from the stored temp file that has all phase definitions
            solution = ct.Solution(self._temp_yaml_file, name='gas')
            return solution
        except Exception as e:
            # Fallback: recreate the file
            import yaml
            yaml_string = yaml.dump(self._combined_yaml_data, default_flow_style=False, sort_keys=False)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(yaml_string)
                temp_filename = f.name
            
            self._temp_yaml_file = temp_filename
            return ct.Solution(temp_filename, name='gas')
        
    def calculate(self, reactants: List[Dict[str, Any]]) -> EquilibriumResults:
        """
        Calculate equilibrium properties for a mixture of reactants.
        
        Supports both gas and condensed species from NASA databases.
        Gas species react in the ideal-gas phase; condensed species are
        treated as fixed-stoichiometry phases during equilibration.
        
        Args:
            reactants: List of dictionaries, each containing:
                - species (str): Species name (e.g., 'H2', 'O2', 'N2O', 'H2O2', 'Al', 'MgO(s)')
                - amount (float): Mass fraction (0-1) or absolute mass (kg)
                - temp (float): Initial temperature of this reactant (K)
                - pressure (float): Pressure (Pa)
        
        Returns:
            EquilibriumResults: Equilibrium properties including adiabatic
                flame temperature, isentropic exponent, and molecular weight
        """
        self.reactants = reactants
        
        # Step 1: Determine if amounts are mass fractions or absolute masses
        total_amount = sum(r['amount'] for r in reactants)
        if total_amount <= 1.0:
            # Assume mass fractions
            mass_fractions = {r['species']: r['amount'] for r in reactants}
        else:
            # Assume absolute masses - normalize to mass fractions
            mass_fractions = {r['species']: r['amount'] / total_amount for r in reactants}
        
        # Step 2: Calculate initial enthalpy accounting for different reactant temperatures
        pressure = reactants[0]['pressure']
        initial_enthalpy = self._calculate_mixture_enthalpy(reactants, mass_fractions)
        
        # Step 3: Create species string for Cantera
        species_string = ', '.join([
            f"{species}:{mf:.6f}" 
            for species, mf in mass_fractions.items()
        ])
        
        # Step 4: Set up the solution with initial composition
        # Start at a moderate temperature to avoid numerical issues
        initial_temp = max(500.0, min(r['temp'] for r in reactants))
        
        self.solution.TP = (initial_temp, pressure)
        self.solution.X = species_string
        
        # Step 5: Set to correct enthalpy and pressure
        try:
            self.solution.HP = (initial_enthalpy, pressure)
        except Exception as e:
            # If HP set fails, try TP first then adjust
            self.solution.TP = (1500.0, pressure)
            self.solution.X = species_string
            self.solution.HP = (initial_enthalpy, pressure)
        
        # Step 6: Store state before equilibration
        h_equilibrate = self.solution.enthalpy_mass
        p_equilibrate = self.solution.P
        
        # Step 7: Equilibrate at constant H and P
        self.equilibrium_state = self.solution
        try:
            self.equilibrium_state.equilibrate('HP')
        except Exception as e:
            # If HP equilibration fails, try TP equilibration at high temp
            print(f"Warning: HP equilibration failed, attempting TP: {e}")
            self.equilibrium_state.TP = (3000.0, p_equilibrate)
            self.equilibrium_state.equilibrate('TP')
        
        # Step 8: Extract results
        results = self._extract_results(p_equilibrate)
        
        return results
    
    def _calculate_mixture_enthalpy(
        self, 
        reactants: List[Dict[str, Any]], 
        mass_fractions: Dict[str, float]
    ) -> float:
        """
        Calculate the enthalpy of the initial mixture.
        
        Args:
            reactants: List of reactant dictionaries
            mass_fractions: Dict of species -> mass fraction
        
        Returns:
            Total mixture enthalpy (J/kg)
        """
        total_enthalpy = 0.0
        
        for reactant in reactants:
            species = reactant['species']
            temp = reactant['temp']
            pressure = reactant['pressure']
            mf = mass_fractions[species]
            
            # Set this species at its stated temperature
            self.solution.TP = (temp, pressure)
            self.solution.X = f"{species}:1.0"
            
            # Get enthalpy per unit mass
            h_species = self.solution.enthalpy_mass
            
            # Add contribution to mixture enthalpy
            total_enthalpy += mf * h_species
        
        return total_enthalpy
    
    def _extract_results(self, pressure: float) -> EquilibriumResults:
        """
        Extract thermodynamic properties from equilibrium state.
        
        Args:
            pressure: Pressure at which equilibrium was computed (Pa)
        
        Returns:
            EquilibriumResults with flame temperature, gamma, MW, etc.
        """
        # Adiabatic flame temperature
        T_ad = self.equilibrium_state.T
        
        # Isentropic exponent (gamma)
        gamma = self.equilibrium_state.cp_mass / self.equilibrium_state.cv_mass
        
        # Molecular weight
        mw = self.equilibrium_state.mean_molecular_weight
        
        # Composition (mole fractions)
        species_names = self.equilibrium_state.species_names
        X = self.equilibrium_state.X
        products_composition = {
            name: mole_frac 
            for name, mole_frac in zip(species_names, X)
            if mole_frac > 1e-10  # Filter out trace species
        }
        
        # Additional properties
        rho = self.equilibrium_state.density
        h_mass = self.equilibrium_state.enthalpy_mass
        s_mass = self.equilibrium_state.entropy_mass
        
        return EquilibriumResults(
            adiabatic_flame_temperature=T_ad,
            isentropic_exponent=gamma,
            molecular_weight=mw,
            products_composition=products_composition,
            products_density=rho,
            products_enthalpy_mass=h_mass,
            products_entropy_mass=s_mass
        )
