import requests
import json
import os
import re
import hashlib
from django.conf import settings
from django.core.cache import cache as django_cache

def call_llm(prompt, system_prompt=None, use_cache=True):
    cache_key = 'llm_' + hashlib.md5(prompt.encode()).hexdigest()
    
    if use_cache:
        cached = django_cache.get(cache_key)
        if cached:
            return cached
    
    if system_prompt is None:
        system_prompt = "You are a helpful book assistant. Always cite sources."
    
    provider = getattr(settings, 'LLM_PROVIDER', 'lmstudio')
    
    if provider == 'claude':
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            message = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            result = message.content[0].text
        except Exception as e:
            result = f"Claude API error: {str(e)}"
    else:
        try:
            response = requests.post(
                f"{settings.LLM_BASE_URL}/chat/completions",
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
            else:
                result = f"Error: Unable to get response from LLM. Status: {response.status_code}"
        except requests.exceptions.ConnectionError:
            result = "Error: Cannot connect to LLM. Make sure LM Studio is running on port 1234."
        except Exception as e:
            result = f"Error: {str(e)}"
    
    if use_cache and result and not result.startswith('Error'):
        django_cache.set(cache_key, result, timeout=86400)
    return result

def generate_summary(text):
    prompt = f"""Based on the following book content, generate a concise summary (2-3 paragraphs):

{text[:3000]}

Summary:"""
    return call_llm(prompt)

def classify_genre(description):
    prompt = f"""Based on the following book description, predict the genre. Return only the genre name (e.g., Fiction, Non-Fiction, Mystery, Science Fiction, Romance, etc.):

Description: {description[:1000]}

Genre:"""
    return call_llm(prompt).strip()

def analyze_sentiment(text):
    prompt = """Analyze the sentiment of this book description.
Return ONLY valid JSON: {"label": "Positive|Neutral|Negative", "score": 0.0-1.0, "reasoning": "one sentence"}

Text: """ + text[:1000]
    result = call_llm(prompt)
    try:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return {"label": data.get("label", "Neutral"), "score": float(data.get("score", 0.5))}
    except:
        pass
    return {"label": "Neutral", "score": 0.5}

def get_recommendations(book_title, book_genre, all_books):
    other_books = [b for b in all_books if b.get('title') != book_title][:10]
    if not other_books:
        return []
    
    books_list = "\n".join([f"- {b.get('title', 'Unknown')} by {b.get('author', 'Unknown')}" for b in other_books])
    
    prompt = f"""Based on the book "{book_title}" (Genre: {book_genre}), recommend 3 books from the following list that a reader would enjoy:

{books_list}

Recommendations (just list the book titles):"""
    
    result = call_llm(prompt)
    recommendations = [line.strip().lstrip('- ') for line in result.split('\n') if line.strip()]
    return recommendations[:3]

def rag_answer(question, context_chunks, book_title):
    context = "\n\n".join([f"[Source {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)])
    
    prompt = f"""Based on the following context from the book "{book_title}", answer the question. Always cite your sources using the format [Source X].

Context:
{context}

Question: {question}

Answer:"""
    
    return call_llm(prompt)