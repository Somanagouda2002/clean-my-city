from django.shortcuts import render

# # Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth import authenticate, login

# from datetime import timedelta
# from .models import Complaint, Category, ComplaintUpdate, Feedback
from .forms import ComplaintForm, ComplaintUpdateForm, FeedbackForm
# from django.db.models import Count, Avg


# complaints/views.py
# complaints/views.py
def home(request):
    # Check if user is logged in and show message
    if request.user.is_authenticated and request.user.role == 'citizen':
        messages.success(request, 'Citizen should successfully log in and access the home page.')
    
    return render(request, 'complaints/home.html')


# # complaints/views.py - Updated create_complaint view
# import base64
# from django.core.files.base import ContentFile




# # complaints/views.py - Updated complaint_list view
# from django.core.paginator import Paginator




# from django.db.models import Q
# import math
# from .models import Complaint, ComplaintUpdate
# from .forms import ComplaintUpdateForm

# def calculate_distance(lat1, lon1, lat2, lon2):
#     """
#     Calculate distance between two points using Haversine formula
#     """
#     # Convert coordinates to radians
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
#     # Haversine formula
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
#     c = 2 * math.asin(math.sqrt(a))
#     r = 6371  # Radius of earth in kilometers
    
#     return c * r



@login_required
def authority_complaint_list(request):
    """List view specifically for authorities with filtering"""
    if request.user.role != 'authority':
        return redirect('complaint_list')
    
    status_filter = request.GET.get('status', '')
    urgency_filter = request.GET.get('urgency', '')
    
    # Start with complaints assigned to this authority
    complaints = Complaint.objects.filter(assigned_authority=request.user)
    
    # Apply filters
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if urgency_filter:
        complaints = complaints.filter(urgency=urgency_filter)
    
    # Order by urgency and creation date
    complaints = complaints.order_by('-urgency', '-created_at')
    
    context = {
        'complaints': complaints,
        'current_status': status_filter,
        'current_urgency': urgency_filter,
    }
    
    return render(request, 'complaints/authority_complaint_list.html', context)






# # complaints/views.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.utils import timezone
# from django.db.models import Q
# import math
# from .models import Complaint, ComplaintUpdate
# from .forms import ComplaintUpdateForm

# def simple_distance(lat1, lon1, lat2, lon2):
#     """
#     Simple distance calculation using Pythagorean theorem
#     Good enough for small distances within a city
#     Returns approximate distance in kilometers
#     """
#     # Convert latitude and longitude differences to kilometers
#     # 1 degree latitude ≈ 111 km, 1 degree longitude ≈ 111 km * cos(latitude)
#     lat_km = abs(lat1 - lat2) * 111
#     lon_km = abs(lon1 - lon2) * 111 * math.cos(math.radians((lat1 + lat2) / 2))
    
#     # Pythagorean theorem
#     distance = math.sqrt(lat_km**2 + lon_km**2)
#     return distance

# # complaints/views.py

# from django.db.models import Q
# from .models import Complaint, ComplaintUpdate
# from .forms import ComplaintUpdateForm
# from .utils import safe_distance, get_nearby_complaints_safe



@login_required
def update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check permissions
    if request.user.role not in ['authority', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    # Auto-assign if not assigned and user is authority
    if request.user.role == 'authority' and not complaint.assigned_authority:
        complaint.assigned_authority = request.user
        complaint.status = 'assigned'
        complaint.save()
        messages.info(request, 'Complaint has been assigned to you.')
    
    # Check if authority owns this complaint
    if request.user.role == 'authority' and complaint.assigned_authority != request.user:
        messages.error(request, 'This complaint is assigned to another authority.')
        return redirect('authority_dashboard')
    
    if request.method == 'POST':
        form = ComplaintUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.complaint = complaint
            update.authority = request.user
            
            new_status = form.cleaned_data['status']
            
            # Update complaint status
            complaint.status = new_status
            
            # Validate proof for resolution
            if new_status == 'resolved' and not request.FILES.get('proof_image'):
                messages.error(request, 'Proof image is required when marking complaint as resolved.')
                return render(request, 'complaints/update_complaint_status.html', {
                    'form': form,
                    'complaint': complaint
                })
            
            complaint.save()
            update.save()
            
            messages.success(request, f'Complaint status updated to {complaint.get_status_display()}!')
            return redirect('complaint_detail', complaint_id=complaint.id)
    else:
        form = ComplaintUpdateForm(initial={'status': complaint.status})
    
    return render(request, 'complaints/update_complaint_status.html', {
        'form': form,
        'complaint': complaint
    })


# # complaints/views.py - Add this temporary view
# def test_distance(request):
#     """Test view to verify distance calculation works"""
#     from django.http import JsonResponse
    
#     # Test coordinates
#     user_lat, user_lon = 12.9716, 77.5946  # Bangalore center
#     test_lat, test_lon = 12.9756, 77.5996  # Nearby point
    
#     distance = simple_distance(user_lat, user_lon, test_lat, test_lon)
    
#     return JsonResponse({
#         'user_location': [user_lat, user_lon],
#         'test_location': [test_lat, test_lon],
#         'distance_km': round(distance, 2),
#         'status': 'success'
#     })




















from .models import Complaint, ComplaintUpdate, Category
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

@login_required
def dashboard(request):
    user = request.user
    
    # Debug print
    print(f"USER ROLE: {getattr(user, 'role', 'NO ROLE')}")
    print(f"Is staff: {user.is_staff}, Is superuser: {user.is_superuser}")
    
    # If user is staff/superuser but role is not set, treat as admin
    if user.is_superuser or user.is_staff:
        if hasattr(user, 'role') and user.role != 'admin':
            # Update the role to admin
            user.role = 'admin'
            user.save()
        return redirect('admin_dashboard')
    
    # Normal role-based routing
    if hasattr(user, 'role'):
        if user.role == 'admin':
            return redirect('admin_dashboard')
        elif user.role == 'authority':
            return redirect('authority_dashboard')
        elif user.role == 'citizen':
            # Your citizen dashboard code here
            complaints = Complaint.objects.filter(citizen=user).order_by('-created_at')
            recent_complaints = complaints[:10]
            
            recent_updates = ComplaintUpdate.objects.filter(
                complaint__citizen=user
            ).select_related('complaint').order_by('-created_at')[:5]
            
            context = {
                'complaints': recent_complaints,
                'recent_updates': recent_updates,
                'total_complaints': complaints.count(),
                'resolved_complaints': complaints.filter(status='resolved').count(),
                'pending_complaints': complaints.filter(status__in=['pending', 'approved', 'assigned']).count(),
            }
            return render(request, 'complaints/dashboard.html', context)
    
    # Default fallback
    messages.error(request, 'Unable to determine user role.')
    return render(request, 'complaints/dashboard.html')

@login_required
def authority_dashboard(request):
    if request.user.role != 'authority':
        messages.error(request, 'Access denied. Authority role required.')
        return redirect('dashboard')
    
    # Default coordinates
    user_lat = 12.9716
    user_lon = 77.5946
    
    # Get base queryset first
    complaints_qs = Complaint.objects.filter(
        Q(assigned_authority=request.user) | 
        Q(assigned_authority__isnull=True)
    ).filter(
        status__in=['pending', 'approved', 'assigned', 'in_progress']
    ).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    # Add distance information and filter
    nearby_complaints = []
    for complaint in complaints_qs:
        try:
            comp_lat = complaint.get_lat_float()
            comp_lon = complaint.get_lon_float()
            if comp_lat and comp_lon:
                distance = safe_distance(user_lat, user_lon, comp_lat, comp_lon)
                
                if distance and distance <= 20:
                    complaint.distance = distance
                    nearby_complaints.append(complaint)
        except (ValueError, TypeError, AttributeError):
            continue
    
    # Sort and limit for display
    nearby_complaints.sort(key=lambda x: (
        x.urgency in ['critical', 'high'],
        x.distance if hasattr(x, 'distance') else 100,
        -x.created_at.timestamp()
    ))
    
    display_complaints = nearby_complaints[:20]  # Limit for display
    
    # Statistics using full querysets
    stats = {
        'assigned_complaints': Complaint.objects.filter(
            assigned_authority=request.user
        ).exclude(status__in=['resolved', 'rejected']).count(),
        'in_progress_complaints': Complaint.objects.filter(
            assigned_authority=request.user,
            status='in_progress'
        ).count(),
        'resolved_today': Complaint.objects.filter(
            assigned_authority=request.user,
            status='resolved',
            updated_at__date=timezone.now().date()
        ).count(),
        'urgent_complaints': Complaint.objects.filter(
            Q(assigned_authority=request.user) | Q(assigned_authority__isnull=True),
            urgency__in=['high', 'critical'],
            status__in=['pending', 'approved', 'assigned']
        ).count(),
    }
    
    context = {
        'assigned_complaints': display_complaints,
        'stats': stats,
    }
    
    return render(request, 'complaints/authority_dashboard.html', context)

@login_required
def complaint_list(request):
    # Get base queryset first
    if request.user.role == 'citizen':
        complaints_qs = Complaint.objects.filter(citizen=request.user)
    else:
        complaints_qs = Complaint.objects.all()
    
    # Apply filters to the base queryset
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    urgency_filter = request.GET.get('urgency', '')
    date_range = request.GET.get('date_range', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        complaints_qs = complaints_qs.filter(status=status_filter)
    if category_filter:
        complaints_qs = complaints_qs.filter(category_id=category_filter)
    if urgency_filter:
        complaints_qs = complaints_qs.filter(urgency=urgency_filter)
    if search_query:
        complaints_qs = complaints_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Date range filter
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            complaints_qs = complaints_qs.filter(created_at__date=today)
        elif date_range == 'week':
            week_ago = today - timezone.timedelta(days=7)
            complaints_qs = complaints_qs.filter(created_at__date__gte=week_ago)
        elif date_range == 'month':
            month_ago = today - timezone.timedelta(days=30)
            complaints_qs = complaints_qs.filter(created_at__date__gte=month_ago)
    
    # Apply sorting
    sort_field = request.GET.get('sort', '-created_at')
    sort_direction = request.GET.get('order', 'desc')
    
    if sort_field:
        if sort_direction == 'desc' and not sort_field.startswith('-'):
            sort_field = '-' + sort_field
        complaints_qs = complaints_qs.order_by(sort_field)
    
    # Pagination - slice only for pagination
    from django.core.paginator import Paginator
    paginator = Paginator(complaints_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics using the filtered queryset (before pagination)
    total_complaints = complaints_qs.count()
    resolved_complaints = complaints_qs.filter(status='resolved').count()
    pending_complaints = complaints_qs.filter(status__in=['pending', 'approved', 'assigned']).count()
    in_progress_complaints = complaints_qs.filter(status='in_progress').count()
    
    context = {
        'complaints': page_obj,
        'categories': Category.objects.all(),
        'status_choices': Complaint.STATUS_CHOICES,
        'urgency_choices': Complaint.URGENCY_CHOICES,
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'current_status': status_filter,
        'current_category': category_filter,
        'current_urgency': urgency_filter,
        'current_date_range': date_range,
        'search_query': search_query,
        'sort_field': sort_field.lstrip('-'),
        'sort_direction': sort_direction,
    }
    
    return render(request, 'complaints/complaint_list.html', context)

# Other views remain the same...
@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.citizen = request.user
            
            # Handle photo data from webcam if needed
            photo_data = request.POST.get('photo_data')
            if photo_data:
                from django.core.files.base import ContentFile
                import base64
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'complaint_{timezone.now().timestamp()}.{ext}')
                complaint.photo = data
            
            complaint.save()
            messages.success(request, 'Complaint submitted successfully!')
            return redirect('complaint_detail', complaint_id=complaint.id)
    else:
        form = ComplaintForm()
    
    return render(request, 'complaints/create_complaint.html', {'form': form})

@login_required
def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    updates = complaint.updates.all().order_by('-created_at')
    feedback = getattr(complaint, 'feedback', None)
    
    # Check permissions
    if request.user.role == 'citizen' and complaint.citizen != request.user:
        messages.error(request, 'You do not have permission to view this complaint.')
        return redirect('dashboard')
    
    context = {
        'complaint': complaint,
        'updates': updates,
        'feedback': feedback,
    }
    return render(request, 'complaints/complaint_detail.html', context)

@login_required
def update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.user.role not in ['authority', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    if request.user.role == 'authority' and complaint.assigned_authority != request.user:
        if not complaint.assigned_authority:
            complaint.assigned_authority = request.user
            complaint.status = 'assigned'
            complaint.save()
            messages.info(request, 'Complaint assigned to you.')
        else:
            messages.error(request, 'This complaint is assigned to another authority.')
            return redirect('authority_dashboard')
    
    if request.method == 'POST':
        form = ComplaintUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.complaint = complaint
            update.authority = request.user
            
            new_status = form.cleaned_data['status']
            complaint.status = new_status
            
            if new_status == 'resolved' and not request.FILES.get('proof_image'):
                messages.error(request, 'Proof image is required when marking as resolved.')
                return render(request, 'complaints/update_complaint_status.html', {
                    'form': form,
                    'complaint': complaint
                })
            
            complaint.save()
            update.save()
            
            messages.success(request, f'Status updated to {complaint.get_status_display()}!')
            return redirect('complaint_detail', complaint_id=complaint.id)
    else:
        form = ComplaintUpdateForm(initial={'status': complaint.status})
    
    return render(request, 'complaints/update_complaint_status.html', {
        'form': form,
        'complaint': complaint
    })

@login_required
def submit_feedback(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if complaint.citizen != request.user:
        messages.error(request, 'You can only provide feedback for your own complaints.')
        return redirect('dashboard')
    
    if complaint.status != 'resolved':
        messages.error(request, 'You can only provide feedback for resolved complaints.')
        return redirect('complaint_detail', complaint_id=complaint.id)
    
    if hasattr(complaint, 'feedback'):
        messages.error(request, 'Feedback already submitted.')
        return redirect('complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.complaint = complaint
            feedback.citizen = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('complaint_detail', complaint_id=complaint.id)
    else:
        form = FeedbackForm()
    
    return render(request, 'complaints/submit_feedback.html', {
        'form': form,
        'complaint': complaint
    })

@login_required
def generate_reports(request):
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can access reports.')
        return redirect('dashboard')
    
    # Basic analytics
    complaints_by_status = Complaint.objects.values('status').annotate(count=Count('id')).order_by('status')
    complaints_by_category = Complaint.objects.values('category__name').annotate(count=Count('id')).order_by('-count')
    complaints_by_urgency = Complaint.objects.values('urgency').annotate(count=Count('id')).order_by('urgency')
    
    context = {
        'complaints_by_status': complaints_by_status,
        'complaints_by_category': complaints_by_category,
        'complaints_by_urgency': complaints_by_urgency,
    }
    return render(request, 'complaints/reports.html', context)

# complaints/views.py - Add these admin views
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

User = get_user_model()

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin role required.')
        return redirect('dashboard')
    
    # Statistics
    stats = {
        'total_users': User.objects.count(),
        'total_complaints': Complaint.objects.count(),
        'resolved_complaints': Complaint.objects.filter(status='resolved').count(),
        'pending_complaints': Complaint.objects.filter(status='pending').count(),
        'citizen_users': User.objects.filter(role='citizen').count(),
        'authority_users': User.objects.filter(role='authority').count(),
    }
    
    # Recent activity
    recent_activity = ComplaintUpdate.objects.select_related(
        'complaint', 'authority'
    ).order_by('-created_at')[:10]
    
    # Urgent complaints
    urgent_complaints = Complaint.objects.filter(
        urgency__in=['high', 'critical'],
        status__in=['pending', 'approved', 'assigned']
    )[:5]
    
    context = {
        'stats': stats,
        'recent_activity': recent_activity,
        'urgent_complaints': urgent_complaints,
    }
    
    return render(request, 'complaints/admin_dashboard.html', context)

@login_required
def admin_user_management(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get filter parameters
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    users = User.objects.all()
    
    # Apply filters
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Statistics
    stats = {
        'total_users': User.objects.count(),
        'citizen_users': User.objects.filter(role='citizen').count(),
        'authority_users': User.objects.filter(role='authority').count(),
        'active_users': User.objects.filter(is_active=True).count(),
    }
    
    context = {
        'users': users,
        'stats': stats,
        'current_role': role_filter,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'complaints/admin_user_management.html', context)

# complaints/views.py - Update the admin user management views
from .forms import CustomUserCreationForm, UserEditForm

@login_required
def admin_create_user(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('admin_user_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'complaints/admin_create_user.html', {'form': form})

@login_required
def admin_edit_user(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('admin_user_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'complaints/admin_edit_user.html', {'form': form, 'user': user})

@login_required
def admin_toggle_user(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        action = "activated" if user.is_active else "deactivated"
        messages.success(request, f'User {user.username} has been {action}.')
    
    return redirect('admin_user_management')

@login_required
def admin_location_management(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get unique locations with complaint counts
    locations_data = []
    complaints_with_location = Complaint.objects.exclude(
        Q(latitude__isnull=True) | Q(longitude__isnull=True) | Q(location__isnull=True)
    )
    
    # Group by location and get statistics
    location_groups = {}
    for complaint in complaints_with_location:
        location_key = complaint.location.strip().lower()
        if location_key not in location_groups:
            location_groups[location_key] = {
                'area': complaint.location,
                'complaint_count': 0,
                'latitude': complaint.get_lat_float(),
                'longitude': complaint.get_lon_float(),
                'latest_complaint': complaint.title
            }
        location_groups[location_key]['complaint_count'] += 1
        
        # Keep the most recent complaint title
        if complaint.created_at > Complaint.objects.filter(location=complaint.location).latest('created_at').created_at:
            location_groups[location_key]['latest_complaint'] = complaint.title
    
    locations = list(location_groups.values())
    
    # Statistics
    stats = {
        'locations_with_data': len(locations),
        'most_active_area': max(locations, key=lambda x: x['complaint_count'])['area'] if locations else 'None',
        'avg_complaints_per_location': round(sum(loc['complaint_count'] for loc in locations) / len(locations) if locations else 0, 1),
    }
    
    context = {
        'locations': locations,
        'stats': stats,
    }
    
    return render(request, 'complaints/admin_location_management.html', context)

@login_required
def advanced_reports(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get filter parameters
    date_range = request.GET.get('date_range', '7days')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    authority_filter = request.GET.get('authority', '')
    
    # Base queryset with date filtering
    complaints = Complaint.objects.all()
    
    # Date range filtering
    if date_range == '7days':
        start_date = timezone.now() - timedelta(days=7)
    elif date_range == '30days':
        start_date = timezone.now() - timedelta(days=30)
    elif date_range == '90days':
        start_date = timezone.now() - timedelta(days=90)
    elif date_range == '1year':
        start_date = timezone.now() - timedelta(days=365)
    else:
        start_date = None
    
    if start_date:
        complaints = complaints.filter(created_at__gte=start_date)
    
    if category_filter:
        complaints = complaints.filter(category_id=category_filter)
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if authority_filter:
        complaints = complaints.filter(assigned_authority_id=authority_filter)
    
    # Overview statistics
    overview = {
        'total_complaints': complaints.count(),
        'resolved_complaints': complaints.filter(status='resolved').count(),
        'urgent_complaints': complaints.filter(urgency__in=['high', 'critical']).count(),
    }
    
    # User statistics
    user_stats = {
        'active_users': User.objects.filter(is_active=True).count(),
        'new_users': User.objects.filter(date_joined__gte=timezone.now()-timedelta(days=30)).count(),
        'avg_resolution_time': 2.5,  # Simplified - in real app, calculate from actual data
    }
    
    # Category statistics
    category_stats = Category.objects.annotate(
        count=Count('complaint')
    ).order_by('-count')
    
    # Authority performance (simplified)
    authority_performance = []
    authorities = User.objects.filter(role='authority')
    
    for authority in authorities:
        assigned_complaints = Complaint.objects.filter(assigned_authority=authority)
        assigned_count = assigned_complaints.count()
        resolved_count = assigned_complaints.filter(status='resolved').count()
        in_progress_count = assigned_complaints.filter(status='in_progress').count()
        
        if assigned_count > 0:
            success_rate = round((resolved_count / assigned_count) * 100)
        else:
            success_rate = 0
        
        authority_performance.append({
            'authority__username': authority.username,
            'assigned': assigned_count,
            'resolved': resolved_count,
            'in_progress': in_progress_count,
            'avg_time': 1.5,  # Simplified
            'success_rate': success_rate
        })
    
    context = {
        'overview': overview,
        'user_stats': user_stats,
        'category_stats': category_stats,
        'authority_performance': authority_performance,
        'categories': Category.objects.all(),
        'status_choices': Complaint.STATUS_CHOICES,
        'authorities': User.objects.filter(role='authority'),
    }
    
    return render(request, 'complaints/advanced_reports.html', context)




# Add this to your views.py
@login_required
def debug_role(request):
    user = request.user
    return render(request, 'complaints/debug_role.html', {
        'username': user.username,
        'role': getattr(user, 'role', 'NO ROLE ATTRIBUTE'),
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'all_attributes': dir(user)
    })










# class CustomLoginView(LoginView):
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         user = self.request.user
#         if user.role == 'citizen':
#             messages.success(self.request, 'Citizen should successfully log in and access the home page.')
#         elif user.role == 'authority':
#             messages.success(self.request, 'Authority should successfully log in and access the dashboard.')
#         elif user.role == 'admin':
#             messages.success(self.request, 'Admin should successfully log in and access the admin dashboard.')
#         return response