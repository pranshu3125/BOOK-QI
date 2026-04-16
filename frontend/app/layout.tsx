import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'BookMind - Document Intelligence Platform',
  description: 'AI-powered book analysis and Q&A platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <nav className="bg-primary text-white shadow-lg sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-8">
                <Link href="/" className="text-xl font-bold flex items-center space-x-2">
                  <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  <span>BookMind</span>
                </Link>
                <div className="hidden md:flex items-center space-x-4">
                  <Link href="/" className="hover:bg-white/10 px-3 py-2 rounded-md transition-colors">
                    Dashboard
                  </Link>
                  <Link href="/qa" className="hover:bg-white/10 px-3 py-2 rounded-md transition-colors">
                    Q&A
                  </Link>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <button className="bg-accent hover:bg-orange-600 px-4 py-2 rounded-md text-sm font-medium transition-colors">
                  Get Started
                </button>
              </div>
            </div>
          </div>
        </nav>
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="bg-primary text-white py-8 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <p className="text-sm text-gray-300">
              &copy; 2026 BookMind. Document Intelligence Platform.
            </p>
          </div>
        </footer>
      </body>
    </html>
  )
}
