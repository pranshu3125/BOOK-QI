from django.urls import path
from .views import (
    BookViewSet, BookListView, BookDetailView, BookChunksView,
    BookInsightsView, BookRelatedView, ScrapeBooksView,
    GenerateEmbeddingsView, AskQuestionView, QAHistoryView, SeedBooksView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('seed/', SeedBooksView.as_view(), name='seed-books'),
    path('scrape/', ScrapeBooksView.as_view(), name='scrape-books'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:pk>/chunks/', BookChunksView.as_view(), name='book-chunks'),
    path('books/<int:pk>/insights/', BookInsightsView.as_view(), name='book-insights'),
    path('books/<int:pk>/related/', BookRelatedView.as_view(), name='book-related'),
    path('books/<int:pk>/embeddings/', GenerateEmbeddingsView.as_view(), name='generate-embeddings'),
    path('qa/ask/', AskQuestionView.as_view(), name='ask-question'),
    path('qa/history/', QAHistoryView.as_view(), name='qa-history'),
]
