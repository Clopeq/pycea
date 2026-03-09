import streamlit as st
from widgets.input_boxes import *
import pycea as pc

if "species" not in st.session_state: # A container keeping all of the species selectboxes
    st.session_state["species"] = [[None, None]]

st.title("Equilibruim solver")

st.header("Propellant composition")



# fuels = ["ABS", "PARAFIN", "PLA", "PETG", "EPOXY", "SORBITOL", "SUCROSE", "DEXTROSE"]
# oxidizers = ["NITROUS OXIDE", "HYDROGEN PEROXIDE", "OXYGEN"]

fuels = []
oxidizers = []

cea = pc.CEA()

for sp in cea.species_all:
    fuels.append(sp)

pressure_units = ["bar", "Pa", "psi", "MPa"]
pressure_units_dict = {"bar":1e5, "Pa":1, "psi":6895, "MPa":10e5}


species = []

c = st.container()

col1, col2 = st.columns(2)

# Add species button declaration and behaviour
if col1.button("Add ingredient", "BUTTON_ADD_SPECIES", "Add a fuel or oxidizer to the mixture", use_container_width=True):
    st.session_state["species"].append([None,None])

# Remove button declaration and behaviour
if col2.button("Remove ingredient", key="BUTTON_REMOVE_SPECIES", use_container_width=True):
    st.session_state["species"].pop()


# Handling of the dynamically generated list of species
for i in range(len(st.session_state["species"])):
    col1, col2 = c.columns([2,1], vertical_alignment="bottom")
    
    st.session_state["species"][i][0] = col1.selectbox(
        f"Ingredient #{i+1}",
        fuels+oxidizers,
        key=f"SPECIES_{i}"
    )
    st.session_state["species"][i][1] = col2.number_input("weight", key=f"NUMBER_INPUT_SPECIES_{i}", step=1.0, format="%.2f")


st.divider()
st.header("Conditions")

pressure_input(st, "CHAMBER_PRESSURE", "Chamber pressure")
pressure_input(st, "AMBIENT_PRESSURE", "Ambient pressure")

if st.button("SUBMIT", key="BUTTON_SUBMIT", use_container_width=True):
    pass

st.space("xxlarge")
st.divider()
with st.expander("DEBUG INFO"):

    "current session state:"
    st.session_state

