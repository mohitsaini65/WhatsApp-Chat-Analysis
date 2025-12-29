import streamlit as st
import pandas as pd
from preprocess import preprocess
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

st.set_page_config(page_title="WhatsApp Chat Analysis", layout="wide")

st.title("📊 WhatsApp Chat Analysis")

uploaded_file = st.file_uploader("Upload WhatsApp Chat (.txt)", type=["txt"])

def count_links(messages):
    links = []
    for msg in messages:
        links.extend(re.findall(r'https?://\S+|www\.\S+', msg))
    return len(links)

if uploaded_file:
    data = uploaded_file.read().decode("utf-8")
    df = preprocess(data)

    users = ['Overall'] + sorted(df['user'].unique().tolist())
    selected_user = st.selectbox("Select User", users)

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Messages", df.shape[0])
    with col2:
        st.metric("Words", sum(df['message'].str.split().apply(len)))
    with col3:
        st.metric("Links", count_links(df['message']))
    with col4:
        st.metric("Active Days", df['day_name'].nunique())

    # WordCloud
    st.subheader("☁ Word Cloud")
    wc = WordCloud(width=600, height=400, background_color='white')
    text = df['message'].str.cat(sep=" ")
    wc.generate(text)

    fig, ax = plt.subplots()
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)

    # Most Active Users
    st.subheader("👥 Most Active Users")
    user_counts = df['user'].value_counts()
    st.bar_chart(user_counts)
