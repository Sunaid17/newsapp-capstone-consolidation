"""
URL patterns for articles app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("bookmarks/", views.bookmarks, name="bookmarks"),
    path("my_articles/", views.my_articles, name="my_articles"),
    path("my_newsletters/", views.my_newsletters, name="my_newsletters"),
    path("pending_articles/", views.pending_articles, name="pending_articles"),
    path("categories/", views.manage_categories, name="manage_categories"),
    path("create_article/", views.create_article, name="create_article"),
    path("create_newsletter/", views.create_newsletter, name="create_newsletter"),
    path("store_article/", views.store_article, name="store_article"),
    path("store_newsletter/", views.store_newsletter, name="store_newsletter"),
    path("article/<int:article_id>/", views.article_detail, name="article_detail"),
    path(
        "update_article/<int:article_id>/", views.update_article, name="update_article"
    ),
    path(
        "toggle_bookmark/<int:article_id>/",
        views.toggle_bookmark,
        name="toggle_bookmark",
    ),
    path(
        "delete_article/<int:article_id>/", views.delete_article, name="delete_article"
    ),
    path(
        "delete_newsletter/<int:newsletter_id>/",
        views.delete_newsletter,
        name="delete_newsletter",
    ),
    path(
        "submit_article/<int:article_id>/", views.submit_article, name="submit_article"
    ),
    path(
        "approve_article/<int:article_id>/",
        views.approve_article,
        name="approve_article",
    ),
    path(
        "reject_article/<int:article_id>/", views.reject_article, name="reject_article"
    ),
    path("api/articles/", views.api_articles, name="api_articles"),
    path("api/categories/", views.api_categories, name="api_categories"),
    path("api/publishers/", views.api_publishers, name="api_publishers"),
]
