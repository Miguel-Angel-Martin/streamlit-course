import streamlit as st
import google.generativeai as genai

genai.configure(api_key= st.secrets["gemini"]["API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# def generate_response(prompt):
#     try:
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         return f"Error con la respuesta: {e}"

def generate_response(message):
    try:
        messages = "\n".join([f"{msg['role']} : {msg['content']}" for msg in message])
        response = model.generate_content(messages)
        return response.text
    except Exception as e:
        return f"Error con la respuesta: {e}"
    
def generate_name(prompt):
    try:
        response = model.generate_content(f"Genera un nombre en base a este texto: {prompt} no superior a 50 caracteres")
        return response.text
    except Exception as e:
        return f"Error con la respuesta: {e}"