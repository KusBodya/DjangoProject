# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.quotes_list, name="quotes_list"),
    path("random/", views.random_quote, name="random_quote"),
    path("quotes/<int:pk>/like/", views.quote_like, name="quote_like"),
    path("quotes/<int:pk>/dislike/", views.quote_dislike, name="quote_dislike"),
    path("quotes/<int:pk>/views/", views.quote_view, name="quote_view"),
    path("liked/", views.liked_quotes, name="liked_quotes"),
    path("unvoted/", views.unvoted_quotes, name="unvoted_quotes"),
]
