import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from collections import Counter
from preprocess import preprocess

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat (.txt)", type=["txt"])

def count_links(messages):
    return sum(len(re.findall(r'https?://\S+|www\.\S+', msg)) for msg in messages)

def is_emoji(char):
    return char >= '\U0001F600' and char <= '\U0001FAFF'

if uploaded_file:
    data = uploaded_file.read().decode("utf-8")
    df = preprocess(data)

    user_list = sorted(df['user'].unique().tolist())
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # ─── TOP STATS ─────────────────────────────
    st.title("Top Statistics")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Messages", df.shape[0])
    col2.metric("Words", df['message'].str.split().apply(len).sum())
    col3.metric("Links", count_links(df['message']))
    col4.metric("Active Days", df['date'].dt.date.nunique())

    # ─── MONTHLY TIMELINE ─────────────────────
    st.title("Monthly Timeline")
    st.title("Monthly Timeline")

timeline = (
    df
    .assign(year=df['date'].dt.year, month=df['date'].dt.month)
    .groupby(['year', 'month'])
    .agg(message=('message', 'count'))
    .reset_index()
)

timeline['time'] = timeline['month'].astype(str) + "-" + timeline['year'].astype(str)

st.line_chart(timeline.set_index('time')['message'])

    st.line_chart(timeline.set_index('time')['message'])

    # ─── DAILY TIMELINE ───────────────────────
    st.title("Daily Timeline")
    daily = df.groupby(df['date'].dt.date).count()['message']
    st.line_chart(daily)

    # ─── ACTIVITY MAP ─────────────────────────
    st.title("Activity Map")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Busy Days")
        st.bar_chart(df['date'].dt.day_name().value_counts())

    with col2:
        st.subheader("Busy Months")
        st.bar_chart(df['date'].dt.month_name().value_counts())

    # ─── HEATMAP ──────────────────────────────
    st.title("Weekly Activity Heatmap")
    heatmap = df.pivot_table(
        index=df['date'].dt.day_name(),
        columns=df['date'].dt.hour,
        values='message',
        aggfunc='count'
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(12,5))
    sns.heatmap(heatmap, ax=ax)
    st.pyplot(fig)

    # ─── WORDCLOUD ────────────────────────────
    st.title("WordCloud")
    wc = WordCloud(width=600, height=400, background_color='white')
    text = df['message'].str.cat(sep=" ")
    wc.generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)

    # ─── EMOJI ANALYSIS ───────────────────────
    st.title("Emoji Analysis")
    emojis = []
    for msg in df['message']:
        emojis.extend([c for c in msg if is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(), columns=['Emoji', 'Count'])
    if not emoji_df.empty:
        col1, col2 = st.columns(2)
        col1.dataframe(emoji_df)
        fig, ax = plt.subplots()
        ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(), autopct="%0.2f")
        col2.pyplot(fig)

    # Most Active Users
    st.subheader("👥 Most Active Users")
    user_counts = df['user'].value_counts()
    st.bar_chart(user_counts)
