from __future__ import annotations
import cantera as ct
import Rocketry_formulas as rf
import scipy.constants as const


# Phase is a wrapper for quantity
# Solution is a wrapper for Solution

class Solution:
    def __init__(self, infile="gri30.yaml", *args, **kwargs):
        self._solution = ct.Solution(infile, *args, **kwargs)
        self.__doc__ = self._solution.__doc__  # copies C-extension docstring

    def __getattr__(self, name):
        return getattr(self._solution, name)
    
    @property
    def n_species(self):
        """Number of species in the solution"""
        return self._solution.n_species
    
    def equilibrate(self, XY = "HP", *args, **kwargs):
        """Equilibrate the solution."""
        return self._solution.equilibrate(XY, *args, **kwargs)

    def solve(self, fuel: Phase, ox: Phase) -> Phase:
        fuel + ox
        self._solution.equilibrate("HP")
        #elf._solution()
        return Phase(self)
    
    def set_of_ratio(self, fuel: Phase, oxidizer: Phase, OF: float) -> None:
        fuel.mass = 1
        oxidizer.mass = OF
    
    def ct_solution(self) -> ct.Solution:
        return self._solution


class Phase(ct.Quantity):
    def __init__(self, solution: Solution, *args, **kwargs):
        self._solution = solution
        super().__init__(solution.ct_solution(), *args, **kwargs)
    
    
    def __getattr__(self, name):
        return getattr(super(), name)
    
    @property
    def k(self):
        return self.cp/self.cv
    
    @property
    def Rs(self):
        return const.R/self.mean_molecular_weight*1000
    
    @property
    def M(self):
        return self.mean_molecular_weight

    @property
    def cstar(self):
        return rf.calculate_cstar_ideal(self.k, self.Rs, self.T)
    
    @property
    def comp(self):
        return self.mass_fraction_dict()
    @comp.setter
    def comp(self, composition) -> None:
        self.Y = composition

    def __iadd__(self, other):
        if self._id != other._id:
            raise ValueError(
                'Cannot add Quantities with different phase '
                f'definitions. {self._id} != {other._id}')
        if self.constant != other.constant:
            raise ValueError(
                "Cannot add Quantities with different "
                f"constant values. {self.constant} != {other.constant}")

        m = self.mass + other.mass
        Y = (self.Y * self.mass + other.Y * other.mass)
        if self.constant == 'UV':
            U = self.int_energy + other.int_energy
            V = self.volume + other.volume
            if self.basis == 'mass':
                self._phase.UVY = U / m, V / m, Y
            else:
                n = self.moles + other.moles
                self._phase.UVY = U / n, V / n, Y
        else:  # self.constant == 'HP'
            dp_rel = 2 * abs(self.P - other.P) / (self.P + other.P)
            if dp_rel > 1.0e-7:
                raise ValueError(
                    'Cannot add Quantities at constant pressure when '
                    f'pressure is not equal ({self.P} != {other.P})')

            H = self.enthalpy + other.enthalpy
            if self.basis == 'mass':
                self._phase.HPY = H / m, None, Y
            else:
                n = self.moles + other.moles
                self._phase.HPY = H / n, None, Y

        self.state = self._phase.state
        self.mass = m
        return self

    def __add__(self, other):
        newquantity = Phase(self._solution, mass=self.mass, constant=self.constant)
        newquantity.comp = self.comp
        newquantity.TP = self.TP
        newquantity += other
        return newquantity