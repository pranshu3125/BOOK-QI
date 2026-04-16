const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface Book {
  id: number;
  title: string;
  author: string;
  description: string;
  rating: number | null;
  review_count: number;
  genre: string;
  cover_url: string;
  book_url: string;
  price: string;
  created_at: string;
}

export interface AIInsights {
  id: number;
  summary: string;
  genre_prediction: string;
  sentiment: string;
  sentiment_score: number;
  recommendations: string[];
  created_at: string;
}

export interface QAHistory {
  id: number;
  book: number;
  book_title: string;
  question: string;
  answer: string;
  sources: Source[];
  created_at: string;
}

export interface Source {
  index: number;
  book_id?: number;
  book_title?: string;
  chunk_index?: number;
  source?: string;
  text: string;
}

export async function fetchBooks(search = '', genre = ''): Promise<Book[]> {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (genre) params.append('genre', genre);
  
  const response = await fetch(`${API_BASE_URL}/?${params.toString()}`);
  if (!response.ok) throw new Error('Failed to fetch books');
  return response.json();
}

export async function fetchBookDetail(id: number): Promise<Book> {
  const response = await fetch(`${API_BASE_URL}/books/${id}/`);
  if (!response.ok) throw new Error('Failed to fetch book details');
  return response.json();
}

export async function fetchBookInsights(id: number): Promise<AIInsights> {
  const response = await fetch(`${API_BASE_URL}/books/${id}/insights/`);
  if (!response.ok) throw new Error('Failed to fetch insights');
  return response.json();
}

export async function fetchRelatedBooks(id: number): Promise<Book[]> {
  const response = await fetch(`${API_BASE_URL}/books/${id}/related/`);
  if (!response.ok) throw new Error('Failed to fetch related books');
  return response.json();
}

export async function generateInsights(id: number): Promise<AIInsights> {
  const response = await fetch(`${API_BASE_URL}/books/${id}/insights/`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to generate insights');
  return response.json();
}

export async function askQuestion(question: string, bookId?: number): Promise<{
  question: string;
  answer: string;
  sources: { index: number; text: string }[];
}> {
  const response = await fetch(`${API_BASE_URL}/qa/ask/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, book_id: bookId }),
  });
  if (!response.ok) throw new Error('Failed to ask question');
  return response.json();
}

export async function fetchQAHistory(bookId?: number): Promise<QAHistory[]> {
  const params = bookId ? `?book_id=${bookId}` : '';
  const response = await fetch(`${API_BASE_URL}/qa/history/${params}`);
  if (!response.ok) throw new Error('Failed to fetch Q&A history');
  return response.json();
}

export async function seedBooks(): Promise<{ message: string; book_ids: number[] }> {
  const response = await fetch(`${API_BASE_URL}/seed/`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to seed books');
  return response.json();
}

export async function scrapeBooks(source = 'goodreads', count = 10): Promise<{
  message: string;
  book_ids: number[];
}> {
  const response = await fetch(`${API_BASE_URL}/scrape/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source, count }),
  });
  if (!response.ok) throw new Error('Failed to scrape books');
  return response.json();
}
