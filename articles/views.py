"""
Views for articles app including home, bookmarks, article detail, and CRUD operations.

Supports journalist and editor workflow:
- Journalists can create, edit, and submit articles and newsletters
- Editors can review, approve, or reject articles (but NOT create)
- Readers can browse and bookmark published articles
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Article, Category, Newsletter, Publisher, Journalist, Editor
import json


def home(request):
    """
    Display the home page with published articles.

    This view shows all published articles to all users (both authenticated and anonymous).
    """
    categories = Category.objects.filter(is_active=True)
    articles = Article.objects.filter(status="published").order_by(
        "-published_date", "-date"
    )

    bookmark_ids = []
    if request.user.is_authenticated:
        bookmark_ids = list(
            request.user.bookmarked_articles.values_list("id", flat=True)
        )

    return render(
        request,
        "home.html",
        {"categories": categories, "articles": articles, "bookmark_ids": bookmark_ids},
    )


def bookmarks(request):
    """
    Display bookmarked articles for the authenticated user.

    Only accessible to logged-in users. Shows articles that the user has bookmarked.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Please login to view your bookmarks.")
        return redirect("login")

    categories = Category.objects.filter(is_active=True)
    bookmarked_articles = request.user.bookmarked_articles.filter(
        status="published"
    ).order_by("-date")
    bookmark_ids = list(request.user.bookmarked_articles.values_list("id", flat=True))

    return render(
        request,
        "home.html",
        {
            "categories": categories,
            "articles": bookmarked_articles,
            "bookmark_ids": bookmark_ids,
            "view": "bookmarks",
        },
    )


@login_required
def my_articles(request):
    """
    Display articles created by the current journalist.

    Only accessible to users with journalist role. Shows articles written by the journalist.
    """
    if not request.user.can_create_articles:
        messages.error(request, "Only journalists can view their articles.")
        return redirect("home")

    categories = Category.objects.filter(is_active=True)
    articles = Article.objects.filter(author=request.user).order_by("-date")
    bookmark_ids = list(request.user.bookmarked_articles.values_list("id", flat=True))

    return render(
        request,
        "my_articles.html",
        {"categories": categories, "articles": articles, "bookmark_ids": bookmark_ids},
    )


@login_required
def my_newsletters(request):
    """
    Display newsletters created by the current journalist.

    Only accessible to users with journalist role.
    """
    if not request.user.can_create_newsletters:
        messages.error(request, "Only journalists can manage newsletters.")
        return redirect("home")

    categories = Category.objects.filter(is_active=True)
    newsletters = Newsletter.objects.filter(author=request.user).order_by("-created_at")

    return render(
        request,
        "my_newsletters.html",
        {"categories": categories, "newsletters": newsletters},
    )


@login_required
def pending_articles(request):
    """
    Display articles pending review for editors.

    Only accessible to users with editor role. Shows articles awaiting approval.
    Note: Editors CANNOT create articles, only review them.
    """
    if not request.user.can_review_articles:
        messages.error(request, "Only editors can review articles.")
        return redirect("home")

    categories = Category.objects.filter(is_active=True)
    articles = Article.objects.filter(status="pending").order_by("-date")
    bookmark_ids = list(request.user.bookmarked_articles.values_list("id", flat=True))

    return render(
        request,
        "pending_articles.html",
        {"categories": categories, "articles": articles, "bookmark_ids": bookmark_ids},
    )


@login_required
def create_article(request):
    """
    Display the create article form.

    Only accessible to users with journalist role. Editors cannot create articles.
    """
    if not request.user.can_create_articles:
        messages.error(request, "Only journalists can create articles.")
        return redirect("home")

    categories = Category.objects.filter(is_active=True)
    publishers = Publisher.objects.all()

    return render(
        request,
        "create_article.html",
        {"categories": categories, "publishers": publishers},
    )


@login_required
def create_newsletter(request):
    """
    Display the create newsletter form.

    Only accessible to users with journalist role.
    """
    if not request.user.can_create_newsletters:
        messages.error(request, "Only journalists can create newsletters.")
        return redirect("home")

    categories = Category.objects.filter(is_active=True)
    articles = Article.objects.filter(author=request.user, status="published")

    return render(
        request,
        "create_newsletter.html",
        {"categories": categories, "articles": articles},
    )


@login_required
@require_POST
def store_article(request):
    """
    Handle article creation by journalists.

    Only accessible to users with journalist role (NOT editors).
    """
    if not request.user.can_create_articles:
        return JsonResponse(
            {
                "success": False,
                "error": "Permission denied. Only journalists can create articles.",
            },
            status=403,
        )

    try:
        data = json.loads(request.body)
        category = get_object_or_404(Category, name=data.get("category"))

        article = Article.objects.create(
            title=data.get("title"),
            category=category,
            author=request.user,
            image=data.get("image", ""),
            content=data.get("content"),
            status="pending",
        )

        if hasattr(request.user, "journalist_profile"):
            request.user.journalist_profile.increment_article_count()

        return JsonResponse({"success": True, "id": article.id})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_POST
def store_newsletter(request):
    """
    Handle newsletter creation by journalists.

    Only accessible to users with journalist role.
    """
    if not request.user.can_create_newsletters:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    try:
        data = json.loads(request.body)

        newsletter = Newsletter.objects.create(
            title=data.get("title"),
            subject=data.get("subject"),
            author=request.user,
            content=data.get("content"),
            status="draft",
        )

        article_ids = data.get("article_ids", [])
        if article_ids:
            articles = Article.objects.filter(id__in=article_ids)
            newsletter.articles.set(articles)

        if hasattr(request.user, "journalist_profile"):
            request.user.journalist_profile.increment_newsletter_count()

        return JsonResponse({"success": True, "id": newsletter.id})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_POST
def update_article(request, article_id):
    """
    Update an existing article.

    Only accessible to the article author.
    """
    article = get_object_or_404(Article, id=article_id)

    if article.author != request.user and not request.user.is_admin_role:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    try:
        data = json.loads(request.body)

        if data.get("title"):
            article.title = data.get("title")
        if data.get("category"):
            article.category = get_object_or_404(Category, name=data.get("category"))
        if data.get("content"):
            article.content = data.get("content")
        if data.get("image"):
            article.image = data.get("image")

        if data.get("status") in ["draft", "pending"]:
            article.status = data.get("status")

        article.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_POST
def submit_article(request, article_id):
    """
    Submit an article for review.

    Only accessible to the article author.
    """
    article = get_object_or_404(Article, id=article_id)

    if article.author != request.user:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    article.status = "pending"
    article.save()
    return JsonResponse({"success": True})


@login_required
@require_POST
def approve_article(request, article_id):
    """
    Approve and publish an article.

    Only accessible to users with editor role.
    Note: Editors cannot create articles, only approve/reject.
    """
    if not request.user.can_review_articles:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    article = get_object_or_404(Article, id=article_id)
    article.status = "published"
    article.reviewed_by = request.user
    article.published_date = timezone.now().date()
    article.save()

    messages.success(request, f'Article "{article.title}" has been published.')
    return JsonResponse({"success": True})


@login_required
@require_POST
def reject_article(request, article_id):
    """
    Reject an article.

    Only accessible to users with editor role.
    """
    if not request.user.can_review_articles:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    article = get_object_or_404(Article, id=article_id)
    data = json.loads(request.body)
    article.status = "rejected"
    article.reviewed_by = request.user
    article.rejection_reason = data.get("reason", "")
    article.save()

    messages.success(request, f'Article "{article.title}" has been rejected.')
    return JsonResponse({"success": True})


def article_detail(request, article_id):
    """
    Display the full article content.

    Accessible to all users for published articles.
    """
    article = get_object_or_404(Article, id=article_id, status="published")
    categories = Category.objects.filter(is_active=True)

    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = request.user.bookmarked_articles.filter(id=article_id).exists()

    return render(
        request,
        "article_detail.html",
        {"article": article, "categories": categories, "is_bookmarked": is_bookmarked},
    )


@login_required
@require_POST
def toggle_bookmark(request, article_id):
    """
    Toggle bookmark status for an article.

    Only accessible to authenticated users.
    """
    article = get_object_or_404(Article, id=article_id)

    if request.user in article.bookmarked_by.all():
        article.bookmarked_by.remove(request.user)
        bookmarked = False
    else:
        article.bookmarked_by.add(request.user)
        bookmarked = True

    return JsonResponse({"bookmarked": bookmarked})


@login_required
@require_POST
def delete_article(request, article_id):
    """
    Delete an article.

    Only accessible to the article author or admin.
    """
    article = get_object_or_404(Article, id=article_id)

    if article.author != request.user and not request.user.is_admin_role:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    if hasattr(article.author, "journalist_profile"):
        article.author.journalist_profile.decrement_article_count()

    article.delete()
    return JsonResponse({"success": True})


@login_required
@require_POST
def delete_newsletter(request, newsletter_id):
    """
    Delete a newsletter.

    Only accessible to the newsletter author or admin.
    """
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if newsletter.author != request.user and not request.user.is_admin_role:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    newsletter.delete()
    return JsonResponse({"success": True})


def api_articles(request):
    """
    API endpoint to retrieve all published articles.

    Returns JSON data containing articles and bookmark information for authenticated users.
    """
    articles = Article.objects.filter(status="published").order_by(
        "-published_date", "-date"
    )

    bookmarks = []
    if request.user.is_authenticated:
        bookmarks = list(request.user.bookmarked_articles.values_list("id", flat=True))

    articles_data = [
        {
            "id": a.id,
            "title": a.title,
            "category_name": a.category.name,
            "author": a.author.username if a.author else "Unknown",
            "author_id": a.author.id if a.author else None,
            "date": (a.published_date or a.date).isoformat(),
            "image": a.image,
            "content": a.content,
        }
        for a in articles
    ]

    return JsonResponse({"articles": articles_data, "bookmarks": bookmarks})


def api_categories(request):
    """
    API endpoint to retrieve all active categories.
    """
    categories = Category.objects.filter(is_active=True)
    data = [
        {"id": c.id, "name": c.name, "description": c.description} for c in categories
    ]
    return JsonResponse({"categories": data})


def api_publishers(request):
    """
    API endpoint to retrieve all publishers.
    """
    publishers = Publisher.objects.all()
    data = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "is_verified": p.is_verified,
            "is_independent": p.is_independent,
        }
        for p in publishers
    ]
    return JsonResponse({"publishers": data})


@login_required
def manage_categories(request):
    """
    Display and manage categories (for editors and admins).
    Only editors and admins can add, edit, or delete categories.
    """
    if not request.user.can_review_articles:
        messages.error(request, "You do not have permission to manage categories.")
        return redirect("home")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()

            if name:
                Category.objects.get_or_create(
                    name=name, defaults={"description": description}
                )
                messages.success(request, f'Category "{name}" created successfully.')

        elif action == "toggle":
            category_id = request.POST.get("category_id")
            category = get_object_or_404(Category, id=category_id)
            category.is_active = not category.is_active
            category.save()
            messages.success(
                request,
                f'Category "{category.name}" {"activated" if category.is_active else "deactivated"}.',
            )

        elif action == "delete":
            category_id = request.POST.get("category_id")
            category = get_object_or_404(Category, id=category_id)
            category_name = category.name
            category.delete()
            messages.success(request, f'Category "{category_name}" deleted.')

        return redirect("manage_categories")

    categories = Category.objects.all().order_by("name")
    return render(request, "manage_categories.html", {"categories": categories})
