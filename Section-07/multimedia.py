import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time




st.set_page_config(layout="wide")
st.divider()
st.title("Multimedia Section with cache")
@st.cache_resource
def get_video_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

video_add= "https://videos.pexels.com/video-files/33185813/14142695_2560_1440_60fps.mp4"

video_data = get_video_url(video_add)
st.video(video_data, format="video/mp4", start_time=0, loop=True)

st.divider()

st.subheader("Multimedia Section")
st.write("This section demonstrates how to display multimedia content in Streamlit.")
st.divider()
st.write("### Displaying Images")
image = st.image("./assets/image.jpg", caption="Sample Image", use_container_width=True, clamp=True,
                output_format="JPEG", width=300)

st.write("### Displaying Audio")
audio_file = "./assets/audio.mp3"
if st.button("Play Audio", key="play_audio"):
    st.audio(audio_file, format="audio/mp3", start_time=0)
    
st.write("### Displaying Video")
video_file = "https://videos.pexels.com/video-files/27604137/12183363_1440_2560_24fps.mp4"
if st.button("Play Video", key="play_video"):
    st.markdown(f"""
    <video width="640" height="360" controls autoplay muted>
        <source src="{video_file}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    """, unsafe_allow_html=True)

st.divider()
st.write("### Displaying HTML Content")
html_content = """
<div style="text-align: center;">
    <h2>Welcome to the Multimedia Section</h2>
    <p>This section showcases how to embed multimedia content in your Streamlit app.</p>
</div>
"""
st.markdown(html_content, unsafe_allow_html=True)
st.divider()
st.write("### Displaying Markdown Content")
markdown_content = """
# Markdown Content
This is an example of how to display **bold text**, *italic text*, and [links](https://www.example.com) in Streamlit.
You can also include lists:
- Item 1
- Item 2
```python
def hello_world():
    print("Hello, World!")
```
"""
st.markdown(markdown_content, unsafe_allow_html=True)
st.divider()
st.write("### Displaying DataFrames")
df = pd.DataFrame({
    "Column 1": [1, 2, 3],
    "Column 2": ["A", "B", "C"],
    "Column 3": [4.5, 5.6, 6.7]
})
st.dataframe(df, use_container_width=True, key="dataframe_display")
st.write("### Displaying Code Snippets")
code_snippet = """```python
def example_function():     
    print("This is an example function.")
```"""
st.code(code_snippet, language="python")
st.divider()
st.write("### Displaying JSON Data")
json_data = {
    "name": "Streamlit",
    "version": "1.0",
    "features": ["Interactive", "Easy to use", "Fast"]
}
st.json(json_data, expanded=True)
st.divider()
st.write("### Displaying Progress Bars")        
progress_bar = st.progress(0)                    
for i in range(100):    
    progress_bar.progress(i + 1)    
    time.sleep(0.05)  # Simulate some processing time
st.write("Progress bar completed!")
st.divider()
st.write("### Displaying Spinner")
with st.spinner("Loading..."):
    time.sleep(2)  # Simulate some loading time
st.write("Spinner completed!")
st.divider()
st.write("### Displaying Notifications")
st.success("This is a success message!", icon="✅")
st.error("This is an error message!", icon="❌")
st.warning("This is a warning message!", icon="⚠️")
st.info("This is an info message!", icon="ℹ️")
st.divider()
st.write("### Displaying Markdown with Custom CSS")
custom_css = """
<style>
    .custom-markdown {
        color: blue;
        font-size: 20px;
        font-weight: bold;
    }
</style>
<div class="custom-markdown">
    This is a custom styled markdown content.
</div>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.write("### Displaying Custom HTML")
custom_html = """
<div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px;">
    <h3>Custom HTML Content</h3>
    <p>This is an example of how to display custom HTML content in Streamlit.</p>
</div>
"""
st.markdown(custom_html, unsafe_allow_html=True)
st.divider()
st.write("### Displaying Custom Widgets")
if st.button("Click Me", key="custom_button"):
    st.write("Button clicked!")
st.checkbox("Check Me", key="custom_checkbox")
if st.radio("Choose an option", ["Option 1", "Option 2"], key="custom_radio") == "Option 1":
    st.write("You selected Option 1")
st.selectbox("Select an option", ["Option A", "Option B"], key="custom_selectbox")
st.multiselect("Select multiple options", ["Choice 1", "Choice 2", "Choice 3"], key="custom_multiselect")
st.slider("Select a value", min_value=0, max_value=100, value=50, key="custom_slider")
st.number_input("Enter a number", min_value=0, max_value=100, value=10, key="custom_number_input")
st.text_input("Enter some text", key="custom_text_input", placeholder="Type here...")
st.text_area("Enter a longer text", key="custom_text_area", placeholder="Type here...", height=100)
st.date_input("Select a date", value=datetime.now(), key="custom_date_input")
st.time_input("Select a time", value=datetime.now().time(), key="custom_time_input")
st.file_uploader("Upload a file", type=["csv", "txt", "jpg", "png"], key="custom_file_uploader")
if st.button("Submit", key="custom_submit_button"):
    st.write("Custom widgets submitted!")
st.divider()
st.write("### Displaying Custom Components")            
st.write("Custom components are not yet supported in Streamlit.")           
