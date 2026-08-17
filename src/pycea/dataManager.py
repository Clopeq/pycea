import json


class dataManager:
    def __init__(self, database: str):
        self._load_json(database)

    def _load_json(self, filepath: str) -> bool:
        try:
            with open(filepath, "r") as f:
                dict = json.load(f)
                check = [i for i in dict]

                #check top level json items
                if check != ["Oxidizers", "Fuels"]:
                    raise Exception(f"dataManager._load_json(): loaded JSON has no valid \"[\"Oxidizers\", \"Fuels\"]\" items: {filepath}")

                self._oxidizer_list = dict["Oxidizers"]
                self._check_material(self._oxidizer_list)
                self._fuel_list = dict["Fuels"]
                self._check_material(self._fuel_list)
                
                self._name_value_pairs = []
                for ox in self._oxidizer_list:
                    self._name_value_pairs.append((ox["name"], ox["value"]))
                for f in self._fuel_list:
                    self._name_value_pairs.append((f["name"], f["value"]))

                return True
        except FileNotFoundError:
            raise ValueError(f"dataManager._load_json(): File not found: {filepath}")
        except json.JSONDecodeError as e:
            raise ValueError(f"dataManager._load_json(): Invalid JSON in {filepath}: {e}")
        return None

    def _check_material(self, materials: list) -> bool:
        for mat in materials:
            if type(mat) != dict:
                raise Exception(f"dataManager._check_material(): materials should be a list of dictionaries not {type(mat)}")
            
            check = [i for i in mat]
            if check != ["name", "value"]:
                raise Exception(f"dataManager._check_material(): materials should be a list of {{\"name\", \"value\"}}, not {check}")
        return True

    def val_to_name(self, value: str) -> str | bool:
        for i in self._name_value_pairs:
            if value in i[1]:
                return i[0]
        raise ValueError(f"dataManager.val_to_name(): \"{value}\" has no valid name assigned to it")

    def name_to_val(self, name: str) -> str | bool:
        for i in self._name_value_pairs:
            if name in i[0]:
                return i[1]
        raise ValueError(f"dataManager.name_to_val(): \"{name}\" has no valid value assigned to it")

    def fuel_or_ox(self, name_or_val: str) -> bool:
        # return True if it is an Oxidizer
        # return False if it is a Fuel

        if not self.is_valid(name_or_val):
            raise ValueError(f"dataManager.fuel_or_ox(): \"{name_or_val}\" is not a valid name or value")

        for ox in self._oxidizer_list:
            if ox["name"] == name_or_val or ox["value"] == name_or_val:
                return True
            
        for f in self._fuel_list:
            if f["name"] == name_or_val or f["value"] == name_or_val:
                return False

        # This basically should never happen after self.is_valid() check at the beggining
        raise ValueError(f"dataManager.fuel_or_ox(): could not find \"{name_or_val}\" in database")

    def is_valid(self, name_or_val: str) -> bool:
        # check the databese if material of given name or value exist
        # useful for checking user input
        for i in self._name_value_pairs:
            if name_or_val in i:
                return True
        return False

    @property
    def ox_names(self) -> list:
        return [i["name"] for i in self._oxidizer_list]

    @property
    def fuel_names(self) -> list:
        return[i["name"] for i in self._fuel_list]

    @property
    def ox_values(self) -> list:
        return [i["value"] for i in self._oxidizer_list]
    
    @property
    def fuel_values(self) -> list:
        return[i["value"] for i in self._fuel_list]

