import json
import urllib.parse
import urllib.request
import re
from typing import List, Dict, Any, Optional, Tuple

def get_domain_name(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or "web"
    except Exception:
        return "web"

def search_duckduckgo(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    """
    Queries DuckDuckGo Instant Answer API for web knowledge.
    Returns structured results: [{'title': ..., 'url': ..., 'snippet': ..., 'source_name': ...}]
    """
    results = []
    try:
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "CampusMindAI/1.0 (Educational Assistant)"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            
            # 1. Main abstract
            abstract_text = data.get("AbstractText")
            abstract_url = data.get("AbstractURL")
            heading = data.get("Heading") or query.title()
            
            if abstract_text and abstract_url:
                results.append({
                    "title": heading,
                    "url": abstract_url,
                    "snippet": abstract_text[:280] + ("..." if len(abstract_text) > 280 else ""),
                    "source_name": get_domain_name(abstract_url)
                })
                
            # 2. Related topics
            for topic in data.get("RelatedTopics", []):
                if len(results) >= max_results:
                    break
                if isinstance(topic, dict) and "FirstURL" in topic and "Text" in topic:
                    t_url = topic["FirstURL"]
                    t_text = topic["Text"]
                    t_title = t_text.split(" - ")[0] if " - " in t_text else t_text[:60]
                    results.append({
                        "title": t_title,
                        "url": t_url,
                        "snippet": t_text[:240] + ("..." if len(t_text) > 240 else ""),
                        "source_name": get_domain_name(t_url)
                    })
    except Exception as e:
        print(f"DuckDuckGo search error for '{query}': {e}")
        
    return results

def search_wikipedia_educational(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Queries Wikipedia API for academic and scientific concepts.
    """
    results = []
    try:
        import wikipedia
        search_terms = wikipedia.search(query, results=max_results)
        for term in search_terms:
            if len(results) >= max_results:
                break
            try:
                page_summary = wikipedia.summary(term, sentences=2, auto_suggest=False)
                clean_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(term.replace(' ', '_'))}"
                results.append({
                    "title": f"{term} - Wikipedia",
                    "url": clean_url,
                    "snippet": page_summary[:280] + ("..." if len(page_summary) > 280 else ""),
                    "source_name": "en.wikipedia.org"
                })
            except Exception:
                continue
    except Exception as e:
        print(f"Wikipedia search error for '{query}': {e}")
        
    return results

def perform_educational_web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Combines educational knowledge sources (Wikipedia & DuckDuckGo API)
    without scraping Google HTML pages.
    """
    combined = []
    seen_urls = set()
    
    # Clean query for search
    cleaned_query = re.sub(r'^(what is|explain|define|tell me about|how does|what are)\s+', '', query.strip(), flags=re.IGNORECASE)
    cleaned_query = re.sub(r'\s+in (hinglish|simple terms|detail|hindi)$', '', cleaned_query, flags=re.IGNORECASE).strip()
    if not cleaned_query:
        cleaned_query = query
        
    # 1. Wikipedia academic query
    wiki_results = search_wikipedia_educational(cleaned_query, max_results=2)
    for r in wiki_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            combined.append(r)
            
    # 2. DuckDuckGo knowledge query
    ddg_results = search_duckduckgo(cleaned_query, max_results=3)
    for r in ddg_results:
        if r["url"] not in seen_urls and len(combined) < max_results:
            seen_urls.add(r["url"])
            combined.append(r)
            
    return combined

def extract_gemini_grounding(candidate_obj) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Extracts web search queries and citation chunks from Gemini's grounding_metadata.
    """
    queries = []
    sources = []
    seen_urls = set()
    
    if not candidate_obj:
        return queries, sources
        
    grounding_meta = getattr(candidate_obj, "grounding_metadata", None)
    if not grounding_meta and isinstance(candidate_obj, dict):
        grounding_meta = candidate_obj.get("grounding_metadata")
        
    if not grounding_meta:
        return queries, sources
        
    # Extract search queries
    raw_queries = getattr(grounding_meta, "web_search_queries", None)
    if not raw_queries and isinstance(grounding_meta, dict):
        raw_queries = grounding_meta.get("web_search_queries", [])
    if raw_queries:
        queries = list(raw_queries)
        
    # Extract grounding chunks (sources)
    chunks = getattr(grounding_meta, "grounding_chunks", None)
    if not chunks and isinstance(grounding_meta, dict):
        chunks = grounding_meta.get("grounding_chunks", [])
        
    if chunks:
        for chunk in chunks:
            web = getattr(chunk, "web", None)
            if not web and isinstance(chunk, dict):
                web = chunk.get("web")
            if web:
                uri = getattr(web, "uri", None) or (web.get("uri") if isinstance(web, dict) else None)
                title = getattr(web, "title", None) or (web.get("title") if isinstance(web, dict) else None)
                if uri and uri not in seen_urls:
                    seen_urls.add(uri)
                    sources.append({
                        "title": title or get_domain_name(uri),
                        "url": uri,
                        "source_name": get_domain_name(uri),
                        "snippet": "Verified educational source grounding via Google Search."
                    })
                    
    return queries, sources
