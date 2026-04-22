"""
REST API views for the News Application.
Uses Django REST Framework with JWT authentication.
"""

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Article, Category, Newsletter, Publisher, CustomUser
from .serializers import (
    ArticleSerializer,
    NewsletterSerializer,
    UserSerializer,
    PublisherSerializer,
    SubscriptionSerializer,
)

CustomUser = get_user_model()


class IsReader(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.role == "reader"


class IsJournalist(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.role == "journalist"


class IsEditor(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.role == "editor"


class IsPublisherOrJournalist(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.role in ["journalist", "editor", "admin"]


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "journalist":
            return Article.objects.filter(author=user)
        elif user.role == "editor":
            return Article.objects.all()
        return Article.objects.filter(status="published")

    def create(self, request, *args, **kwargs):
        if not request.user.can_create_articles:
            return Response(
                {"error": "Only journalists can create articles"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, status="pending")


class SubscribedArticlesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "reader":
            return Response(
                {"error": "Only readers can access subscribed content"},
                status=status.HTTP_403_FORBIDDEN,
            )

        subscribed_publishers = user.subscribed_publishers.all()
        subscribed_journalists = user.subscribed_journalists.filter(role="journalist")

        from articles.models import Journalist

        journalist_users = Journalist.objects.filter(
            organization__in=subscribed_publishers
        ).values_list("user", flat=True)

        articles = Article.objects.filter(status="published").filter(
            author__in=list(subscribed_journalists) + list(journalist_users)
        ) | Article.objects.filter(
            status="published",
            author__journalist_profile__organization__in=subscribed_publishers,
        )

        articles = articles.distinct().order_by("-published_date", "-date")
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "journalist":
            return Article.objects.filter(author=user)
        return Article.objects.all()


class ArticleApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_id):
        if not request.user.can_review_articles:
            return Response(
                {"error": "Only editors can approve articles"},
                status=status.HTTP_403_FORBIDDEN,
            )

        article = get_object_or_404(Article, id=article_id)

        action = request.data.get("action", "approve")

        if action == "approve":
            article.status = "published"
            article.reviewed_by = request.user
            from django.utils import timezone

            article.published_date = timezone.now().date()
            article.save()
            return Response(
                {"status": "approved", "article": ArticleSerializer(article).data}
            )
        elif action == "reject":
            article.status = "rejected"
            article.reviewed_by = request.user
            article.rejection_reason = request.data.get("reason", "")
            article.save()
            return Response(
                {"status": "rejected", "article": ArticleSerializer(article).data}
            )

        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class NewsletterListCreateView(generics.ListCreateAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "journalist":
            return Newsletter.objects.filter(author=user)
        return Newsletter.objects.filter(status="sent")

    def create(self, request, *args, **kwargs):
        if not request.user.can_create_newsletters:
            return Response(
                {"error": "Only journalists can create newsletters"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class NewsletterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [IsAuthenticated]


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != "reader":
            return Response(
                {"error": "Only readers can subscribe"},
                status=status.HTTP_403_FORBIDDEN,
            )

        subscribe_type = request.data.get("type")

        if subscribe_type == "publisher":
            publisher_id = request.data.get("publisher_id")
            publisher = get_object_or_404(Publisher, id=publisher_id)
            request.user.subscribed_publishers.add(publisher)
            return Response(
                {
                    "status": "subscribed",
                    "publisher": PublisherSerializer(publisher).data,
                }
            )

        elif subscribe_type == "journalist":
            journalist_id = request.data.get("journalist_id")
            journalist = get_object_or_404(
                CustomUser, id=journalist_id, role="journalist"
            )
            request.user.subscribed_journalists.add(journalist)
            return Response(
                {"status": "subscribed", "journalist": UserSerializer(journalist).data}
            )

        return Response(
            {"error": "Invalid subscription type"}, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        subscribe_type = request.data.get("type")

        if subscribe_type == "publisher":
            publisher_id = request.data.get("publisher_id")
            publisher = get_object_or_404(Publisher, id=publisher_id)
            request.user.subscribed_publishers.remove(publisher)
            return Response({"status": "unsubscribed"})

        elif subscribe_type == "journalist":
            journalist_id = request.data.get("journalist_id")
            journalist = get_object_or_404(CustomUser, id=journalist_id)
            request.user.subscribed_journalists.remove(journalist)
            return Response({"status": "unsubscribed"})

        return Response(
            {"error": "Invalid subscription type"}, status=status.HTTP_400_BAD_REQUEST
        )


class PublisherListView(generics.ListAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]


class JournalistsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from articles.models import Journalist

        journalists = Journalist.objects.filter(is_verified=True)
        data = []
        for j in journalists:
            data.append(
                {
                    "id": j.user.id,
                    "username": j.user.username,
                    "specialization": j.specialization,
                    "organization": j.organization.name if j.organization else None,
                }
            )
        return Response(data)
