import streamlit as st
from openai import OpenAI
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Streamlit sidebar: OpenAI API Key Input
st.sidebar.title("OpenAI API Key")
if api_key:
    st.sidebar.success("API Key Loaded!")
else:
    api_key_input = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
    if api_key_input:
        # Save API key to .env file for future use
        with open(".env", "w") as f:
            f.write(f"OPENAI_API_KEY={api_key_input}")
        st.sidebar.success("API Key Saved! Please refresh the page.")
        st.stop()  # Stop execution to reload with the new key

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Sidebar: Input Options
st.sidebar.header("Article Parameters")
input_method = st.sidebar.radio("Select Input Method", ["Manual Input", "CSV Upload"])
article_length = st.sidebar.slider("Select Article Length (words)", 500, 2000, step=500)
tone = st.sidebar.selectbox("Select Tone", ["Formal", "Friendly", "Technical", "Conversational"])

# Main Window: Keyword Input Section
st.title("article/seo content generator")

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
