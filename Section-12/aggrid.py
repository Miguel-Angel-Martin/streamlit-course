from st_aggrid import AgGrid
import pandas as pd
import streamlit as st

df = pd.DataFrame({"Nombre": ["Ana", "Luis", "Carlos"], "Edad": [28, 34, 45]})
AgGrid(df, paginationAutoPageSize=True)
