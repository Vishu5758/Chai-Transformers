import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import load_articles, get_article_content, paginate_articles

# --- Page configuration ---
st.set_page_config(
    page_title="InsightAI | Advanced LLM Blog",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for enhanced visual design ---
st.markdown("""
<style>
    /* Main content area styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    
    /* Typography styling */
    h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        color: #1E3A8A !important;
        font-family: 'Helvetica Neue', sans-serif !important;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #1E3A8A !important;
        margin-top: 1rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #2563EB !important;
    }
    
    /* Card styling for articles */
    .article-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .article-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: none;
        transition: background-color 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    
    /* Tag styling */
    .tag {
        background-color: #EFF6FF;
        color: #2563EB;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Search input styling */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #E5E7EB;
        padding: 0.75rem 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F8FAFC;
    }
    
    /* Article reading view */
    .article-content {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 2rem;
        margin-top: 1rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Featured article badge */
    .featured-badge {
        background-color: #FBBF24;
        color: #92400E;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    /* Read time badge */
    .read-time {
        color: #6B7280;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Article thumbnail */
    .article-thumbnail {
        width: 100%;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
    
    /* Header/hero section */
    .hero-section {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .hero-title {
        color: white !important;
        margin-bottom: 1rem !important;
    }
    
    .hero-subtitle {
        font-size: 1.2rem !important;
        opacity: 0.9;
        margin-bottom: 1.5rem;
    }
    
    /* Pagination styling */
    .pagination {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
    }
    
    .pagination-button {
        margin: 0 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Functions to enhance UI/UX ---
def create_tag_html(tags):
    """Generate HTML for article tags"""
    tags_html = ""
    for tag in tags:
        tags_html += f'<span class="tag">{tag}</span>'
    return tags_html

def estimate_read_time(content):
    """Estimate reading time based on article content"""
    words = len(content.split())
    minutes = max(1, round(words / 200))  # Average reading speed
    return f"{minutes} min read"

def render_article_card(article, is_featured=False):
    """Generate a visually appealing article card"""
    # Generate thumbnail based on article slug (in real app, you'd store this in article metadata)
    thumbnail_id = hash(article['slug']) % 10 + 1  # Use hash of slug to pick a consistent thumbnail
    
    # In a real application, you would have actual thumbnails for each article
    thumbnail_url = f"https://picsum.photos/seed/{thumbnail_id}/600/300"
    
    # Mock tags (in a real app, these would come from article metadata)
    tags = []
    if "transformer" in article['title'].lower() or "transformer" in article['slug'].lower():
        tags.append("Transformers")
    if "llm" in article['title'].lower() or "llm" in article['slug'].lower():
        tags.append("LLMs")
    if "gpt" in article['title'].lower() or "gpt" in article['slug'].lower():
        tags.append("GPT")
    if "ai" in article['title'].lower() or "ai" in article['slug'].lower():
        tags.append("AI")
    if len(tags) == 0:
        tags.append("Machine Learning")
        
    # Add generic ML tags to ensure we have some diversity
    if len(tags) < 3:
        if "AI Ethics" not in tags:
            tags.append("AI Ethics")
        if "NLP" not in tags and len(tags) < 3:
            tags.append("NLP")
            
    # Get content for read time estimation
    content = get_article_content(article['path'])
    read_time = estimate_read_time(content)
    
    # Create a summary (first 150 characters of content without the title)
    content_without_title = content.split('\n', 2)[-1] if len(content.split('\n')) > 1 else content
    summary = content_without_title[:150] + "..." if len(content_without_title) > 150 else content_without_title
    
    # Render the card HTML
    st.markdown(f"""
    <div class="article-card">
        <img src="{thumbnail_url}" class="article-thumbnail" alt="Article thumbnail">
        <h3>{article['title']} {' <span class="featured-badge">Featured</span>' if is_featured else ''}</h3>
        <p><em>{article['date']}</em> · <span class="read-time">{read_time}</span></p>
        <div>{create_tag_html(tags)}</div>
        <p>{summary}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add a read more button
    if st.button(f"📖 Read Full Article", key=f"read_{article['slug']}"):
        st.session_state["current_article"] = article

def display_article(article):
    """Display a full article with enhanced styling"""
    # Get the full content
    content = get_article_content(article['path'])
    read_time = estimate_read_time(content)
    
    # Display article header
    st.markdown(f"""
    <h2>{article['title']}</h2>
    <p><em>{article['date']}</em> · <span class="read-time">{read_time}</span></p>
    """, unsafe_allow_html=True)
    
    # Add a back button
    if st.button("← Back to Articles"):
        st.session_state.pop("current_article", None)
        st.experimental_rerun()
    
    # Display the article content
    st.markdown(f"""
    <div class="article-content">
        {content}
    </div>
    """, unsafe_allow_html=True)

# --- Initialize session state for navigation ---
if "current_article" not in st.session_state:
    st.session_state["current_article"] = None

# --- Sidebar with advanced filtering ---
with st.sidebar:
    st.markdown("""
    <h2 style="margin-top: 0;">InsightAI</h2>
    <p>Cutting-edge insights on LLMs, AI trends, and machine learning breakthroughs.</p>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Search & Filter")
    
    # Advanced search
    search_query = st.text_input("Search articles...", placeholder="Enter keywords...")
    
    # Category filter (mock categories, would be derived from article metadata)
    categories = ["All Categories", "Large Language Models", "AI Ethics", "Transformers", 
                  "Computer Vision", "Reinforcement Learning", "NLP", "Industry Applications"]
    selected_category = st.selectbox("Category", categories)
    
    # Date filter
    st.markdown("### 📅 Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", datetime(2023, 1, 1))
    with col2:
        end_date = st.date_input("To", datetime.now())
    
    # Sort options
    sort_options = ["Newest First", "Oldest First", "Most Popular", "Most Relevant"]
    sort_by = st.selectbox("Sort By", sort_options)
    
    # Newsletter signup (mock)
    st.markdown("---")
    st.markdown("### 📫 Newsletter")
    st.markdown("Get the latest AI insights delivered to your inbox")
    email = st.text_input("Email address", placeholder="your@email.com")
    if st.button("Subscribe"):
        st.success("Thank you for subscribing!")
        time.sleep(1)
    
    # About section
    st.markdown("---")
    st.markdown("### About InsightAI")
    st.markdown("""
    InsightAI is your go-to resource for cutting-edge insights on artificial intelligence, 
    large language models, and the future of machine learning technology.
    """)
    
    # Social links (mock)
    st.markdown("### Connect")
    cols = st.columns(4)
    with cols[0]:
        st.markdown("[![Twitter](https://img.icons8.com/ios-filled/25/1DA1F2/twitter.png)](https://twitter.com)")
    with cols[1]:
        st.markdown("[![LinkedIn](https://img.icons8.com/ios-filled/25/0077B5/linkedin.png)](https://linkedin.com)")
    with cols[2]:
        st.markdown("[![GitHub](https://img.icons8.com/ios-filled/25/000000/github.png)](https://github.com)")
    with cols[3]:
        st.markdown("[![YouTube](https://img.icons8.com/ios-filled/25/FF0000/youtube-play.png)](https://youtube.com)")

# --- Main content area ---
if st.session_state["current_article"]:
    # Display single article view
    display_article(st.session_state["current_article"])
else:
    # Display blog listing view
    
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">InsightAI Journal</h1>
        <p class="hero-subtitle">Exploring the frontiers of artificial intelligence and large language models</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load articles
    articles = load_articles("articles")
    
    # Apply filters
    if search_query:
        articles = [a for a in articles if search_query.lower() in a['title'].lower()]
    
    # Apply category filter (mock implementation)
    if selected_category != "All Categories":
        # This is a mock filter since we don't have real categories
        # In a real app, you'd filter based on article metadata
        category_keywords = {
            "Large Language Models": ["llm", "language model", "gpt"],
            "AI Ethics": ["ethics", "bias", "fairness"],
            "Transformers": ["transformer", "attention", "bert"],
            "Computer Vision": ["vision", "image", "recognition"],
            "Reinforcement Learning": ["reinforcement", "rl", "reward"],
            "NLP": ["nlp", "language", "text"],
            "Industry Applications": ["industry", "business", "application"]
        }
        
        if selected_category in category_keywords:
            keywords = category_keywords[selected_category]
            filtered_articles = []
            for article in articles:
                if any(kw in article['title'].lower() for kw in keywords):
                    filtered_articles.append(article)
            articles = filtered_articles
    
    # Apply date filter
    articles = [a for a in articles if start_date <= datetime.strptime(a['date'], "%Y-%m-%d").date() <= end_date]
    
    # Apply sorting
    if sort_by == "Oldest First":
        articles.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
    elif sort_by == "Newest First":
        articles.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"), reverse=True)
    # Note: Most Popular and Most Relevant would need real metrics, this is a mock implementation
    
    # Display message if no articles found
    if not articles:
        st.warning("No articles match your search criteria. Try adjusting your filters.")
    else:
        # Featured articles section (first 2 articles)
        if len(articles) > 0:
            st.markdown("## 🌟 Featured Articles")
            featured_cols = st.columns(min(2, len(articles)))
            for i in range(min(2, len(articles))):
                with featured_cols[i]:
                    render_article_card(articles[i], is_featured=True)
        
        # Regular articles
        st.markdown("## 📚 Latest Insights")
        
        # Calculate pagination
        per_page = 6
        total_pages = max(1, len(articles[2:]) // per_page + (1 if len(articles[2:]) % per_page > 0 else 0))
        
        # Get page number from query params or session state
        if "page" not in st.session_state:
            st.session_state.page = 1
            
        # Display paginated articles
        start_idx = 2  # Start after featured articles
        start_idx += (st.session_state.page - 1) * per_page
        end_idx = min(start_idx + per_page, len(articles))
        
        # Use columns for a grid layout
        for i in range(start_idx, end_idx, 2):
            cols = st.columns(2)
            with cols[0]:
                if i < len(articles):
                    render_article_card(articles[i])
            with cols[1]:
                if i + 1 < len(articles):
                    render_article_card(articles[i + 1])
        
        # Pagination controls
        if total_pages > 1:
            st.markdown('<div class="pagination">', unsafe_allow_html=True)
            cols = st.columns([1, 3, 1])
            with cols[1]:
                pagination_cols = st.columns(min(7, total_pages + 2))
                
                # Previous button
                with pagination_cols[0]:
                    if st.button("◀", disabled=st.session_state.page <= 1):
                        st.session_state.page -= 1
                        st.experimental_rerun()
                
                # Page buttons
                display_pages = min(5, total_pages)
                start_page = max(1, min(st.session_state.page - display_pages // 2, total_pages - display_pages + 1))
                end_page = min(start_page + display_pages - 1, total_pages)
                
                for i, col in enumerate(pagination_cols[1:-1], start=1):
                    if i <= end_page - start_page + 1:
                        page_num = start_page + i - 1
                        with col:
                            button_type = "primary" if page_num == st.session_state.page else "secondary"
                            if st.button(f"{page_num}", key=f"page_{page_num}"):
                                st.session_state.page = page_num
                                st.experimental_rerun()
                
                # Next button
                with pagination_cols[-1]:
                    if st.button("▶", disabled=st.session_state.page >= total_pages):
                        st.session_state.page += 1
                        st.experimental_rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; padding: 1rem 0;">
        <p>© 2025 InsightAI Journal. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)
