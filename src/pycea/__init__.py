import cantera as ct
import Rocketry_formulas as rf
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import R
import plotly.graph_objects as go
import cliscreen as cli

from .dataManager import dataManager

def main() -> None:
    data = dataManager("./src/pycea/matasderials.json")


    # fuel_options = ["ABS", "PLA", "PETG"]
    # oxidizer_options = ["N2O", "O2"]
    # fuel = cli.InlineSelectBox(label="Fuel", options=fuel_options)
    # ox = cli.InlineSelectBox(label="Oxidizer", options=oxidizer_options)
    # pressure = cli.InlineNumberInput(label="Pressure [bar]", value=30, allow_negative=False)

    # menu = cli.Menu(
    #     title="Test menu",
    #     widgets= [
    #         fuel,
    #         ox,
    #         pressure,
    #         cli.MenuItem(label="Run", action=lambda: OFSweep(fuel.value, ox.value, pressure.value * 10**5)),
    #         cli.MenuItem(label="Quit", action=lambda: "EXIT"),
    #     ],
    # )
    # menu.run()





    

'''
    tales fuel and oxidizer as a string
    takes OF range
    takes number of points
    takes initial pressure and teperature
    outputs a 

'''