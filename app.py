import streamlit as st

st.title("Sentiment Analyzer")
st.write("This is a simple Streamlit app for sentiment analysis!")

user_input = st.text_input("Enter your text:")
if user_input:
    # Placeholder for actual sentiment analysis
    st.write("You entered:", user_input)
    st.write("Sentiment: Neutral (mock result)")
