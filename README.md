# pycea 🚀

**A Python-native, Cantera-powered chemical equilibrium solver for rocket propulsion — built for 3D-printed hybrid rocket fuels.**

`pycea` is a lightweight alternative to NASA's CEA (Chemical Equilibrium with Applications), aimed squarely at the hybrid rocket / amateur & university rocketry crowd. Instead of wrestling with CEA's Fortran-era interface, you get a scriptable Python API on top of [Cantera](https://cantera.org/), pre-loaded with a custom thermodynamic mechanism for common 3D-printing thermoplastics (ABS, PLA, PETG, Sorbitol) burning against N₂O or gaseous O₂.

Sweep O/F ratio and chamber pressure, get Isp, c*, Cf, flame temperature, and gas properties back as clean NumPy arrays — ready to plot, export, or feed into a larger sizing tool.

> **Status:** early / actively developed. Core equilibrium solver and CSV export work today; a few convenience methods (HDF5/JSON export, species editing) are stubbed out. See [Roadmap](#roadmap).

---

## Why

Hybrid rocket motors using 3D-printed fuel grains (ABS, PLA, PETG) have become popular in student and amateur rocketry, but NASA CEA's built-in thermo database doesn't know about these materials out of the box. `pycea` ships a Cantera mechanism file with these fuels defined by their elemental composition and heat of formation, so you can run real equilibrium chemistry against them directly — no manual propellant-card hacking required.

## Features

- 🔥 **Chemical equilibrium via Cantera** — constant-pressure (`HP`) equilibration at your chamber conditions, not curve-fit approximations
- 🧪 **Custom mechanism for print fuels** — ABS, ABS(wet), PLA, PETG, and Sorbitol defined on top of a trimmed GRI-Mech 3.0 species set
- 📊 **Full performance sweep** — vectorized over O/F ratio *and* chamber pressure in one `run()` call
- 📈 **Derived rocket performance** — Isp (sea-level & vacuum), characteristic velocity (c*), thrust coefficient (Cf, vacuum Cf), isentropic exponent, mean molecular weight, specific gas constant — via [`Rocketry_formulas`](https://github.com/Clopeq/Rocketry_formulas)
- 🗂️ **CSV export** of the full result grid, and quick matplotlib charts of any output variable vs O/F ratio
- 💻 **Interactive terminal UI** for quick fuel/oxidizer/plot selection via [`cliscreen`](https://github.com/Clopeq/cliscreen)
- ✅ **Validated propellant data** — `dataManager` checks your fuel/oxidizer JSON database on load so bad entries fail fast

## Requirements

- Python **3.14+**
- [Cantera](https://cantera.org/) 3.2+ (the physics engine underneath)
- [uv](https://docs.astral.sh/uv/) (recommended — this project is built and locked with it)

## Installation

```bash
git clone https://github.com/Clopeq/pycea.git
cd pycea
uv sync
```

This pulls in `cantera`, `numpy`, `scipy`, `matplotlib`, `plotly`, `pyqtgraph`, `pyside6`, plus two first-party companion packages fetched directly from GitHub:

- [`Rocketry_formulas`](https://github.com/Clopeq/Rocketry_formulas) — Isp / c* / Cf formulas
- [`cliscreen`](https://github.com/Clopeq/cliscreen) — terminal menu widgets

No PyPI install yet — clone and run with `uv` for now.

## Quick start

Run the interactive CLI (installed as a script entry point):

```bash
uv run pycea
```

This opens a terminal menu to pick a fuel (ABS / PLA / PETG / Sorbitol), an oxidizer (N₂O / O₂), and a variable to plot — then sweeps O/F from 1 to 15 across five chamber pressures (5–300 bar), saves a chart to `output/`, and dumps the full grid to `output/output.csv`.

### Using it as a library

```python
import numpy as np
from pycea.cea import CEA

# fuel, oxidizer, and the Cantera mechanism file with your propellant thermo data
sim = CEA(fuel="PLA", oxidizer="N2O", mech_file="./data/filaments.yaml")

OF_list = np.linspace(1, 15, 100)      # O/F ratio sweep
P_list  = np.linspace(5e5, 30e5, 5)    # chamber pressure sweep [Pa]

results = sim.run(OF_list, P_list)

print("Best Isp:", results.Isp.max(), "s")

sim.print_chart("Isp")   # -> output/output.png
sim.save_csv()           # -> output/output.csv
```

`results` is a `CEAResults` dataclass holding 2D NumPy arrays shaped `(len(P_list), len(OF_list))` for every output — flame temperature, `cp`/`cv` (mass & molar), isentropic exponent `k`, molecular weight, specific gas constant, species mole/mass fractions, Isp, vacuum Isp, c*, Cf, and vacuum Cf.

## Defining your own propellants

Propellants live in a Cantera YAML mechanism (see `data/filaments.yaml`). Each custom species needs at minimum its elemental `composition` and standard enthalpy of formation `h0`:

```yaml
- name: PLA
  composition: {C: 4.5500, H: 5.2827, N: 0.0462, O: 2.0902}
  thermo:
    model: constant-cp
    h0: -801.104 kJ/mol      # heat of formation (or derived from HHV)
```

Add `cp0` if the species' actual temperature deviates significantly from 298.15 K on the reactant side. See the comments at the top of `data/filaments.yaml` for the full rules.

The human-readable name ↔ Cantera species symbol mapping (e.g. "Nitrous Oxide" ↔ `N2O`) used by the CLI lives in `data/materials.json`, validated at load time by `dataManager`.

## Project layout

```
pycea/
├── data/
│   ├── filaments.yaml      # Cantera mechanism: GRI-Mech 3.0 subset + custom fuel species
│   └── materials.json      # display name <-> species symbol lookup for fuels/oxidizers
├── src/pycea/
│   ├── cea.py               # CEA class: equilibrium solver, sweeps, charts, CSV export
│   ├── dataManager.py       # loads & validates the fuel/oxidizer JSON database
│   └── app.py                # interactive CLI entry point (`pycea` command)
├── tests/                    # pytest suite for dataManager
└── output/                   # generated charts & CSVs land here
```

## Running tests

```bash
uv run pytest
```

## Roadmap

- [ ] Finish `save_hdf5()` / `save_json()` export methods
- [ ] `add_species()` / `remove_species()` / `modify_species()` for editing the mechanism at runtime
- [ ] `is_valid_species()` and `_check_mech_file()` input validation
- [ ] Wire up the `cliscreen` menu for chamber pressure entry (currently hardcoded)
- [ ] Interactive plotly/pyqtgraph views alongside static matplotlib charts

## Acknowledgments

Built on [Cantera](https://cantera.org/), an open-source suite for chemical kinetics, thermodynamics, and transport. Base gas-phase chemistry from **GRI-Mech 3.0**.

## License

No license file yet — all rights reserved by default until one is added. Open an issue if you'd like to use this and need clarity on terms.
