# complaints/fields.py
from django.db import models

class SimpleLocationField(models.CharField):
    """A simple char field to store latitude,longitude as string"""
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 100
        kwargs['blank'] = True
        kwargs['null'] = True
        super().__init__(*args, **kwargs)
    
    def get_coordinates(self, value):
        """Extract lat,lon from string 'lat,lon'"""
        if value and ',' in value:
            try:
                lat, lon = value.split(',')
                return float(lat.strip()), float(lon.strip())
            except (ValueError, TypeError):
                return None, None
        return None, None
    
    def set_coordinates(self, lat, lon):
        """Store lat,lon as string"""
        if lat is not None and lon is not None:
            return f"{lat},{lon}"
        return None