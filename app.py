import streamlit as st
from tavily import TavilyClient
import os
from typing import List, Dict, Optional
import re

# Set page config
st.set_page_config(
    page_title="Enhanced Code Answer Search",
    page_icon="💻",
    layout="centered"
)

# Initialize Tavily client
def get_tavily_client() -> Optional[TavilyClient]:
    """Initialize and return Tavily client with error handling"""
    try:
        return TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
    except Exception as e:
        st.error(f"Failed to initialize search client: {str(e)}")
        return None

def search_coding_answers(question: str) -> Optional[Dict]:
    """Enhanced search for coding answers"""
    tavily_client = get_tavily_client()
    if not tavily_client:
        return None
    
    # Enhanced search query focusing on coding sites
    search_query = (
        f"{question} site:geeksforgeeks.org OR site:stackoverflow.com OR "
        "site:w3schools.com OR site:codegrepper.com OR site:realpython.com"
    )
    
    try:
        response = tavily_client.search(
            query=search_query,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            max_results=7
        )
        return response
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        return None

def extract_code_blocks(content: str) -> List[str]:
    """Improved code extraction with better pattern matching"""
    if not content:
        return []
    
    # Enhanced regex pattern for code blocks
    code_pattern = re.compile(
        r'```(?:python)?\n(.*?)```|'
        r'<code>(.*?)</code>|'
        r'(?:def|class)\s+\w+.*?:\n(?:    .*\n)+',
        re.DOTALL
    )
    
    matches = code_pattern.findall(content)
    code_blocks = []
    
    for match in matches:
        # Join all non-empty groups from the match
        block = '\n'.join([m for m in match if m.strip()])
        if block:
            # Clean up the code block
            block = re.sub(r'^\s*\n', '', block)  # Remove leading empty lines
            block = re.sub(r'\s+$', '', block)    # Remove trailing whitespace
            code_blocks.append(block)
    
    return code_blocks

def display_results(results: Dict):
    """Enhanced results display with better formatting"""
    if not results or not results.get('results'):
        st.warning("No results found. Try rephrasing your question.")
        return
    
    st.subheader("Search Results")
    
    for i, result in enumerate(results['results'], 1):
        with st.expander(f"🔍 Result {i}: {result.get('title', 'Untitled')}"):
            st.markdown(f"**Source:** [{result['url']}]({result['url']})")
            
            # Display answer if available
            if answer := result.get('answer'):
                st.markdown("**Summary:**")
                st.write(answer)
            
            # Display enhanced code snippets
            if raw_content := result.get('raw_content'):
                code_blocks = extract_code_blocks(raw_content)
                if code_blocks:
                    st.markdown("**Code Examples:**")
                    for j, code in enumerate(code_blocks, 1):
                        st.code(code, language='python')
                        st.markdown("---")

def display_example_questions():
    """Show clickable example questions"""
    st.markdown("**Try these examples:**")
    examples = [
        "How to reverse a string in Python?",
        "What's the difference between list and tuple?",
        "How to read a CSV file in Pandas?",
        "Explain Python decorators with examples",
        "How to handle exceptions in Python?"
    ]
    
    for example in examples:
        if st.button(example, key=f"example_{example}"):
            st.session_state.question = example

def main():
    st.title("💻 Enhanced Code Answer Search")
    st.markdown("Get high-quality coding answers from top programming sites!")
    
    # Initialize session state
    if 'question' not in st.session_state:
        st.session_state.question = ""
    
    # Display example questions
    display_example_questions()
    
    # User input
    question = st.text_input(
        "Or ask your own coding question:",
        value=st.session_state.question,
        placeholder="e.g., How to merge two dictionaries in Python?"
    )
    
    # Single search button with improved functionality
    if st.button("🔍 Search for Answers", type="primary"):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Searching across programming resources..."):
                results = search_coding_answers(question)
                if results:
                    display_results(results)
                else:
                    st.error("Failed to retrieve results. Please try again later.")

if __name__ == "__main__":
    main()
