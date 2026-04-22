"""
Management command to seed the database with sample data.
Creates users with different roles: reader, journalist, and editor.
"""

from django.core.management.base import BaseCommand
from articles.models import Article, Category, CustomUser, Journalist, Editor, Publisher


class Command(BaseCommand):
    """Seeds the database with sample categories, users, and articles."""

    help = "Seeds the database with sample data"

    def handle(self, *args, **options):
        # Create categories
        categories_data = [
            "politics",
            "technology",
            "sports",
            "entertainment",
            "business",
            "health",
            "science",
        ]
        for cat_name in categories_data:
            Category.objects.get_or_create(name=cat_name)
        self.stdout.write(self.style.SUCCESS("Created categories"))

        # Create Publishers
        pub1, _ = Publisher.objects.get_or_create(
            name="Tech News Daily",
            defaults={
                "description": "Leading technology news publication",
                "is_verified": True,
            },
        )
        pub2, _ = Publisher.objects.get_or_create(
            name="Sports Weekly",
            defaults={"description": "Sports news and updates", "is_verified": True},
        )
        pub_independent, _ = Publisher.objects.get_or_create(
            name="Independent News",
            defaults={"description": "Independent journalism", "is_independent": True},
        )
        self.stdout.write(self.style.SUCCESS("Created publishers"))

        # Create Reader
        if not CustomUser.objects.filter(username="reader1").exists():
            reader = CustomUser.objects.create_user(
                username="reader1",
                email="reader1@newsapp.com",
                password="password123",
                role="reader",
            )
            self.stdout.write(self.style.SUCCESS(f"Created reader: {reader.username}"))

        # Create Journalists
        if not CustomUser.objects.filter(username="journalist1").exists():
            journalist1 = CustomUser.objects.create_user(
                username="journalist1",
                email="journalist1@newsapp.com",
                password="password123",
                role="journalist",
                publisher=pub1,
            )
            Journalist.objects.create(
                user=journalist1,
                specialization="Technology",
                organization=pub1,
                is_verified=True,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Created journalist: {journalist1.username}")
            )

        if not CustomUser.objects.filter(username="journalist2").exists():
            journalist2 = CustomUser.objects.create_user(
                username="journalist2",
                email="journalist2@newsapp.com",
                password="password123",
                role="journalist",
                publisher=pub2,
            )
            Journalist.objects.create(
                user=journalist2,
                specialization="Sports",
                organization=pub2,
                is_verified=True,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Created journalist: {journalist2.username}")
            )

        # Create Editor
        if not CustomUser.objects.filter(username="editor1").exists():
            editor = CustomUser.objects.create_user(
                username="editor1",
                email="editor1@newsapp.com",
                password="password123",
                role="editor",
            )
            Editor.objects.create(user=editor, department="News", is_chief_editor=True)
            self.stdout.write(self.style.SUCCESS(f"Created editor: {editor.username}"))

        journalist1_user = CustomUser.objects.get(username="journalist1")
        journalist1_profile = journalist1_user.journalist_profile

        # Create published articles
        articles_data = [
            {
                "title": "Global Climate Summit Reaches Historic Agreement on Emissions",
                "category": "politics",
                "content": "In a historic moment for climate action, representatives from over 190 countries have signed the Vienna Climate Accord, committing to aggressive new targets for reducing greenhouse gas emissions. The agreement sets a goal of cutting global emissions by 50% by 2035.\n\nEnvironmental groups have largely praised the agreement, though some activists argue the targets don't go far enough.",
                "image": "https://images.unsplash.com/photo-1569163139394-de4e5f43e5ca?w=800",
            },
            {
                "title": "Revolutionary AI System Passes Medical Licensing Exam",
                "category": "technology",
                "content": "MedAI, a cutting-edge artificial intelligence system, has achieved a passing score on the comprehensive medical licensing examination, becoming the first AI to accomplish this feat.\n\nHealthcare experts believe this development could revolutionize medical diagnosis and treatment planning.",
                "image": "https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=800",
            },
            {
                "title": "Underdog Team Wins Championship in Stunning Upset",
                "category": "sports",
                "content": "In one of the most surprising finishes in sports history, the underdog Riverside Eagles defeated the reigning champions 3-2 in what commentators are calling the greatest championship game ever played.\n\nThe victory has sparked celebrations across the city.",
                "image": "https://images.unsplash.com/photo-1461896836934-5d3d191fa87c?w=800",
            },
            {
                "title": "Award-Winning Director Announces Ambitious New Film Project",
                "category": "entertainment",
                "content": "Acclaimed director has announced his most ambitious project yet: a sweeping historical epic that will trace the story of a single family across 300 years of human history.\n\nThe project has already generated significant awards buzz.",
                "image": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=800",
            },
            {
                "title": "Tech Giants Report Record Quarterly Earnings Amid AI Boom",
                "category": "business",
                "content": "Major technology companies have reported record-breaking quarterly earnings, with AI-powered products and services fueling growth.\n\nEvery business wants to integrate AI, and companies are delivering the tools they need.",
                "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
            },
            {
                "title": "New Study Reveals Promising Results for Alzheimer's Treatment",
                "category": "health",
                "content": "A groundbreaking clinical trial has shown that an experimental treatment can significantly slow cognitive decline in patients with early-stage Alzheimer's disease.\n\nThis is the most significant advancement in Alzheimer's treatment in decades.",
                "image": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=800",
            },
            {
                "title": "Astronomers Discover New Earth-Sized Planet in Habitable Zone",
                "category": "science",
                "content": "Astronomers have made a potentially groundbreaking discovery: an Earth-sized planet orbiting within the habitable zone of a nearby star.\n\nThe planet could have liquid water on its surface, located just 40 light-years from Earth.",
                "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800",
            },
            {
                "title": "International Space Station Marks 30 Years of Continuous Human Presence",
                "category": "science",
                "content": "The International Space Station reached a remarkable milestone: 30 years of continuous human presence in low Earth orbit.\n\nThe station has hosted over 250 visitors from 19 countries and served as a laboratory for more than 3,000 scientific experiments.",
                "image": "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=800",
            },
        ]

        for article_data in articles_data:
            category = Category.objects.get(name=article_data["category"])
            _, created = Article.objects.get_or_create(
                title=article_data["title"],
                defaults={
                    "category": category,
                    "author": journalist1_user,
                    "content": article_data["content"],
                    "image": article_data["image"],
                    "status": "published",
                },
            )
            if created:
                journalist1_profile.increment_article_count()

        # Create pending article
        journalist2_user = CustomUser.objects.get(username="journalist2")
        if not Article.objects.filter(
            title="Breaking: Major Technology Announcement Expected"
        ).exists():
            Article.objects.create(
                title="Breaking: Major Technology Announcement Expected",
                category=Category.objects.get(name="technology"),
                author=journalist2_user,
                content="Industry experts are anticipating a major announcement from leading tech companies regarding breakthrough developments in artificial intelligence and quantum computing. The announcement is expected to reshape the technology landscape for years to come.\n\nStay tuned for more updates as this story develops.",
                image="https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
                status="pending",
            )
            self.stdout.write(
                self.style.WARNING("Created pending article for editorial review")
            )

        self.stdout.write(self.style.SUCCESS("\nSuccessfully seeded database!"))
        self.stdout.write(self.style.SUCCESS("\nTest Accounts:"))
        self.stdout.write("  Reader:     reader1 / password123")
        self.stdout.write("  Journalist: journalist1 / password123")
        self.stdout.write("  Journalist: journalist2 / password123")
        self.stdout.write("  Editor:     editor1 / password123")
