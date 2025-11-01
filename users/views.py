from django.shortcuts import render

# Create your views here.
# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

@login_required
def profile(request):
    return render(request, 'users/profile.html')


# users/views.py - Updated profile view
from django.contrib import messages
from complaints.models import Complaint, ComplaintUpdate
from datetime import datetime, timedelta

@login_required
def profile(request):
    user = request.user
    
    # Statistics
    if user.role == 'citizen':
        complaints = Complaint.objects.filter(citizen=user)
    else:
        complaints = Complaint.objects.all()
    
    total_complaints = complaints.count()
    resolved_complaints = complaints.filter(status='resolved').count()
    pending_complaints = complaints.filter(status__in=['pending', 'approved', 'assigned']).count()
    in_progress_complaints = complaints.filter(status='in_progress').count()
    
    # Recent activity
    if user.role == 'citizen':
        recent_complaints = Complaint.objects.filter(citizen=user).order_by('-created_at')[:10]
    else:
        recent_complaints = Complaint.objects.all().order_by('-created_at')[:10]
    
    # Recent updates
    recent_updates = ComplaintUpdate.objects.all().order_by('-created_at')[:10]
    
    # Assigned complaints for authorities/admins
    if user.role != 'citizen':
        assigned_complaints_list = Complaint.objects.filter(
            assigned_authority=user
        ).order_by('-created_at')[:10]
    else:
        assigned_complaints_list = []
    
    # Handle profile updates
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone_number = request.POST.get('phone_number', '')
        user.address = request.POST.get('address', '')
        
        if user.role == 'authority':
            user.department = request.POST.get('department', '')
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            # In a real implementation, you'd want to resize and validate the image
            user.profile.avatar = request.FILES['avatar']
            user.profile.save()
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'recent_complaints': recent_complaints,
        'recent_updates': recent_updates,
        'assigned_complaints_list': assigned_complaints_list,
    }
    
    # Add assigned count for authorities
    if user.role == 'authority':
        context['assigned_complaints'] = Complaint.objects.filter(
            assigned_authority=user
        ).exclude(status__in=['resolved', 'rejected']).count()
    
    return render(request, 'users/profile.html', context)



# users/views.py - Custom logout view with statistics
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from complaints.models import Complaint

# users/views.py - Simplified logout view
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    
    # Simple context without complex statistics
    context = {
        'user_stats': {
            'total_complaints': 0,
            'resolved_complaints': 0,
        },
        'session_duration': 'Unknown'
    }
    
    return render(request, 'registration/logout.html', context)


# users/views.py - Updated register view
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

# users/forms.py - Updated form
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    department = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 
                 'role', 'phone_number', 'address', 'department')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make role field not required in form, we'll handle it via hidden input
        self.fields['role'].required = False
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        user.department = self.cleaned_data['department']
        
        # Get role from form data
        role = self.data.get('role', 'citizen')
        user.role = role
        
        if commit:
            user.save()
        return user
    
# complaints/views.py or users/views.py
from django.contrib.auth.views import LoginView
from django.contrib import messages

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        if user.role == 'citizen':
            messages.success(self.request, 'Citizen should successfully log in and access the home page.')
        elif user.role == 'authority':
            messages.success(self.request, 'Authority should successfully log in and access the dashboard.')
        elif user.role == 'admin':
            messages.success(self.request, 'Admin should successfully log in and access the admin dashboard.')
        return response