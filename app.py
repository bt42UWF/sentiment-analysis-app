import streamlit as st
from textblob import TextBlob

st.title("Sentiment Analyzer")
st.write("Enter a sentence or paragraph to analyze its sentiment.")

# Text input
user_input = st.text_input("Enter your text:")

if user_input:
    blob = TextBlob(user_input)
    sentiment = blob.sentiment

    st.write("**Polarity:**", round(sentiment.polarity, 2))
    st.write("**Subjectivity:**", round(sentiment.subjectivity, 2))

    if sentiment.polarity > 0:
        st.success("This text is **positive** 😊")
    elif sentiment.polarity < 0:
        st.error("This text is **negative** 😠")
    else:
        st.info("This text is **neutral** 😐")
