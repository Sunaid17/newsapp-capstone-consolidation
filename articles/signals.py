"""
Signals for the articles app.
Handles email notifications and social media posts when articles are approved.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Article


@receiver(post_save, sender=Article)
def article_status_changed(sender, instance, **kwargs):
    """
    Send notifications when an article is published.
    Handles email to subscribers and social media posts.
    """
    if instance.status == "published" and instance.reviewed_by:
        send_article_notification(instance)


def send_article_notification(article):
    """
    Send email notification to subscribers when an article is published.
    Also posts to social media (X/Twitter).
    """
    if article.author and article.author.email:
        send_mail(
            f'Your article "{article.title}" has been published!',
            f"Your article has been published and is now live on the site.\n\nView it at: /articles/{article.id}/",
            settings.DEFAULT_FROM_EMAIL,
            [article.author.email],
            fail_silently=False,
        )

    post_to_twitter(article)


def post_to_twitter(article):
    """
    Post article to X (Twitter).
    This is a placeholder - implement actual Twitter API integration.
    """
    pass
