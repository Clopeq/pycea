# pycea CEA Examples

This directory contains example scripts demonstrating the use of pycea's Chemical Equilibrium Analysis (CEA) module for rocket propulsion calculations.

## Quick Start

```python
from pycea import CEA, Species

# Initialize calculator
cea = CEA(
    thermo_file="data/thermo.yaml",
    chamber_pressure=30e5,      # 30 bar
    ambient_pressure=101325      # 1 atm
)

# Add reactants
cea.add_reactants([
    Species("H2", mass=1.0, temperature=20.0),    # Liquid hydrogen
    Species("O2", mass=8.0, temperature=90.0)     # Liquid oxygen
])

# Calculate equilibrium
results = cea.equilibrate()

# Display results
cea.print_results()

# Access specific values
print(f"Specific Impulse: {results.isp:.1f} s")
print(f"Exhaust Velocity: {results.v_e:.1f} m/s")
```

## Examples

### `cea_examples.py`

Comprehensive examples demonstrating various propellant combinations:

1. **Hydrogen + Oxygen (LH2/LOX)** - Classic high-performance propellant
2. **Methane + Oxygen (CH4/LOX)** - Modern reusable rocket propellant
3. **ABS + N2O** - Hybrid rocket propellant
4. **Aluminum + Oxygen** - Metallized solid propellant
5. **Pressure Study** - Effect of chamber pressure on performance
6. **Custom Multi-Component** - Complex propellant mixtures

### Running the Examples

```bash
# From the pycea root directory
python examples/cea_examples.py
```

Or run individual examples:

```python
from examples.cea_examples import example_hydrogen_oxygen
example_hydrogen_oxygen()
```

## Key Classes

### `Species`
Represents a chemical reactant with mass and temperature.

**Parameters:**
- `name` (str): Chemical formula (e.g., 'H2', 'O2', 'CH4')
- `mass` (float): Mass in kg (default: 1.0)
- `temperature` (float): Temperature in K (default: 298.15)

### `CEA`
Main calculator for chemical equilibrium analysis.

**Parameters:**
- `thermo_file` (str): Path to thermodynamic database (YAML)
- `chamber_pressure` (float): Chamber pressure in Pa
- `ambient_pressure` (float): Ambient pressure in Pa (default: 101325)

**Methods:**
- `add_reactant(species)`: Add single reactant
- `add_reactants(species_list)`: Add multiple reactants
- `equilibrate()`: Perform equilibrium calculation
- `print_results(n_products)`: Display formatted results

### `Results`
Contains all equilibrium properties and rocket performance parameters.

**Key Attributes:**
- `T`: Adiabatic flame temperature (K)
- `k`: Isentropic exponent (gamma)
- `M`: Molecular weight (kg/mol)
- `isp`: Specific impulse (s)
- `v_e`: Exhaust velocity (m/s)
- `c_star`: Characteristic velocity (m/s)
- `Cf`: Thrust coefficient

## Common Propellant Combinations

| Propellant | O/F Ratio | Chamber Pressure | Typical Isp (s) |
|------------|-----------|------------------|-----------------|
| H2/O2 (LOX) | 6-8 | 20-50 bar | 430-460 |
| RP-1/O2 | 2.5-3 | 20-40 bar | 300-350 |
| CH4/O2 | 3-4 | 20-40 bar | 350-380 |
| N2O/HTPB | 6-8 | 10-20 bar | 230-260 |
| ABS/N2O | 5-7 | 10-15 bar | 240-270 |

## Tips for Accurate Calculations

1. **Use appropriate thermodynamic database**: Ensure all species are present
2. **Set realistic temperatures**: Use actual propellant storage temperatures
3. **Match chamber pressure**: Use typical operating pressures for your engine
4. **Check O/F ratio**: Compare with literature values for validation
5. **Verify convergence**: Check that equilibration completes successfully

## Thermodynamic Databases

pycea uses Cantera-compatible YAML thermodynamic databases. The default `thermo.yaml` should contain:

- Common gas species (H2, O2, N2, CO2, H2O, etc.)
- Combustion products (CO, OH, H, O, etc.)
- Specialized species (N2O, H2O2, ABS, etc.)
- NASA polynomial coefficients for enthalpy and entropy

### Creating Custom Databases

To add custom species, edit `thermo.yaml` following the Cantera format:

```yaml
species:
- name: MY_SPECIES
  composition: {C: 1, H: 4}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [coefficients for low T range]
    - [coefficients for high T range]
```

## Troubleshooting

**"Species not found in database"**
- Check species name spelling matches database exactly
- Verify species exists in your thermo.yaml file

**"No compatible species found"**
- Ensure database contains species with elements from your reactants
- Check that required combustion products are available

**"Equilibration failed"**
- Try more moderate initial conditions
- Verify species names and masses are correct
- Check for typos in chemical formulas

**Unrealistic results**
- Validate O/F ratio against literature
- Verify chamber pressure is reasonable
- Check that all species have correct thermodynamic data

## Further Reading

- [NASA CEA Documentation](https://www1.grc.nasa.gov/research-and-engineering/ceaweb/)
- [Cantera Documentation](https://cantera.org/)
- [Rocket Propulsion Elements by Sutton](https://www.wiley.com/en-us/Rocket+Propulsion+Elements%2C+9th+Edition-p-9781118753910)

## Contributing

To add more examples:

1. Create a new function in `cea_examples.py`
2. Follow the naming pattern: `example_<descriptive_name>()`
3. Include print statements explaining the setup
4. Document expected results and typical ranges
5. Add to `main()` function

## License

See main pycea LICENSE file.
