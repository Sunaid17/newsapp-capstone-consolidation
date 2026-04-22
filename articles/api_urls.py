"""
URL patterns for REST API.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from . import api

urlpatterns = [
    path(
        "token/",
        TokenObtainPairView.as_view(permission_classes=[AllowAny]),
        name="obtain_token",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=[AllowAny]),
        name="token_refresh",
    ),
    path("user/", api.UserDetailView.as_view(), name="user_detail"),
    path("articles/", api.ArticleListCreateView.as_view(), name="article_list_create"),
    path(
        "articles/subscribed/",
        api.SubscribedArticlesView.as_view(),
        name="subscribed_articles",
    ),
    path("articles/<int:pk>/", api.ArticleDetailView.as_view(), name="article_detail"),
    path(
        "articles/<int:article_id>/approve/",
        api.ArticleApproveView.as_view(),
        name="article_approve",
    ),
    path(
        "newsletters/",
        api.NewsletterListCreateView.as_view(),
        name="newsletter_list_create",
    ),
    path(
        "newsletters/<int:pk>/",
        api.NewsletterDetailView.as_view(),
        name="newsletter_detail",
    ),
    path("subscribe/", api.SubscribeView.as_view(), name="subscribe"),
    path("publishers/", api.PublisherListView.as_view(), name="publisher_list"),
    path("journalists/", api.JournalistsListView.as_view(), name="journalists_list"),
]
