"""
Models for the News Application.

This module defines the database models for users, articles, newsletters, and categories.
Includes CustomUser with role-based access control.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.

    Supports four roles:
    - 'reader': Can browse and bookmark articles, subscribe to publishers
    - 'journalist': Can create and manage their own articles and newsletters
    - 'editor': Can review, approve, and manage all articles
    - 'admin': Full system access
    """

    ROLE_CHOICES = [
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
        ("admin", "Admin"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="reader",
        help_text="User role determines permissions and access levels",
    )
    bio = models.TextField(
        blank=True, max_length=500, help_text="Short biography for content creators"
    )
    profile_image = models.URLField(blank=True, help_text="URL to profile image")
    publisher = models.ForeignKey(
        "Publisher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_members",
        help_text="Publisher organization this user belongs to",
    )
    subscribed_publishers = models.ManyToManyField(
        "Publisher",
        blank=True,
        related_name="subscribers",
        help_text="Publishers this user has subscribed to",
    )
    subscribed_journalists = models.ManyToManyField(
        "self",
        blank=True,
        related_name="subscribers",
        help_text="Journalists this user has subscribed to",
        symmetrical=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_reader(self):
        """Check if user is a reader."""
        return self.role == "reader"

    @property
    def is_journalist(self):
        """Check if user is a journalist."""
        return self.role == "journalist"

    @property
    def is_editor(self):
        """Check if user is an editor."""
        return self.role == "editor"

    @property
    def is_admin_role(self):
        """Check if user has admin role."""
        return self.role == "admin"

    @property
    def can_create_articles(self):
        """Check if user can create articles. Only journalists can create."""
        return self.role == "journalist"

    @property
    def can_create_newsletters(self):
        """Check if user can create newsletters. Journalists can create."""
        return self.role == "journalist"

    @property
    def can_edit_all_articles(self):
        """Check if user can edit all articles."""
        return self.role in ["editor", "admin"]

    @property
    def can_review_articles(self):
        """Check if user can review pending articles."""
        return self.role in ["editor", "admin"]


class Publisher(models.Model):
    """
    Publisher model representing news organizations.
    Journalists can join publishers, readers can subscribe.
    """

    name = models.CharField(
        max_length=200, unique=True, help_text="Publisher organization name"
    )
    description = models.TextField(blank=True, help_text="Description of the publisher")
    website = models.URLField(blank=True, help_text="Publisher website URL")
    logo = models.URLField(blank=True, help_text="Publisher logo URL")
    is_verified = models.BooleanField(
        default=False, help_text="Verification status of the publisher"
    )
    is_independent = models.BooleanField(
        default=False, help_text="Whether this is an independent publisher"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "publishers"
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        """Get number of staff members."""
        return self.staff_members.count()

    @property
    def subscriber_count(self):
        """Get number of subscribers."""
        return self.subscribed_users.count()


class Journalist(models.Model):
    """
    Journalist profile model linked to CustomUser.
    Contains additional information for content creators.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="journalist_profile",
        help_text="Associated journalist user account",
    )
    specialization = models.CharField(
        max_length=200, blank=True, help_text="Area of journalism specialization"
    )
    organization = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journalists",
        help_text="Publisher organization",
    )
    is_verified = models.BooleanField(
        default=False, help_text="Verification status of the journalist"
    )
    total_articles_written = models.PositiveIntegerField(
        default=0, help_text="Count of articles written by this journalist"
    )
    total_newsletters_sent = models.PositiveIntegerField(
        default=0, help_text="Count of newsletters sent by this journalist"
    )

    class Meta:
        db_table = "journalists"
        verbose_name = "Journalist"
        verbose_name_plural = "Journalists"

    def __str__(self):
        return f"Journalist: {self.user.username}"

    def increment_article_count(self):
        """Increment the article count by 1."""
        self.total_articles_written += 1
        self.save()

    def decrement_article_count(self):
        """Decrement the article count by 1."""
        if self.total_articles_written > 0:
            self.total_articles_written -= 1
            self.save()

    def increment_newsletter_count(self):
        """Increment the newsletter count by 1."""
        self.total_newsletters_sent += 1
        self.save()


class Editor(models.Model):
    """
    Editor profile model linked to CustomUser.
    Editors can review and approve articles from journalists.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="editor_profile",
        help_text="Associated editor user account",
    )
    department = models.CharField(
        max_length=100, blank=True, help_text="Editorial department"
    )
    is_chief_editor = models.BooleanField(
        default=False, help_text="Whether this is a chief/senior editor"
    )
    articles_reviewed = models.PositiveIntegerField(
        default=0, help_text="Count of articles reviewed by this editor"
    )

    class Meta:
        db_table = "editors"
        verbose_name = "Editor"
        verbose_name_plural = "Editors"

    def __str__(self):
        return f"Editor: {self.user.username}"

    def increment_review_count(self):
        """Increment the review count by 1."""
        self.articles_reviewed += 1
        self.save()


class Category(models.Model):
    """
    Category model for organizing articles by topic.
    """

    name = models.CharField(max_length=50, unique=True, help_text="Category name")
    description = models.TextField(
        blank=True, help_text="Brief description of the category"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this category is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Article model representing news articles.
    Supports different statuses and publishing workflow.
    Journalists create articles, editors review and publish them.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending Review"),
        ("published", "Published"),
        ("rejected", "Rejected"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=200, help_text="Article title")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="articles",
        help_text="Article category",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="articles",
        help_text="Article author (journalist)",
    )
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_articles",
        help_text="Editor who reviewed this article",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Article publication status",
    )
    rejection_reason = models.TextField(
        blank=True, help_text="Reason for rejection (if applicable)"
    )
    date = models.DateField(auto_now_add=True, help_text="Creation date")
    published_date = models.DateField(
        null=True, blank=True, help_text="Date when article was published"
    )
    image = models.URLField(blank=True, null=True, help_text="URL to article image")
    content = models.TextField(help_text="Article content")
    bookmarked_by = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name="bookmarked_articles",
        help_text="Users who bookmarked this article",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "articles"
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-date"]

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        """Check if article is published."""
        return self.status == "published"

    @property
    def is_pending(self):
        """Check if article is pending review."""
        return self.status == "pending"

    @property
    def can_be_edited_by(self, user):
        """Check if a user can edit this article."""
        if user.role in ["admin", "editor"]:
            return True
        if user.role == "journalist" and self.author == user:
            return self.status in ["draft", "pending", "rejected"]
        return False


class Newsletter(models.Model):
    """
    Newsletter model for periodic news updates.
    Journalists can create and send newsletters to subscribers.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("sent", "Sent"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=200, help_text="Newsletter title")
    subject = models.CharField(max_length=200, help_text="Email subject line")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletters",
        help_text="Newsletter category",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="newsletters",
        help_text="Newsletter author (journalist)",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Newsletter status",
    )
    content = models.TextField(help_text="Newsletter content")
    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name="newsletters",
        help_text="Articles featured in this newsletter",
    )
    scheduled_date = models.DateTimeField(
        null=True, blank=True, help_text="When to send the newsletter"
    )
    sent_date = models.DateTimeField(
        null=True, blank=True, help_text="When the newsletter was sent"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "newsletters"
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletters"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_sent(self):
        """Check if newsletter was sent."""
        return self.status == "sent"
