import streamlit as st
from tavily import TavilyClient
import os

# Set page config
st.set_page_config(
    page_title="Code Answer Search",
    page_icon="💻",
    layout="centered"
)

def initialize_tavily_client():
    """Initialize Tavily client using Streamlit secrets"""
    try:
        tavily_api_key = st.secrets["TAVILY_API_KEY"]
        return TavilyClient(api_key=tavily_api_key)
    except KeyError:
        st.error("🔑 API key not found. Please check Streamlit Secrets.")
        return None

def search_coding_answers(tavily_client, question):
    """Search for coding answers using Tavily API"""
    if not tavily_client:
        return None
    
    search_query = (
        f"{question} site:geeksforgeeks.org OR "
        "site:stackoverflow.com OR site:w3schools.com OR "
        "site:codegrepper.com"
    )
    
    try:
        response = tavily_client.search(
            query=search_query,
            search_depth="basic",
            include_answer=True,
            include_raw_content=True,
            max_results=5
        )
        return response
    except Exception as e:
        st.error(f"🔍 Search failed: {str(e)}")
        return None

def extract_code_blocks(content):
    """Extract code blocks from raw content (simplified)"""
    if not content:
        return []
    
    # Split by common code block patterns
    code_blocks = []
    temp_block = []
    in_code = False
    
    for line in content.split("\n"):
        if "```" in line:
            if in_code and temp_block:
                code_blocks.append("\n".join(temp_block))
                temp_block = []
            in_code = not in_code
        elif in_code:
            temp_block.append(line)
    
    return code_blocks

def display_results(results):
    """Display search results in Streamlit"""
    if not results or not results.get("results"):
        st.warning("No results found. Try a different query.")
        return
    
    for result in results["results"]:
        with st.expander(f"📌 {result.get('title', 'Untitled')}"):
            st.markdown(f"🔗 **Source:** [{result['url']}]({result['url']})")
            
            # Display answer if available
            if answer := result.get("answer"):
                st.markdown("**Answer:**")
                st.write(answer)
            
            # Display code snippets
            if raw_content := result.get("raw_content"):
                code_blocks = extract_code_blocks(raw_content)
                if code_blocks:
                    st.markdown("**Code Snippets:**")
                    for code in code_blocks:
                        st.code(code, language="python")

def main():
    st.title("💻 Code Answer Search")
    st.caption("Search GeeksforGeeks, StackOverflow, and more for coding solutions!")
    
    # Initialize Tavily client
    tavily_client = initialize_tavily_client()
    
    # User input
    question = st.text_input(
        "Ask a coding question:",
        placeholder="e.g., How to reverse a string in Python?"
    )
    
    if st.button("Search", key="search_button_1") and question:
        with st.spinner("🔍 Searching for answers..."):
            results = search_coding_answers(tavily_client, question)
            display_results(results)
    elif st.button("Search", key="search_button_2") and not question:
        st.warning("Please enter a question first.")

if __name__ == "__main__":
    main()
