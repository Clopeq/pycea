# pycea

`pycea` is a Python package for rocket-oriented chemical equilibrium analysis using Cantera.

It provides a clean API to compute:
- adiabatic flame temperature
- equilibrium product composition
- isentropic exponent and molecular weight
- rocket performance metrics (`c*`, `Cf`, exhaust velocity, `Isp`)

## Installation

```bash
pip install git+https://github.com/Clopeq/PyPep3.git
```

Note: the repository URL currently contains `PyPep3`, but the package/import name is `pycea`.

## Requirements

- Python 3.9+
- `numpy`
- `scipy`
- `cantera`
- `Rocketry_formulas`

## Quick Start

```python
from pycea import CEA, Species

cea = CEA(
    thermo_file="gri30.yaml",   # Cantera built-in mechanism
    chamber_pressure=30e5,       # 30 bar
    ambient_pressure=101325      # 1 atm
)

cea.add_reactants([
    Species("H2", mass=1.0, temperature=20.0),
    Species("O2", mass=8.0, temperature=90.0)
])

results = cea.equilibrate()
cea.print_results()

print(f"Isp: {results.isp:.1f} s")
print(f"Flame temperature: {results.T:.1f} K")
```

## Main API

### `Species`
Represents one reactant stream.

```python
Species(name: str, mass: float = 1.0, temperature: float = 298.15)
```

### `CEA`
Main equilibrium calculator.

```python
CEA(
    thermo_file: str = "gri30.yaml",
    chamber_pressure: float = 1e5,
    ambient_pressure: float = 101325,
)
```

Important methods:
- `add_reactant(species)`
- `add_reactants(species_list)`
- `clear_reactants()`
- `equilibrate()`
- `print_results(n_products=10)`
- `get_mixture_ratio()`

### `Results`
Returned by `equilibrate()`. Key fields:
- `T`, `k`, `M`, `Rs`
- `c_star`, `Cf`, `v_e`, `isp`, `exp_ratio`
- `solution` (raw Cantera equilibrium solution)

## Examples

Run the full examples suite:

```bash
python examples/cea_examples.py
```

See:
- `examples/cea_examples.py`
- `examples/README.md`

## Tests

```bash
python tests/test_cea_package.py
```

## Project Layout

```text
src/pycea/
  __init__.py
  core/
    __init__.py
    pycea.py
    constants.py
examples/
  cea_examples.py
tests/
  test_cea_package.py
```

## License

MIT
