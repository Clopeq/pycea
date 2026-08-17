import pytest
from pycea import dataManager

def test_init():
    data = dataManager("./tests/materials_good.json")


def test_top_level_json_error():
    with pytest.raises(Exception):
        dataManager("./tests/materials_top_level_error.json")

def test_mid_level_json_error():
    with pytest.raises(Exception):
        dataManager("./tests/materials_mid_leve_error.json")

def test_fuel_names():
    data = dataManager("./tests/materials_good.json")
    assert data.fuel_names == ["ABS", "PLA", "PETG"]

def test_ox_names():
    data = dataManager("./tests/materials_good.json")
    assert data.ox_names == ["Nitrous Oxide", "Oxygen (gaseous)"]

def test_fuel_values():
    data = dataManager("./tests/materials_good.json")
    assert data.fuel_values == ["ABS", "PLA", "PETG"]

def test_ox_values():
    data = dataManager("./tests/materials_good.json")
    assert data.ox_values == ["N2O", "O2"]

def test_normal_val_to_name():
    data = dataManager("./tests/materials_good.json")
    assert data.val_to_name("N2O") == "Nitrous Oxide"

def test_val_to_name_incorrect_val():
    data = dataManager("./tests/materials_good.json")
    with pytest.raises(ValueError):
        data.val_to_name("Nitrous Oxide")

def test_normal_name_to_val():
    data = dataManager("./tests/materials_good.json")
    assert data.name_to_val("Nitrous Oxide") == "N2O"

def test_name_to_val_incorrect_val():
    data = dataManager("./tests/materials_good.json")
    with pytest.raises(ValueError):
        data.name_to_val("N2O")

def test_fuel_or_ox_oxidizer_value():
    data = dataManager("./tests/materials_good.json")
    assert data.fuel_or_ox("N2O") == True

def test_fuel_or_ox_oxidizer_name():
    data = dataManager("./tests/materials_good.json")
    assert data.fuel_or_ox("Nitrous Oxide") == True

def test_fuel_or_ox_fuel():
    data = dataManager("./tests/materials_good.json")
    assert data.fuel_or_ox("PETG") == False

def test_fuel_or_ox_incorrect_input():
    data = dataManager("./tests/materials_good.json")
    with pytest.raises(ValueError):
        data.fuel_or_ox(123)