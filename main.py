from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
import io
import PyPDF2

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

app = FastAPI()

class SearchResult(BaseModel):
    title: str
    description: str
    url: str
    summary: str

def scrape_webpage(url):
    try:
        if url.lower().endswith('.pdf'):
            # Download and extract text from PDF
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with io.BytesIO(response.content) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() or ''
            return text.strip() if text else f"Error scraping {url}: PDF contains no extractable text"
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

def summarize_text(text, sentences_count=3):
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, sentences_count)
        return ' '.join([str(sentence) for sentence in summary])
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

@app.get("/search", response_model=List[SearchResult])
def search(query: str = Query(..., description="Search query")):
    results = DDGS().text(query, max_results=5)
    output = []
    for result in results:
        title = result.get('title', '')
        url = result.get('href', '')
        description = result.get('body', '')
        scraped_text = scrape_webpage(url)
        if scraped_text.startswith("Error"):
            summary = scraped_text
        else:
            if len(scraped_text) > 8000:
                scraped_text = scraped_text[:8000] + "..."
            summary = summarize_text(scraped_text, sentences_count=3)
        output.append(SearchResult(title=title, description=description, url=url, summary=summary))
    return output
