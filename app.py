import streamlit as st
from openai import OpenAI
import pandas as pd

# Streamlit sidebar: OpenAI API Key Input
st.sidebar.title("OpenAI API Key")

if "api_key" not in st.session_state:
    st.session_state.api_key = None

if st.session_state.api_key:
    st.sidebar.success("API Key Loaded!")
    # Add a way to view the first few characters of the API key
    masked_key = st.session_state.api_key[:5] + "*" * (len(st.session_state.api_key) - 5)
    st.sidebar.text(f"Current key: {masked_key}")
    if st.sidebar.button("Logout"):
        st.session_state.api_key = None
        st.rerun()
else:
    api_key_input = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
    if api_key_input:
        # Trim any whitespace from the input
        api_key_input = api_key_input.strip()
        st.session_state.api_key = api_key_input
        st.sidebar.success("API Key Saved for this session!")
        st.rerun()

if not st.session_state.api_key:
    st.warning("Please enter your OpenAI API Key in the sidebar to continue.")
    st.stop()

# Initialize OpenAI client
try:
    client = OpenAI(api_key=st.session_state.api_key)
    # Test the API key with a simple request
    client.models.list()
    st.sidebar.success("API Key is valid!")
except Exception as e:
    st.sidebar.error(f"Error with API Key: {str(e)}")
    st.stop()

# Sidebar: Input Options
st.sidebar.header("Article Parameters")
input_method = st.sidebar.radio("Select Input Method", ["Manual Input", "CSV Upload"])
article_length = st.sidebar.slider("Select Article Length (words)", 500, 2000, step=500)
tone = st.sidebar.selectbox("Select Tone", ["Formal", "Friendly", "Technical", "Conversational"])

# Main Window: Keyword Input Section
st.title("article content gen")

if input_method == "Manual Input":
    keywords = st.text_area("Enter Keywords (comma-separated)", placeholder="e.g., marketing, SEO, AI content")
    keywords_list = [kw.strip() for kw in keywords.split(",") if kw]
else:
    uploaded_file = st.file_uploader("Upload CSV with Keyword Groups", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of Uploaded Keywords:", df.head())
        keywords_list = df.iloc[:, 0].tolist()  # Assume keywords are in the first column

# Generate Article Outline
if st.button("Generate Outline"):
    if keywords_list:
        prompt = f"Generate an outline for a blog post using the following keywords: {', '.join(keywords_list)}."
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates SEO blog outlines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            outline = response.choices[0].message.content.strip()
            st.subheader("Generated Outline:")
            st.text_area("Outline", outline, height=200)
            st.session_state.outline = outline  # Store outline in session state
        except Exception as e:
            st.error(f"Error generating outline: {e}")
    else:
        st.warning("Please enter or upload keywords first.")

# Generate Full Article
if st.button("Generate Full Article"):
    outline = st.session_state.get("outline")
    if outline:
        prompt = f"Write a {article_length}-word article based on the following outline: {outline}. Use a {tone} tone."
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates full articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            article = response.choices[0].message.content.strip()
            st.subheader("Generated Article:")
            st.text_area("Article", article, height=400)
            st.session_state.article = article  # Store article in session state
        except Exception as e:
            st.error(f"Error generating article: {e}")
    else:
        st.warning("Please generate an outline first.")

# Export Article as Markdown
if st.button("Export to Markdown"):
    article = st.session_state.get("article")
    if article:
        markdown_content = f"# Generated Article\n\n{article}"
        st.download_button(
            label="Download Markdown",
            data=markdown_content,
            file_name="article.md",
            mime="text/markdown"
        )
    else:
        st.warning("Please generate an article first.")
