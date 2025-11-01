# complaints/management/commands/load_sample_data.py
from django.core.management.base import BaseCommand
from complaints.models import Category
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Load sample data for Clean My City'

    def handle(self, *args, **options):
        # Create sample categories
        categories = [
            ('Garbage Accumulation', 'Improper waste disposal and garbage accumulation'),
            ('Drainage Issues', 'Blocked or clogged drainage systems'),
            ('Public Hygiene', 'Unclean public spaces and sanitation issues'),
            ('Street Cleaning', 'Poor street cleaning and maintenance'),
            ('Waste Collection', 'Irregular or missed waste collection'),
        ]
        
        for name, description in categories:
            Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded sample categories')
        )
        
        # Create admin user if not exists
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@cleanmycity.com',
                password='admin123',
                role='admin'
            )
            self.stdout.write(
                self.style.SUCCESS('Created admin user: admin/admin123')
            )