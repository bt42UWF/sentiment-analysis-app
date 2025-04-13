import streamlit as st
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests
# from textblob import TextBlob

# Your Bearer Token from the X API

api_key = st.secrets["api_key"]

# Function to get recent tweets using Twitter API v2
def get_tweets(query, max_results=10):
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "text"
    }
    response = requests.get(url, headers=headers, params=params)
    tweets = response.json()
    return tweets.get("data", [])

# Streamlit App UI
st.title("📡 Real-Time Tweet Sentiment Analyzer")

query = st.text_input("Enter a keyword to search tweets (e.g. Nike):", "Nike")
if st.button("Fetch Tweets"):
    tweets = get_tweets(query)
    st.write(f"Fetched {len(tweets)} tweets about '{query}'")

    for tweet in tweets:
        text = tweet["text"]
        sentiment = TextBlob(text).sentiment.polarity
        sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
        st.markdown(f"**Tweet:** {text}")
        st.markdown(f"Sentiment: `{sentiment_label}` ({sentiment})")
        st.markdown("---")



# st.markdown("## 🔍 Analyze Your Text’s Sentiment")
# st.markdown("Enter anything — a tweet, comment, review, or thought — and get instant sentiment feedback.")

# # Text input
# user_input = st.text_input("Enter your text:")

# if user_input:
#     blob = TextBlob(user_input)
#     sentiment = blob.sentiment

#     st.write("**Polarity:**", round(sentiment.polarity, 2))
#     st.write("**Subjectivity:**", round(sentiment.subjectivity, 2))

#     if sentiment.polarity > 0:
#         st.success("This text is **positive** 😊")
#     elif sentiment.polarity < 0:
#         st.error("This text is **negative** 😠")
#     else:
#         st.info("This text is **neutral** 😐")

#      wordcloud = WordCloud(width=800, height=400).generate(user_input)
#         st.markdown("### 🧠 Word Cloud")
#         fig, ax = plt.subplots()
#         ax.imshow(wordcloud, interpolation='bilinear')
#         ax.axis("off")
#         st.pyplot(fig)
