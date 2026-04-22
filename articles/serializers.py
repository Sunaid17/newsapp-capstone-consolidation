"""
Serializers for the REST API.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Article, Category, Newsletter, Publisher, CustomUser

CustomUser = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "bio", "profile_image"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "is_active"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = [
            "id",
            "name",
            "description",
            "website",
            "logo",
            "is_verified",
            "is_independent",
        ]


class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "image",
            "category",
            "category_id",
            "author",
            "status",
            "rejection_reason",
            "date",
            "published_date",
            "bookmarked_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "status",
            "date",
            "created_at",
            "updated_at",
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    articles = ArticleSerializer(many=True, read_only=True)
    article_ids = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(), source="articles", many=True, write_only=True
    )

    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "subject",
            "content",
            "category",
            "author",
            "status",
            "articles",
            "article_ids",
            "scheduled_date",
            "sent_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "status",
            "sent_date",
            "created_at",
            "updated_at",
        ]


class SubscriptionSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["publisher", "journalist"])
    publisher_id = serializers.IntegerField(required=False)
    journalist_id = serializers.IntegerField(required=False)
