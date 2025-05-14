import streamlit as st
from utils import load_articles, get_article_content, paginate_articles

# --- Page config ---
st.set_page_config(page_title="📚 My Streamlit Blog", layout="wide")

# --- Load articles ---
articles = load_articles("articles")

# --- Sidebar search ---
st.sidebar.title("🔍 Search")
search_query = st.sidebar.text_input("Search articles...")

# --- Filter articles ---
if search_query:
    articles = [a for a in articles if search_query.lower() in a['title'].lower()]

# --- Pagination ---
page = st.sidebar.number_input("Page", min_value=1, max_value=max(1, len(articles)//5 + 1), step=1)
paginated = paginate_articles(articles, page=page, per_page=5)

# --- Display articles ---
st.title("📝 Streamlit Blog")
if not paginated:
    st.warning("No articles found.")
else:
    for article in paginated:
        st.subheader(article['title'])
        st.write(f"*{article['date']}*")
        if st.button(f"📖 Read More - {article['slug']}", key=article['slug']):
            content = get_article_content(article['path'])
            st.markdown(content, unsafe_allow_html=True)
        st.markdown("---")
