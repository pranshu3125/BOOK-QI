'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import Link from 'next/link';
import { ArrowLeft, Star, Loader2, ExternalLink } from 'lucide-react';
import BookCard from '@/components/BookCard';
import InsightCard from '@/components/InsightCard';
import QuestionInput from '@/components/QuestionInput';
import AnswerCard from '@/components/AnswerCard';
import {
  fetchBookDetail,
  fetchBookInsights,
  fetchRelatedBooks,
  generateInsights,
  askQuestion,
  Book,
  AIInsights,
} from '@/lib/api';

export default function BookDetail() {
  const router = useRouter();
  const { id } = router.query;

  const [book, setBook] = useState<Book | null>(null);
  const [insights, setInsights] = useState<AIInsights | null>(null);
  const [relatedBooks, setRelatedBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [answer, setAnswer] = useState<{ question: string; answer: string; sources: any[] } | null>(null);
  const [answerLoading, setAnswerLoading] = useState(false);

  useEffect(() => {
    if (!id) return;

    const loadData = async () => {
      setLoading(true);
      try {
        const [bookData, insightsData, relatedData] = await Promise.all([
          fetchBookDetail(Number(id)),
          fetchBookInsights(Number(id)).catch(() => null),
          fetchRelatedBooks(Number(id)),
        ]);
        setBook(bookData);
        setInsights(insightsData);
        setRelatedBooks(relatedData);
      } catch (error) {
        console.error('Failed to load book:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id]);

  const handleGenerateInsights = async () => {
    if (!id) return;
    setInsightsLoading(true);
    try {
      const data = await generateInsights(Number(id));
      setInsights(data);
    } catch (error) {
      console.error('Failed to generate insights:', error);
    } finally {
      setInsightsLoading(false);
    }
  };

  const handleAskQuestion = async (question: string) => {
    if (!id) return;
    setAnswerLoading(true);
    try {
      const data = await askQuestion(question, Number(id));
      setAnswer(data);
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

  if (!book) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-center">
        <p className="text-text-secondary text-lg">Book not found</p>
        <Link href="/" className="text-primary hover:underline mt-4 inline-block">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link
        href="/"
        className="inline-flex items-center space-x-2 text-text-secondary hover:text-primary transition-colors mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Dashboard</span>
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        <div className="lg:col-span-1">
          <div className="bg-surface rounded-xl shadow-md overflow-hidden sticky top-24">
            <div className="relative aspect-[2/3] bg-gray-200">
              {book.cover_url ? (
                <Image src={book.cover_url} alt={book.title} fill className="object-cover" />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center">
                  <Star className="w-16 h-16 text-gray-400" />
                </div>
              )}
            </div>
            {book.book_url && (
              <a
                href={book.book_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center space-x-2 p-3 bg-primary text-white hover:bg-primary/90 transition-colors"
              >
                <span>View Book</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="bg-surface rounded-xl shadow-md p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-text-primary mb-2">{book.title}</h1>
                <p className="text-lg text-text-secondary">{book.author}</p>
              </div>
              <div className="flex items-center space-x-1 bg-accent/10 px-3 py-1 rounded-full">
                <Star className="w-5 h-5 text-accent fill-current" />
                <span className="font-semibold text-accent">{book.rating?.toFixed(1) || 'N/A'}</span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-6">
              <span className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-medium">
                {book.genre || 'Fiction'}
              </span>
              <span className="bg-gray-100 text-text-secondary px-3 py-1 rounded-full text-sm">
                {book.review_count} reviews
              </span>
              {book.price && (
                <span className="bg-success/10 text-success px-3 py-1 rounded-full text-sm">
                  {book.price}
                </span>
              )}
            </div>

            {book.description && (
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-text-primary mb-2">Description</h2>
                <p className="text-text-secondary whitespace-pre-wrap">{book.description}</p>
              </div>
            )}

            <div className="mb-6">
              <h2 className="text-lg font-semibold text-text-primary mb-4">Ask a Question</h2>
              <QuestionInput onSubmit={handleAskQuestion} disabled={answerLoading} />
              {answer && (
                <div className="mt-4">
                  <AnswerCard question={answer.question} answer={answer.answer} sources={answer.sources} />
                </div>
              )}
            </div>
          </div>

          <div className="mt-8">
            <h2 className="text-xl font-bold text-text-primary mb-4">AI Insights</h2>
            {!insights ? (
              <button
                onClick={handleGenerateInsights}
                disabled={insightsLoading}
                className="flex items-center space-x-2 bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {insightsLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Star className="w-5 h-5" />
                )}
                <span>{insightsLoading ? 'Generating...' : 'Generate AI Insights'}</span>
              </button>
            ) : (
              <div className="space-y-4">
                <InsightCard title="Summary" content={insights.summary || 'No summary available'} icon="summary" onRefresh={handleGenerateInsights} loading={insightsLoading} />
                <InsightCard title="Genre Prediction" content={insights.genre_prediction || 'Unknown'} icon="genre" />
                <InsightCard title="Sentiment Analysis" content={insights.sentiment || 'Unknown'} icon="sentiment" />
                <InsightCard title="Recommendations" content={insights.recommendations?.join('\n') || 'No recommendations yet'} icon="recommendations" />
              </div>
            )}
          </div>
        </div>
      </div>

      {relatedBooks.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-text-primary mb-4">Related Books</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {relatedBooks.map((rb) => (
              <BookCard key={rb.id} book={rb} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
