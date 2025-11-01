# users/management/commands/fix_admin_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix admin user roles'

    def handle(self, *args, **options):
        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)
        
        for user in superusers:
            if user.role != 'admin':
                user.role = 'admin'
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {user.username} role to admin')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'{user.username} already has admin role')
                )