import streamlit as st

def custom_card(title, content, footer, color):
    card_style = f"""    
        <style>
        body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #f0f2f5;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
        }}

        .card {{
        background-color: {color};
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        overflow: hidden; /* Ensures child elements respect the border-radius */
        width: 350px;
        transition: box-shadow 0.3s ease-in-out;
        }}

        .card:hover {{
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }}

        .card-header {{
        padding: 20px;
        background-color: #f7f7f7;
        border-bottom: 1px solid #e0e0e0;
        }}

        .card-header h2 {{
        margin: 0;
        font-size: 1.5em;
        color: #333;
        }}

        .card-body {{
        padding: 20px;
        color: #555;
        line-height: 1.6;
        }}

        .card-footer {{
        padding: 20px;
        background-color: #f7f7f7;
        border-top: 1px solid #e0e0e0;
        text-align: right;
        }}

        .card-footer button {{
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1em;
        transition: background-color 0.2s ease;
        }}

        .card-footer button:hover {{
        background-color: #0056b3;
        }}
    </style>

    """
    st.markdown(card_style, unsafe_allow_html=True)
    card_html = f"""
        <div class="card">
        <div class="card-header">
        <h2>{title}</h2>
        </div>
        <div class="card-body">
        <p>{content}</p>
        </div>
        <div class="card-footer">
        {footer}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)