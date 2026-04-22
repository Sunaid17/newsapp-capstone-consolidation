"""
Authentication views for user registration, login, and logout.

Supports registration with role selection:
- Reader: Can browse and bookmark articles
- Journalist: Can create and manage articles
- Editor: Can review and approve articles
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def register(request):
    """
    Handle user registration with role selection.

    Allows users to register as:
    - 'reader': Can browse and bookmark articles
    - 'journalist': Can create and submit articles for review
    - 'editor': Can review and approve articles
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role", "reader")
        specialization = request.POST.get("specialization", "")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "register.html")

        from articles.models import CustomUser, Journalist, Editor

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "register.html")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register.html")

        user = CustomUser.objects.create_user(
            username=username, email=email, password=password1, role=role
        )

        if role == "journalist":
            Journalist.objects.create(user=user, specialization=specialization)
            messages.success(
                request, f"Welcome, {username}! You are now registered as a Journalist."
            )
        elif role == "editor":
            Editor.objects.create(user=user)
            messages.success(
                request, f"Welcome, {username}! You are now registered as an Editor."
            )
        else:
            messages.success(
                request, f"Welcome, {username}! Your account has been created."
            )

        login(request, user)
        return redirect("home")

    return render(request, "register.html")


@csrf_protect
def user_login(request):
    """
    Handle user authentication and login.

    Authenticates user and logs them in with their appropriate role.
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            role_display = user.get_role_display()
            messages.success(
                request,
                f"Welcome back, {username}! You are logged in as {role_display}.",
            )
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "login.html", {"username": username})

    return render(request, "login.html")


def user_logout(request):
    """
    Handle user logout and redirect to home page.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("home")


@login_required
def profile(request):
    """
    Display user profile information.
    """
    return render(request, "profile.html", {"user": request.user})
