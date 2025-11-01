# complaints/utils.py
import math

def safe_distance(lat1, lon1, lat2, lon2):
    """
    Safe distance calculation that handles None values and errors
    """
    if None in [lat1, lon1, lat2, lon2]:
        return None
    
    try:
        # Convert to floats
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
        
        # Simple distance calculation (good for city distances)
        lat_km = abs(lat1 - lat2) * 111
        lon_km = abs(lon1 - lon2) * 111 * math.cos(math.radians((lat1 + lat2) / 2))
        
        distance = math.sqrt(lat_km**2 + lon_km**2)
        return round(distance, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def get_nearby_complaints_safe(user_lat, user_lon, max_distance_km=20):
    """
    Safely get nearby complaints without geospatial dependencies
    """
    from .models import Complaint
    
    complaints = Complaint.objects.filter(
        status__in=['pending', 'approved', 'assigned', 'in_progress']
    ).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    nearby_complaints = []
    for complaint in complaints:
        comp_lat = complaint.get_lat_float()
        comp_lon = complaint.get_lon_float()
        
        if comp_lat is not None and comp_lon is not None:
            distance = safe_distance(user_lat, user_lon, comp_lat, comp_lon)
            
            if distance is not None and distance <= max_distance_km:
                complaint.distance = distance
                nearby_complaints.append(complaint)
    
    # Sort by urgency and distance
    nearby_complaints.sort(key=lambda x: (
        x.urgency in ['critical', 'high'],  # Urgent first
        x.distance if hasattr(x, 'distance') else 100,  # Then by distance
    ))
    
    return nearby_complaints