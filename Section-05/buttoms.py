import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

df = pd.DataFrame({
    "first column": [1, 2, 3, 4],
    "second column": [10, 20, 30, 40]
})

st.dataframe(df)

st.download_button(
    label="Download data as CSV",
    data=df.to_csv(index=False),
    file_name="data.csv",
    mime="text/csv",
)
st.button("Click me", key="1")
st.button("Click me", key="2")

st.divider()

st.button("Click me", disabled=True, key="btn_false")
st.button("Click me", disabled=False, key="btn_true")

st.divider()
text=""
if st.button("Click me", key="btn_if"):
    text="clik button"

st.write(text)

st.divider()
if "counter" not in st.session_state:
    st.session_state.counter=0
    
if st.button("Increment"):
    st.session_state.counter +=1
if st.button("Decrement"):
    st.session_state.counter -=1

st.write("#", st.session_state.counter)

if "text" not in st.session_state:
    st.session_state.text="Hi there"

st.text_input("Enter your name", key="text")
st.write(st.session_state.text)
def change_text():
    st.session_state.text="from function and callback"

st.button("Change text", on_click=change_text)
st.write(st.session_state.text)