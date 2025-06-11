import streamlit as st
st.set_page_config(layout="wide", page_title="Home", page_icon="🐍")




st.title("Hello from streamlit")

st.header("hellos I'm a header")
st.subheader("I'm a subheader")
st.markdown("I'm a markdown")
st.write("I'm a write")
st.caption("I'm a caption")
name= "miguel"
st.text(f"I'm a text {name}")
st.text("I'm a text: " + name)
st.button("Click me")

name = st.text_input("Enter your name")

st.text("Your name is: " + name)

st.slider("Select a number", 0, 100, 50)

st.color_picker("Pick a color")

st.date_input("Pick a date")

st.time_input("Pick a time")

st.checkbox("I'm a checkbox")

st.radio("Pick an option", ["Option 1", "Option 2", "Option 3"])


st.latex(r'''
    a + ar + a r^2 + a r^3 + \cdots + a r^{n-1} =
    \sum_{k=0}^{n-1} ar^k =
    a \left(\frac{1-r^{n}}{1-r}\right)
''')
st.latex(r'''
    \frac{n!}{k!(n-k)!} = \binom{n}{k}
''')
st.latex(r''' matrix = \begin{pmatrix} a & b \\ c & d \end{pmatrix} ''')
st.latex(r''' CH_4 +2H_2O -> H_2 + 2OH_2 ''')


json={
    "name": "miguel",
    "age": 25,
    "city": "bogota"}
st.json(json)

code ='''
fuction hello() {
    print("Hello from streamlit")
}
'''

st.code(code, language="python")

st.metric ("Temperature", "70 °F", "1.2 °F")
st.metric (label="Dola", value="1500 $", delta="-34%")