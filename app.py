import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import nltk
import random
from textblob import TextBlob
from faker import Faker
import tweepy
import json  # Import the json library

nltk.download('punkt')

# Initialize Faker for generating realistic dummy text (you might not need this anymore)
fake = Faker()

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Twitter Sentiment Dashboard", layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">', unsafe_allow_html=True)

# -------------------- LOGIN PAGE --------------------
def login():
    st.markdown(
        """
        <style>
        .login-title {
            text-align: center;
        }
        .login-icon {
            text-align: center;
            font-size: 4em; /* Adjust size as needed */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<h2 class="login-title">Login to Sentiment Dashboard</h2>', unsafe_allow_html=True)
    st.markdown('<div class="login-icon"><i class="bi bi-person-circle"></i></div>', unsafe_allow_html=True)
    col_user_left, col_user_mid, col_user_right = st.columns([2, 1, 2])
    with col_user_mid:
        username = st.text_input("Username", key="username_input", label_visibility="visible")

    col_pass_left, col_pass_mid, col_pass_right = st.columns([2, 1, 2])
    with col_pass_mid:
        password = st.text_input("Password", type="password", key="password_input", label_visibility="visible")

    col_button_left, col_button_mid, col_button_right = st.columns([4, 1, 4])
    with col_button_mid:
        login_button = st.button("Login", key="login_button", use_container_width=True)

    return username, password, login_button

# -------------------- SENTIMENT ANALYSIS FUNCTION --------------------
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    else:
        return "Neutral", polarity

# -------------------- LOAD AND PREPROCESS DATA FUNCTION --------------------
@st.cache_data(show_spinner=True)
def load_and_preprocess_data(file_path, keyword="Nike"):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                tweet = json.loads(line)
                data.append(tweet)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

    df = pd.DataFrame(data)

    # Filter for tweets containing the keyword
    nike_df = df[df['full_text'].str.contains(keyword, case=False, na=False)].copy()

    if nike_df.empty:
        return pd.DataFrame()  # Return an empty DataFrame if no Nike tweets found

    # Select relevant columns and rename them
    nike_df = nike_df[['created_at', 'full_text', 'user', 'retweet_count', 'favorite_count']].copy()
    nike_df.rename(columns={'full_text': 'text', 'retweet_count': 'retweets', 'favorite_count': 'likes'}, inplace=True)

    # Add a 'date' column
    nike_df.loc[:, 'date'] = pd.to_datetime(nike_df['created_at']).dt.date

    # Perform sentiment analysis
    sentiment_results = nike_df['text'].apply(analyze_sentiment)
    nike_df[['sentiment', 'polarity']] = pd.DataFrame(sentiment_results.tolist(), index=nike_df.index)

    return nike_df

# -------------------- MAIN APP FUNCTION --------------------
def main_app():
    # -------------------- HEADER --------------------
    st.markdown("""
        <style>
         .big-font {
             font-size:30px !important;
             font-weight: bold;
         }
         .subheader-font{
             font-size: 20px;
             font-weight: bold;
             margin-bottom: 10px;
         }
         .logout-container {
             position: absolute;
             top: 10px;
             right: 10px;
             z-index: 1000;
         }
         .logout-button {
             background-color: transparent;
             border: none;
             cursor: pointer;
             padding: 5px;
             font-size: 20px;
         }
         </style>
    """, unsafe_allow_html=True)

    username = st.session_state.get("username", "User")

    logout_html = f"""
         <div style="position: absolute; top: 10px; right: 10px; z-index: 1000;">
             <button id="logout-trigger" style="background-color: transparent; border: none; cursor: pointer; padding: 5px;">
                 <i class="bi bi-person-circle"></i> {username}
             </button>
         </div>
     """

    st.markdown(logout_html, unsafe_allow_html=True)

    if st.session_state.get('logout'):
        st.session_state["logged_in"] = False
        st.session_state.pop("username", None)
        st.session_state.pop("logout", None)
        st.rerun()

    st.markdown(f'<div class="big-font"><i class="bi bi-graph-up-arrow"></i> Twitter Sentiment Dashboard</div>', unsafe_allow_html=True)

    # -------------------- USER INPUT --------------------
    keyword = "Nike"  # Focusing on Nike
    st.markdown(f'<i class="bi bi-twitter"></i> Analyzing tweets about {keyword}', unsafe_allow_html=True)

    # --- Load and preprocess the real data ---
    file_path = "/Users/belannatorres/Downloads/nikelululemonadidas_tweets.jsonl"  # Replace with the actual path
    df = load_and_preprocess_data(file_path, keyword)

    if df.empty:
        st.warning(f"No tweets found containing '{keyword}' in the provided dataset.")
    else:
        # -------------------- FILTERS AT THE TOP --------------------
        st.subheader("Filter Data")
        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            sentiment_filter = st.multiselect("Filter by Sentiment:",
                                                options=df["sentiment"].unique(),
                                                default=df["sentiment"].unique())

        with filter_col2:
            min_date = df["date"].min()
            max_date = df["date"].max()
            date_range = st.date_input("Filter by Date:",
                                       min_value=min_date,
                                       max_value=max_date,
                                       value=(min_date, max_date))

        # Apply Filters
        filtered_df = df[df["sentiment"].isin(sentiment_filter)]
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[(filtered_df["date"] >= start_date) & (filtered_df["date"] <= end_date)]

        # Metrics based on filtered data
        total_comments = len(filtered_df)
        positive = filtered_df[filtered_df["sentiment"] == "Positive"].shape[0]
        negative = filtered_df[filtered_df["sentiment"] == "Negative"].shape[0]
        neutral = filtered_df[filtered_df["sentiment"] == "Neutral"].shape[0]
        overall_sentiment = "Positive" if positive > negative else "Negative" if negative > positive else "Neutral"

        total_likes = filtered_df["likes"].sum()
        total_retweets = filtered_df["retweets"].sum()

        # -------------------- METRIC BAR --------------------
        col1, col2, col3 = st.columns(3)
        col1.metric("🗨️ Comments", total_comments)
        col2.metric("👍 Likes", total_likes)
        col3.metric("🔁 Retweets", total_retweets)

        # -------------------- SENTIMENT PIE & HALF-DONUT --------------------
        col1_charts, col2_charts = st.columns(2)

        with col1_charts:
            st.markdown(f'<div class="subheader-font"><i class="bi bi-emoji-smile"></i><i class="bi bi-emoji-neutral"></i><i class="bi bi-emoji-frown"></i> Overall Sentiment Level</div>', unsafe_allow_html=True)
            half_donut_data = filtered_df[filtered_df["sentiment"].isin(["Positive", "Negative"])]
            if not half_donut_data.empty:
                half_donut_data = half_donut_data["sentiment"].value_counts().reset_index()
                half_donut_data.columns = ["Sentiment", "Count"]
                half_donut_data["Percentage"] = half_donut_data["Count"] / half_donut_data["Count"].sum()

                half_donut_fig = px.pie(half_donut_data, names="Sentiment", values="Count", hole=0.6,
                                         color="Sentiment",
                                         color_discrete_map={"Positive": "#4CAF50", "Negative": "#F44336"})
                half_donut_fig.update_traces(
                    sort=False,
                    marker=dict(line=dict(width=2, color="white")),
                    textinfo="percent+label",
                    insidetextfont=dict(color="white")
                )
                half_donut_fig.update_layout(showlegend=False,
                                             margin=dict(l=0, r=0, t=30, b=0))

                # Add annotations for percentages
                total = half_donut_data["Count"].sum()
                positive_percent = half_donut_data[half_donut_data["Sentiment"] == "Positive"]["Count"].values[0] / total * 100 if "Positive" in half_donut_data["Sentiment"].values else 0
                negative_percent = half_donut_data[half_donut_data["Sentiment"] == "Negative"]["Count"].values[0] / total * 100 if "Negative" in half_donut_data["Sentiment"].values else 0

                half_donut_fig.add_annotation(
                    text=f"Positive: {positive_percent:.1f}%<br>Negative: {negative_percent:.1f}%",
                    x=0.5, y=0.5,
                    font=dict(size=14),
                    showarrow=False
                )
                st.plotly_chart(half_donut_fig, use_container_width=True)
            else:
                st.warning("No positive or negative tweets to display the overall sentiment level.")

        with col2_charts:
            st.markdown(f'<div class="subheader-font"><i class="bi bi-pie-chart"></i> Sentiment Distribution</div>', unsafe_allow_html=True)
            pie_data = filtered_df["sentiment"].value_counts().reset_index()
            pie_data.columns = ["Sentiment", "Count"]

            pie_fig = px.pie(pie_data, names="Sentiment", values="Count", hole=0.4,
                             color="Sentiment",
                             color_discrete_map={"Positive": "#4CAF50", "Neutral": "#FFC107", "Negative": "#F44336"})
            st.plotly_chart(pie_fig, use_container_width=True)

        # -------------------- SENTIMENT OVER TIME WITH POLARITY --------------------
        st.markdown(f'<div class="subheader-font"><i class="bi bi-clock-history"></i> Sentiment Over Time (with Average Polarity)</div>', unsafe_allow_html=True)
        timeline = filtered_df.groupby("date").agg(
            Count=('sentiment', 'size'),
            Avg_Polarity=('polarity', 'mean')
        ).reset_index()

        bar_fig = px.bar(timeline, x="date", y="Count",
                         color=timeline['Avg_Polarity'],
                         color_continuous_scale=['red', 'yellow', 'green'],
                         title="Sentiment Over Time",
                         labels={"Count": "Number of Tweets", "date": "Date", "color": "Avg. Polarity"})
        st.plotly_chart(bar_fig, use_container_width=True)

        # -------------------- DOWNLOAD DATA BUTTON --------------------
        st.markdown(f'<div class="subheader-font"><i class="bi bi-download"></i> Download Data</div>', unsafe_allow_html=True)
        csv = filtered_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name='filtered_nike_tweet_sentiment_data.csv',
            mime='text/csv',
        )

        # -------------------- DATA TABLE --------------------
        with st.expander("View Raw Tweet Data"):
            st.dataframe(filtered_df[["text", "likes", "retweets", "sentiment", "polarity", ]])

# -------------------- AUTHENTICATION AND SESSION STATE MANAGEMENT --------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    username, password, login_button = login()
    if login_button:
        # Use st.secrets to get the username and password
        correct_username = st.secrets.get("app_username")
        correct_password = st.secrets.get("app_password")

        if username == correct_username and password == correct_password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.rerun()  # Force a rerun to hide the login form
        else:
            st.error("Incorrect username or password")
else:
    main_app()
