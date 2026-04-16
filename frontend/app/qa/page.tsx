'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Loader2, MessageCircle, BookOpen } from 'lucide-react';
import QuestionInput from '@/components/QuestionInput';
import AnswerCard from '@/components/AnswerCard';
import { fetchBooks, askQuestion, fetchQAHistory, Book, QAHistory } from '@/lib/api';

export default function QAPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedBook, setSelectedBook] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [answer, setAnswer] = useState<{ question: string; answer: string; sources: any[] } | null>(null);
  const [answerLoading, setAnswerLoading] = useState(false);
  const [history, setHistory] = useState<QAHistory[]>([]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [booksData, historyData] = await Promise.all([
          fetchBooks(),
          fetchQAHistory(),
        ]);
        setBooks(booksData);
        setHistory(historyData);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleAskQuestion = async (question: string) => {
    setAnswerLoading(true);
    try {
      const data = await askQuestion(question, selectedBook || undefined);
      setAnswer(data);
      setHistory(prev => [{ id: data.qa_id || Date.now(), book: selectedBook, book_title: books.find(b => b.id === selectedBook)?.title || 'General', question: data.question, answer: data.answer, sources: data.sources, created_at: new Date().toISOString() }, ...prev]);
    } catch (error) {
      console.error('Failed to ask question:', error);
    } finally {
      setAnswerLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary mb-2">Question & Answer</h1>
        <p className="text-text-secondary">
          Ask questions about any book and get AI-powered answers with source citations
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-surface rounded-xl shadow-md p-6">
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Select a book (optional)
            </label>
            <select
              value={selectedBook || ''}
              onChange={(e) => setSelectedBook(e.target.value ? Number(e.target.value) : null)}
              className="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="">All books (general query)</option>
              {books.map((book) => (
                <option key={book.id} value={book.id}>
                  {book.title}
                </option>
              ))}
            </select>
          </div>

          <QuestionInput onSubmit={handleAskQuestion} disabled={answerLoading} />

          {answer && (
            <AnswerCard
              question={answer.question}
              answer={answer.answer}
              sources={answer.sources}
            />
          )}
        </div>

        <div className="lg:col-span-1">
          <div className="bg-surface rounded-xl shadow-md p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center space-x-2">
              <MessageCircle className="w-5 h-5" />
              <span>Recent Questions</span>
            </h2>
            {history.length === 0 ? (
              <p className="text-text-secondary text-sm">No questions yet</p>
            ) : (
              <div className="space-y-3">
                {history.slice(0, 10).map((item) => (
                  <div key={item.id} className="p-3 bg-gray-50 rounded-lg">
                    {item.book_title && (
                      <p className="text-xs text-primary mb-1">{item.book_title}</p>
                    )}
                    <p className="text-sm font-medium text-text-primary line-clamp-2">
                      {item.question}
                    </p>
                    <p className="text-xs text-text-secondary mt-1">
                      {new Date(item.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-surface rounded-xl shadow-md p-6 mt-4">
            <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center space-x-2">
              <BookOpen className="w-5 h-5" />
              <span>Sample Questions</span>
            </h2>
            <div className="space-y-2">
              {['What is this book about?', 'Who is the main character?', 'What genre is this book?', 'What are the main themes?', 'Is this book worth reading?'].map((q) => (
                <button
                  key={q}
                  onClick={() => handleAskQuestion(q)}
                  disabled={answerLoading}
                  className="w-full text-left p-2 text-sm text-text-secondary hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
