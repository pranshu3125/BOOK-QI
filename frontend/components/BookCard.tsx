import Link from 'next/link';
import Image from 'next/image';
import { Star, BookOpen } from 'lucide-react';
import type { Book } from '@/lib/api';

interface BookCardProps {
  book: Book;
}

export default function BookCard({ book }: BookCardProps) {
  return (
    <Link href={`/book/${book.id}`}>
      <div className="bg-surface rounded-xl shadow-md hover:shadow-xl transition-all duration-300 hover:scale-[1.02] overflow-hidden group">
        <div className="relative aspect-[2/3] bg-gray-200">
          {book.cover_url ? (
            <Image
              src={book.cover_url}
              alt={book.title}
              fill
              className="object-cover"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <BookOpen className="w-16 h-16 text-gray-400" />
            </div>
          )}
          <div className="absolute top-2 right-2 bg-accent text-white px-2 py-1 rounded-full text-xs font-medium">
            {book.genre || 'Fiction'}
          </div>
        </div>
        <div className="p-4">
          <h3 className="font-semibold text-text-primary truncate group-hover:text-primary transition-colors">
            {book.title}
          </h3>
          <p className="text-sm text-text-secondary mt-1 truncate">
            {book.author || 'Unknown Author'}
          </p>
          <div className="flex items-center mt-2">
            {book.rating && (
              <>
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
                <span className="ml-1 text-sm font-medium text-text-primary">
                  {book.rating.toFixed(1)}
                </span>
              </>
            )}
            <span className="ml-auto text-xs text-text-secondary">
              {book.review_count} reviews
            </span>
          </div>
          {book.description && (
            <p className="text-sm text-text-secondary mt-2 line-clamp-2">
              {book.description}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}
