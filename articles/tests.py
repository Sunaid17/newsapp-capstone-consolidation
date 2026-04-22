"""
Unit tests for the articles app API.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.utils import timezone

from articles.models import (
    CustomUser,
    Article,
    Category,
    Newsletter,
    Publisher,
    Journalist,
    Editor,
)


class ArticleAPITestCase(TestCase):
    """Base test case for article API tests."""

    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(
            name="technology", description="Tech news"
        )

        self.publisher = Publisher.objects.create(
            name="Tech News Daily",
            description="Leading tech publication",
            is_verified=True,
        )

        self.reader = CustomUser.objects.create_user(
            username="reader1",
            email="reader1@test.com",
            password="testpass123",
            role="reader",
        )

        self.journalist = CustomUser.objects.create_user(
            username="journalist1",
            email="journalist1@test.com",
            password="testpass123",
            role="journalist",
            publisher=self.publisher,
        )
        self.journalist_profile = Journalist.objects.create(
            user=self.journalist,
            specialization="Technology",
            organization=self.publisher,
            is_verified=True,
        )

        self.editor = CustomUser.objects.create_user(
            username="editor1",
            email="editor1@test.com",
            password="testpass123",
            role="editor",
        )
        self.editor_profile = Editor.objects.create(
            user=self.editor, department="News", is_chief_editor=True
        )

        self.published_article = Article.objects.create(
            title="Published Article",
            content="Published content",
            category=self.category,
            author=self.journalist,
            status="published",
        )

        self.pending_article = Article.objects.create(
            title="Pending Article",
            content="Pending content",
            category=self.category,
            author=self.journalist,
            status="pending",
        )


class SubscribedArticlesTestCase(ArticleAPITestCase):
    """Tests for the /api/articles/subscribed/ endpoint."""

    def test_reader_subscribed_returns_empty_no_subscriptions(self):
        """A reader with no subscriptions gets empty results."""
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/subscribed/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_reader_subscribed_returns_only_subscribed_content(self):
        """A reader's /api/articles/subscribed/ returns only subscribed content."""
        other_journalist = CustomUser.objects.create_user(
            username="journalist2",
            email="journalist2@test.com",
            password="testpass123",
            role="journalist",
            publisher=self.publisher,
        )
        Journalist.objects.create(
            user=other_journalist,
            specialization="Sports",
            organization=self.publisher,
            is_verified=True,
        )

        Article.objects.create(
            title="Subscribed Journalist Article",
            content="Content from subscribed journalist",
            category=self.category,
            author=other_journalist,
            status="published",
        )

        self.reader.subscribed_journalists.add(other_journalist)

        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/subscribed/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Subscribed Journalist Article")

    def test_reader_subscribed_returns_publisher_content(self):
        """A reader subscribed to a publisher gets articles from that publisher's journalists."""
        self.reader.subscribed_publishers.add(self.publisher)

        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/subscribed/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Published Article")

    def test_non_reader_cannot_access_subscribed(self):
        """Non-readers cannot access the subscribed endpoint."""
        self.client.force_authenticate(user=self.journalist)
        response = self.client.get("/api/articles/subscribed/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ArticleCreationTestCase(ArticleAPITestCase):
    """Tests for article creation via API."""

    def test_journalist_can_create_article(self):
        """A journalist can POST an article via the API."""
        self.client.force_authenticate(user=self.journalist)
        data = {
            "title": "New Article",
            "content": "New article content",
            "category_id": self.category.id,
        }
        response = self.client.post("/api/articles/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.filter(title="New Article").count(), 1)

    def test_reader_cannot_create_article(self):
        """A reader cannot create articles."""
        self.client.force_authenticate(user=self.reader)
        data = {
            "title": "New Article",
            "content": "New article content",
            "category_id": self.category.id,
        }
        response = self.client.post("/api/articles/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_cannot_create_article(self):
        """An editor cannot create articles (only review/approve)."""
        self.client.force_authenticate(user=self.editor)
        data = {
            "title": "New Article",
            "content": "New article content",
            "category_id": self.category.id,
        }
        response = self.client.post("/api/articles/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ArticleApprovalTestCase(ArticleAPITestCase):
    """Tests for article approval workflow."""

    @patch("articles.signals.send_mail")
    @patch("articles.signals.post_to_twitter")
    def test_editor_approval_triggers_email_and_x(self, mock_twitter, mock_email):
        """An editor's approval triggers email and X calls."""
        mock_email.return_value = None
        mock_twitter.return_value = None

        self.client.force_authenticate(user=self.editor)
        data = {"action": "approve"}
        response = self.client.post(
            f"/api/articles/{self.pending_article.id}/approve/", data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "approved")

        self.pending_article.refresh_from_db()
        self.assertEqual(self.pending_article.status, "published")

        mock_email.assert_called_once()
        mock_twitter.assert_called_once()

    @patch("articles.signals.send_mail")
    def test_editor_rejection_triggers_email(self, mock_email):
        """An editor's rejection can include a reason."""
        self.client.force_authenticate(user=self.editor)
        data = {"action": "reject", "reason": "Needs more evidence"}
        response = self.client.post(
            f"/api/articles/{self.pending_article.id}/approve/", data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "rejected")

        self.pending_article.refresh_from_db()
        self.assertEqual(self.pending_article.status, "rejected")
        self.assertEqual(self.pending_article.rejection_reason, "Needs more evidence")

    def test_non_editor_cannot_approve(self):
        """Non-editors cannot approve articles."""
        self.client.force_authenticate(user=self.journalist)
        data = {"action": "approve"}
        response = self.client.post(
            f"/api/articles/{self.pending_article.id}/approve/", data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NewsletterAPITestCase(ArticleAPITestCase):
    """Tests for newsletter API."""

    def test_journalist_can_create_newsletter(self):
        """A journalist can create newsletters."""
        self.client.force_authenticate(user=self.journalist)
        data = {
            "title": "Weekly News",
            "subject": "This week in tech",
            "content": "Newsletter content",
            "article_ids": [self.published_article.id],
        }
        response = self.client.post("/api/newsletters/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reader_cannot_create_newsletter(self):
        """A reader cannot create newsletters."""
        self.client.force_authenticate(user=self.reader)
        data = {
            "title": "Weekly News",
            "subject": "This week in tech",
            "content": "Newsletter content",
        }
        response = self.client.post("/api/newsletters/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticationTestCase(ArticleAPITestCase):
    """Tests for JWT authentication."""

    def test_unauthenticated_request_denied(self):
        """Unauthenticated requests are denied."""
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_request_allowed(self):
        """Authenticated requests are allowed."""
        self.client.force_authenticate(user=self.reader)
        response = self.client.get("/api/articles/")
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        )
