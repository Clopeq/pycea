import pycea.cea as pycea
import cliscreen as cli
import numpy as np
import matplotlib.pyplot as plt
import time


ISP = 0
msg_box = cli.MenuItem(label=f"Isp: {ISP}")

def main():
    fuel_options = ["ABS", "PLA", "PETG", "Sorbitol"]
    oxidizer_options = ["N2O", "O2"]
    chart_options = ["Isp", "cstar", "Cf", "k", "M", "T"]
    fuel = cli.InlineSelectBox(label="Fuel", options=fuel_options)
    ox = cli.InlineSelectBox(label="Oxidizer", options=oxidizer_options)
    var_to_print = cli.InlineSelectBox(label="Print", options=chart_options)
    #pressure = cli.InlineNumberInput(label="Pressure [bar]", value=30, allow_negative=False)
    pressure = np.linspace(5e5, 300e5, 5)
    OF_list = np.linspace(1, 15, 100)

    menu = cli.Menu(
        title="Test menu",
        widgets= [
            fuel,
            ox,
            #pressure,
            var_to_print,
            cli.MenuItem(label="Run", action=lambda: run(fuel.value, ox.value, pressure, OF_list, var_to_print.value)),
            cli.MenuItem(label="Quit", action=lambda: "EXIT"),
            msg_box
        ],
    )
    menu.run()

def run(fuel: str, oxidizer: str, pressure_list: float, OF_list: float, var_to_print: str = "Isp"):
    cea = pycea.CEA(fuel, oxidizer, "./src/pycea/data/filaments.yaml")

    start = time.perf_counter()
    results = cea.run(OF_list, pressure_list)
    end = time.perf_counter()

    ISP = results.Isp.max()
    msg_box.label = f"calculated in: {end - start:.4f} sec"

    cea.print_chart(var_to_print)  
    cea.save_csv()              



if __name__ == "__main__":
    main()