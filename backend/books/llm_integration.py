import requests
import json
import os
from django.conf import settings

llm_cache = {}

def call_llm(prompt, system_prompt=None, use_cache=True):
    cache_key = hash(prompt)
    
    if use_cache and cache_key in llm_cache:
        return llm_cache[cache_key]
    
    if system_prompt is None:
        system_prompt = "You are a helpful assistant that answers questions based on the provided context. Always cite your sources when possible."
    
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
            if use_cache:
                llm_cache[cache_key] = result
            return result
        else:
            return f"Error: Unable to get response from LLM. Status: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to LLM. Make sure LM Studio is running on port 1234."
    except Exception as e:
        return f"Error: {str(e)}"

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
    prompt = f"""Analyze the sentiment of the following text. Return only one word: Positive, Negative, or Neutral:

Text: {text[:1000]}

Sentiment:"""
    return call_llm(prompt).strip()

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
