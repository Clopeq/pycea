import cantera as ct
import Rocketry_formulas as rf
import numpy as np
from scipy.constants import R
from importlib.metadata import version
from datetime import datetime
from dataclasses import dataclass, fields
import logging
import matplotlib.pyplot as plt
import csv

logger = logging.getLogger(__name__)

class InvalidSpeciesError(ValueError):
    """Raised when a requested species is not found in the current mechanism."""

class CEAError(Exception):
    """Raised when Cantera fails to equilibrate()"""

@dataclass
class CEAMetadata:
    software_version: str
    cantera_version: str
    date: str

@dataclass
class CEAInputs:
    fuel: str
    ox: str
    OF: list[float]
    P: list[float]
    Pa: float
    T: float
    mech_file: str

CEARESULTS_DICT_FIELDS = {"species", "species_mole"}
@dataclass
class CEAResults:
    T: np.ndarray
    cp_mass: np.ndarray
    cv_mass: np.ndarray
    cp_mole: np.ndarray
    cv_mole: np.ndarray
    k: np.ndarray
    M: np.ndarray
    Rs: np.ndarray
    species: np.ndarray
    species_mole: np.ndarray
    Isp: np.ndarray
    Isp_vac: np.ndarray
    cstar: np.ndarray
    Cf: np.ndarray
    Cf_vac: np.ndarray

class CEA:
    """ Chemical Equilibrium solver with Applications. This package uses Cantera behind the scenes"""


    def __init__(self, fuel: str, oxidizer: str, mech_file: str) -> None:
        __version__ = version("pycea")
        self._inputs = CEAInputs(
            T=300,
            Pa=101325,
            P=None,
            fuel=None,
            OF=None,
            mech_file=None,
            ox=None,
        )

        shape = (0,)
        data = {}           # initialize data with empty grid
        for f in fields(CEAResults):
            if f.name in CEARESULTS_DICT_FIELDS:
                data[f.name] = np.empty(shape, dtype=object)
            else:
                data[f.name] = np.zeros(shape, dtype=float)
        self._results = CEAResults(**data)

        self._metadata = CEAMetadata(
            cantera_version = ct.__version__,
            software_version = __version__,
            date = self._now()
        )

        self._sim = ct.Solution(mech_file)
        species = self._sim.species_names

        if fuel not in species:
            logger.warning("%r not found in species database", fuel)
            raise InvalidSpeciesError(f"{fuel!r} is not a valid species in the current mechanism")
        self._fuel = fuel

        if oxidizer not in species:
            logger.warning("%r not found in species database", oxidizer)
            raise InvalidSpeciesError(f"{oxidizer!r} is not a valid species in the current mechanism")
        self._ox = oxidizer

        self._ambient_pressure = 101325

        _field_names = {f.name for f in fields(CEAResults)}
        assert CEARESULTS_DICT_FIELDS <= _field_names, f"CEARESULTS_DICT_FIELDS has unknown fields: {CEARESULTS_DICT_FIELDS - _field_names}"

    def _equilibrate(self,
            OF: float,
            pressure: float, 
            temperature: float = 300
            ) -> CEAResults:
        """
        
        """

        #TODO: check input data
        #TODO: check cantera results for errors/exceptions
        if OF <= 0:
            logger.error("Negative Oxidizer to Fuel ratio: OF=%f", OF)
            raise ValueError(f"Oxidizer to Fuel ratio has to be greater than 0: OF={OF}")

        if pressure <= 0:
            logger.error("Negative chamber pressure: p_ch=%f", pressure)
            raise ValueError(f"Chamber pressure has to be greater than 0: p_ch={pressure}")


        F = 1/(1+OF)
        ox = OF/(1+OF)
        self._sim.Y = self._fuel+f":{F}" + ", "+self._ox+f":{ox}"
        self._sim.TP = temperature, pressure

        try:
            self._sim.equilibrate("HP", max_steps=5000, max_iter=1000)
        except ct.CanteraError as e:
            logger.error("%s._equilibrate(): equilibration failed — %s", self.__class__.__name__, e)
            raise CEAError(f"Failed to equlibrate: {e}") from e


        Rs = 1000*R/self._sim.mean_molecular_weight
        k = self._sim.cp_mass/self._sim.cv_mass
        Isp = rf.calculate_isp_ideal(k, Rs, self._sim.T, self._sim.P, self._ambient_pressure)
        Isp_vac = rf.calculate_isp_ideal(k, Rs, self._sim.T, self._sim.P, 0)
        cstar = rf.calculate_cstar_ideal(k, Rs, self._sim.T)
        Cf = rf.calculate_Cf_ideal(k, self._sim.P, self._ambient_pressure)
        Cf_vac = rf.calculate_Cf_ideal(k, self._sim.P, 0)

        results = CEAResults(
            T=self._sim.T,
            cp_mass=self._sim.cp_mass,
            cv_mass=self._sim.cv_mass,
            cp_mole=self._sim.cp_mole,
            cv_mole=self._sim.cv_mole,
            k=k,
            M=self._sim.mean_molecular_weight,
            Rs=Rs,
            species=self._sim.mass_fraction_dict(),
            species_mole=self._sim.mole_fraction_dict(),
            Isp=Isp,
            Isp_vac=Isp_vac,
            cstar=cstar,
            Cf=Cf,
            Cf_vac=Cf_vac,
        )

        return results

    def run(self,
            OF_list: list[float],
            pressure_list: list[float], 
            temperature: float = 300
        ) -> CEAResults:

        """
            Run equlibrate() for a range of OF and pressures, for single run

        """

        # Clear inputs and results data befor running
        # clear nad setup inputs log
        self._inputs.P = pressure_list
        self._inputs.OF = OF_list
        self._inputs.T = temperature
        self._inputs.Pa = self._ambient_pressure

        # Clear output logs
        shape = (len(pressure_list), len(OF_list))
        data = {}           # initialize data with empty grid
        for f in fields(CEAResults):
            if f.name in CEARESULTS_DICT_FIELDS:
                data[f.name] = np.empty(shape, dtype=object)
            else:
                data[f.name] = np.zeros(shape, dtype=float)



        for i, P in enumerate(pressure_list):
            for i2, OF in enumerate(OF_list):
                result = self._equilibrate(OF, P, temperature)
                for name in data:
                    data[name][i, i2] = getattr(result, name)

        self._results = CEAResults(**data)
        self._metadata.date = self._now()

        return self._results



    def _check_mech_file(self, mech_file: str) -> bool:
        """ Check if the provided mechanism file (.yaml) exist and if it is valid Cantera mechanism file. """
        pass

    def print_chart(self, Y: str, name: str = "output.png", output_folder: str = "./output") -> None:
        valid_names = [f.name for f in fields(CEAResults)]
        if Y not in valid_names:
            logger.warning(f"Invalid Y. Valid fields {valid_names}, got {Y!r}")
            raise ValueError(f"Y must be one of {valid_names},  got {Y!r}")

        fig, ax = plt.subplots()

        for i, P in enumerate(self._inputs.P):
            ax.plot(self._inputs.OF, getattr(self._results, Y)[i, :], label=f"P = {(P*1e-5):.1f}")

        ax.set_xlabel("O/F ratio")
        ax.set_ylabel(f"{Y}")
        ax.set_title(f"{Y} vs O/F ratio")
        ax.legend()

        fig.savefig(f"{output_folder}/{name}")
        plt.close(fig)  # release the figure from memory once saved   

    def save_csv(self, output_file: str = "./output/output.csv") -> None:
        if type(self._inputs.P) == None:
            raise RuntimeError("No results available — call run() before save_csv()")

        headers = [
            "Chamber Pressure",
            "OF",
            "Adiabatic flame temperature",
            "cp mass",
            "cv mass",
            "cp molar",
            "cv molar",
            "Isentropic exponent",
            "Molecular weight",
            "Specific gas constant",
            "Specifc impulse",
            "Vacuum specific Impulse",
            "Characteristic velocity"
            "Thrust coefficient",
            "Vacuum thrust coefficient"
        ]

        sub_headers = [
            "bar",
            "-",
            "K",
            "J/kg-K",
            "J/mol-K",
            "J/kg-K",
            "J/mol-K",
            "-",
            "g/mol",
            "J/kg-K",
            "sec",
            "sec",
            "m/s",
            "-",
            "-"
        ]

        with open(output_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows([headers, sub_headers])
            for i, P in enumerate(self._inputs.P):
                for i2, OF in enumerate(self._inputs.OF):
                    row = [self._inputs.P[i]*1e-5, self._inputs.OF[i2]]
                    field_names = [f.name for f in fields(CEAResults) if f.name not in CEARESULTS_DICT_FIELDS]
                    for name in field_names:
                        row.append(getattr(self._results, name)[i, i2])
                    writer.writerow(row)

    def save_hdf5(self):
        pass

    def save_json(self):
        pass

    def add_species(self):
        pass

    def remove_species(self):
        pass

    def modify_species(self):
        pass

    def is_valid_species(self, species: str) -> bool:
        """ Check if the provided spieces exist in the cantera database """
        pass

    def _now(self) -> str:
        return datetime.now().strftime("%H:%M, %d, %b, %Y")

    @property
    def ambient_pressure(self) -> float:
        return self._ambient_pressure

    @ambient_pressure.setter
    def ambient_pressure(self, p_ambient: float) -> float:
        if p_ambient < 0:
            logger.warning("Trying to set negative ambient pressure: ambient_pressure = %f Pa", p_ambient)
            raise ValueError(f"Ambient pressure cannot be negative: ambient_pressure = {p_ambient} Pa")
        self._ambient_pressure = p_ambient

    
    @property
    def fuel(self) -> str:
        return self._fuel

    @fuel.setter
    def fuel(self, fuel: str) -> None:
        if fuel not in self._sim.species_names:
            logger.warning(("%r not found in species database", fuel))
            raise InvalidSpeciesError(f"{fuel!r} is not a valid species in the current mechanism")
        self._fuel = fuel      

    @property
    def oxidizer(self) -> str:
        return self._ox

    @oxidizer.setter
    def oxidizer(self, oxidizer: str) -> None:
        if oxidizer not in self._sim.species_names:
            logger.warning(("%r not found in species database", oxidizer))
            raise InvalidSpeciesError(f"{oxidizer!r} is not a valid species in the current mechanism")
        self._ox = oxidizer

    @property
    def results(self) -> CEAResults:
        """ returns results """
        return self._results

    @property
    def inputs(self) -> CEAInputs:
        return self._inputs

    @property
    def metadata(self) -> CEAMetadata:
        return self._metadata