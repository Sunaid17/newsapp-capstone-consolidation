"""
Management command to set up Django groups and assign users based on their role.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from articles.models import CustomUser


class Command(BaseCommand):
    help = "Set up Django groups and assign users"

    def handle(self, *args, **options):
        readers_group, _ = Group.objects.get_or_create(name="Readers")
        journalists_group, _ = Group.objects.get_or_create(name="Journalists")
        editors_group, _ = Group.objects.get_or_create(name="Editors")

        self.stdout.write(
            self.style.SUCCESS("Created groups: Readers, Journalists, Editors")
        )

        for user in CustomUser.objects.all():
            user.groups.clear()
            if user.role == "reader":
                user.groups.add(readers_group)
            elif user.role == "journalist":
                user.groups.add(journalists_group)
            elif user.role == "editor":
                user.groups.add(editors_group)
            self.stdout.write(f"Added {user.username} to {user.role} group")

        self.stdout.write(
            self.style.SUCCESS("Successfully set up groups and assigned users")
        )
