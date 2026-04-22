"""
Admin configuration for articles models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    Journalist,
    Editor,
    Category,
    Article,
    Newsletter,
    Publisher,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""

    list_display = (
        "username",
        "email",
        "role",
        "publisher",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "is_active", "is_staff", "publisher")
    search_fields = ("username", "email")
    fieldsets = UserAdmin.fieldsets + (
        (
            "User Info",
            {
                "fields": (
                    "role",
                    "bio",
                    "profile_image",
                    "publisher",
                    "subscribed_publishers",
                    "subscribed_journalists",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (("User Info", {"fields": ("role",)}),)


@admin.register(Journalist)
class JournalistAdmin(admin.ModelAdmin):
    """Admin interface for Journalist model."""

    list_display = (
        "user",
        "specialization",
        "organization",
        "is_verified",
        "total_articles_written",
        "total_newsletters_sent",
    )
    list_filter = ("is_verified",)
    search_fields = ("user__username", "organization", "specialization")


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    """Admin interface for Editor model."""

    list_display = ("user", "department", "is_chief_editor", "articles_reviewed")
    list_filter = ("is_chief_editor",)
    search_fields = ("user__username", "department")


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Admin interface for Publisher model."""

    list_display = ("name", "is_verified", "is_independent", "created_at")
    list_filter = ("is_verified", "is_independent")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""

    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for Article model."""

    list_display = ("title", "author", "category", "status", "date", "reviewed_by")
    list_filter = ("status", "category", "date")
    search_fields = ("title", "content")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at", "reviewed_by")
    list_editable = ("status",)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin interface for Newsletter model."""

    list_display = ("title", "author", "category", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "content")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("status",)
