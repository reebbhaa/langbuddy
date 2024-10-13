import os
import argparse

from llama_index.core.agent import ReActAgent
# from llama_index.llms.openai_like import OpenAILike
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
from urllib.request import urlopen
# from openai import OpenAI
from bs4 import BeautifulSoup
import re 
from langchain_community.utilities import SearxSearchWrapper
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

ENDPOINT = os.environ.get("ENDPOINT", "")
default_prompt = "What is the weather like in San Francisco today?"

def url_to_filename(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    path = parsed_url.path
    filename = "past_searches/" +  netloc + path
    filename = filename.replace('/', '_')
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    if path:
        extension = path.split('.')[-1] if '.' in path else 'txt'
        filename += '.' + extension
    return filename

def remove_multiple_newlines(input_string: str) -> str:
    """Use regex to replace multiple newlines with a single newline"""
    return re.sub(r'\n+', '\n', input_string)

def get_page_content(url: str) -> str:
    """Searches the web for the search query and returns the result."""
    try:
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        soup_text = soup.get_text()
        clean_soup_text = remove_multiple_newlines(soup_text)
        return clean_soup_text
    except Exception as e:
        print(e)
        print(f"Page not loaded: {url}")
        return None

def current_date() -> str:
    """
    Get current date
    
    args:
        None
    """
    return datetime.today().strftime('%B %d, %Y')

def search_web(search_query: str) -> list[str]:
    """Searches the web for the search query and returns the result."""
    search = SearxSearchWrapper(searx_host="http://127.0.0.1:9090")
    results = search.results(search_query, num_results=5)

    urls = [result['link'] for result in results]

    soups = []
    # write page content to file
    for url in urls:
        filename = url_to_filename(url)
        with open(f"{filename}.txt", "w") as f:
            content = get_page_content(url)
            soups.append(content)
            if content is not None:
                f.write(content)  
    summaries = [summarize(soup) for soup in soups if soup is not None]
    return summaries

def summarize(text: str) -> str:
    """Summarizes the text."""
    messages = [
        ChatMessage(
            role="system", content="Please summarize the following text in 300 words or less."
        ),
        ChatMessage(role="user", content=text[:10000]),
    ]
    return llm.chat(messages)


search_web_tool = FunctionTool.from_defaults(fn=search_web)
current_date_tool = FunctionTool.from_defaults(fn=current_date)
summarize_tool = FunctionTool.from_defaults(fn=summarize)

# llm = OpenAILike(
#     api_base=os.path.join(ENDPOINT, "v1"),
#     api_key="none",
#     model="unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
# )
llm = OpenAI(model="gpt-3.5-turbo-instruct", max_tokens=1000)
agent = ReActAgent.from_tools([search_web_tool, current_date_tool, summarize_tool], llm=llm, verbose=True)

async def generate_response_with_tools(prompt, user_context, max_tokens=150):
    """Generate a response from the AI model based on the agent's personality."""
    response = agent.chat(
        messages=[ChatMessage(role="system", content=user_context),ChatMessage(role="user", content=prompt),])
    return response