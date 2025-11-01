# complaints/management/commands/add_sample_locations.py
from django.core.management.base import BaseCommand
from complaints.models import Complaint
import random

class Command(BaseCommand):
    help = 'Add sample location data to complaints'

    def handle(self, *args, **options):
        # Bangalore coordinates range
        bangalore_lat_range = (12.85, 13.15)
        bangalore_lon_range = (77.45, 77.75)
        
        complaints = Complaint.objects.filter(latitude__isnull=True)
        
        for complaint in complaints:
            # Generate random coordinates within Bangalore
            lat = random.uniform(*bangalore_lat_range)
            lon = random.uniform(*bangalore_lon_range)
            
            complaint.latitude = lat
            complaint.longitude = lon
            complaint.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Added location to complaint: {complaint.title}')
            )