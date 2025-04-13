import streamlit as st
from textblob import TextBlob

st.markdown("## 🔍 Analyze Your Text’s Sentiment")
st.markdown("Enter anything — a tweet, comment, review, or thought — and get instant sentiment feedback.")

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
