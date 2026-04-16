'use client';

import { useState, useEffect } from 'react';
import { Search, Loader2, Sparkles, Globe } from 'lucide-react';
import BookCard from '@/components/BookCard';
import { fetchBooks, seedBooks, scrapeBooks, Book } from '@/lib/api';

const GENRES = ['All', 'Fiction', 'Fantasy', 'Mystery', 'Science Fiction', 'Romance', 'Non-Fiction', 'Thriller'];

export default function Dashboard() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [seeding, setSeeding] = useState(false);
  const [scraping, setScraping] = useState(false);

  const loadBooks = async () => {
    setLoading(true);
    try {
      const genre = selectedGenre !== 'All' ? selectedGenre : '';
      const data = await fetchBooks(search, genre);
      setBooks(data);
    } catch (error) {
      console.error('Failed to load books:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks();
  }, []);

  const handleSeedBooks = async () => {
    setSeeding(true);
    try {
      await seedBooks();
      await loadBooks();
    } catch (error) {
      console.error('Failed to seed books:', error);
    } finally {
      setSeeding(false);
    }
  };

  const handleScrapeBooks = async () => {
    setScraping(true);
    try {
      await scrapeBooks('goodreads', 10);
      await loadBooks();
    } catch (error) {
      console.error('Failed to scrape books:', error);
    } finally {
      setScraping(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadBooks();
  };

  return (
    <div className="min-h-screen">
      <div className="bg-gradient-to-r from-primary to-secondary py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Discover Your Next Great Read
            </h1>
            <p className="text-xl text-white/80 mb-8">
              AI-powered book insights and intelligent Q&A
            </p>
            <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search books by title or author..."
                  className="w-full pl-12 pr-4 py-4 rounded-xl border-0 shadow-lg focus:outline-none focus:ring-2 focus:ring-accent text-lg"
                />
              </div>
            </form>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <h2 className="text-2xl font-bold text-text-primary">Books</h2>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleSeedBooks}
              disabled={seeding}
              className="flex items-center space-x-2 bg-secondary text-white px-4 py-2 rounded-lg hover:bg-secondary/90 transition-colors disabled:opacity-50"
            >
              {seeding ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              <span>{seeding ? 'Loading...' : 'Load Sample Books'}</span>
            </button>
            <button
              onClick={handleScrapeBooks}
              disabled={scraping}
              className="flex items-center space-x-2 bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent/90 transition-colors disabled:opacity-50"
            >
              {scraping ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Globe className="w-4 h-4" />
              )}
              <span>{scraping ? 'Scraping...' : 'Scrape Books'}</span>
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          {GENRES.map(genre => (
            <button
              key={genre}
              onClick={() => { setSelectedGenre(genre); loadBooks(); }}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                selectedGenre === genre || (genre === 'All' && !selectedGenre)
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-text-secondary hover:bg-gray-200'
              }`}
            >
              {genre}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <span className="ml-3 text-text-secondary">Loading books...</span>
          </div>
        ) : books.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-text-secondary text-lg">
              No books found. Click "Load Sample Books" to get started!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {books.map((book, idx) => (
              <div key={book.id} className="animate-fadeIn" style={{ animationDelay: `${idx * 50}ms` }}>
                <BookCard book={book} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}