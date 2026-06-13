# app.py

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==========================
# CONFIGURATION
# ==========================
API_KEY = "YOUR_NEWSAPI_KEY"
BASE_URL = "https://newsapi.org/v2/top-headlines"

st.set_page_config(
    page_title="Advanced News Dashboard",
    page_icon="📰",
    layout="wide"
)

# ==========================
# FUNCTIONS
# ==========================

@st.cache_data(ttl=300)
def fetch_news(country, category, page_size, keyword):
    params = {
        "apiKey": API_KEY,
        "pageSize": page_size
    }

    if country:
        params["country"] = country

    if category != "All":
        params["category"] = category.lower()

    if keyword:
        params["q"] = keyword

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()
    return None


def process_articles(data):
    if not data or "articles" not in data:
        return []

    articles = []

    for article in data["articles"]:
        articles.append({
            "Title": article.get("title"),
            "Source": article.get("source", {}).get("name"),
            "Published": article.get("publishedAt"),
            "Description": article.get("description"),
            "URL": article.get("url"),
            "Image": article.get("urlToImage")
        })

    return articles


# ==========================
# HEADER
# ==========================

st.title("📰 AI News Dashboard")
st.markdown("Search and filter news from around the world")

# ==========================
# SIDEBAR FILTERS
# ==========================

st.sidebar.header("Filters")

countries = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "Germany": "de",
    "France": "fr",
    "Japan": "jp",
    "China": "cn"
}

country_name = st.sidebar.selectbox(
    "Select Country",
    list(countries.keys())
)

country_code = countries[country_name]

category = st.sidebar.selectbox(
    "Select Category",
    [
        "All",
        "Business",
        "Entertainment",
        "General",
        "Health",
        "Science",
        "Sports",
        "Technology"
    ]
)

page_size = st.sidebar.slider(
    "Number of Articles",
    5,
    50,
    20
)

keyword = st.sidebar.text_input(
    "Search Keywords",
    placeholder="AI, Tesla, Cricket..."
)

search_btn = st.sidebar.button("🔍 Fetch News")

# ==========================
# NEWS FETCHING
# ==========================

if search_btn:

    with st.spinner("Fetching latest news..."):

        news_data = fetch_news(
            country_code,
            category,
            page_size,
            keyword
        )

        if news_data and news_data.get("status") == "ok":

            articles = process_articles(news_data)

            st.success(f"Found {len(articles)} articles")

            # Metrics
            col1, col2, col3 = st.columns(3)

            col1.metric("Articles", len(articles))
            col2.metric("Country", country_name)
            col3.metric("Category", category)

            st.divider()

            # News Cards
            for article in articles:

                with st.container():

                    col1, col2 = st.columns([1, 3])

                    with col1:
                        if article["Image"]:
                            st.image(
                                article["Image"],
                                use_container_width=True
                            )

                    with col2:
                        st.subheader(article["Title"])

                        st.caption(
                            f"Source: {article['Source']}"
                        )

                        if article["Published"]:
                            try:
                                dt = datetime.strptime(
                                    article["Published"],
                                    "%Y-%m-%dT%H:%M:%SZ"
                                )
                                st.caption(
                                    f"Published: {dt.strftime('%d %b %Y %H:%M')}"
                                )
                            except:
                                pass

                        st.write(article["Description"])

                        st.link_button(
                            "Read Full Article",
                            article["URL"]
                        )

                    st.divider()

            # Download Section
            st.subheader("Download Articles")

            df = pd.DataFrame(articles)

            csv = df.to_csv(index=False)

            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="news_articles.csv",
                mime="text/csv"
            )

        else:
            st.error("Unable to fetch news. Check API key.")

# ==========================
# DEFAULT SCREEN
# ==========================

else:
    st.info("Use filters in the sidebar and click 'Fetch News'.")