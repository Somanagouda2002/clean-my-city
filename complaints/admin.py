from django.contrib import admin

# Register your models here.
# complaints/admin.py
from django.contrib import admin
from .models import Category, Complaint, ComplaintUpdate, Feedback

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'citizen', 'category', 'urgency', 'status', 'created_at')
    list_filter = ('status', 'urgency', 'category', 'created_at')
    search_fields = ('title', 'description', 'citizen__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ComplaintUpdate)
class ComplaintUpdateAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'authority', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'citizen', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at',)







# # complaints/admin.py
# from django.contrib import admin
# from django.urls import path
# from django.shortcuts import render
# from django.contrib.admin.views.decorators import staff_member_required

# @admin.site.admin_view
# @staff_member_required
# def advanced_reports_admin_view(request):
#     from .views import advanced_reports
#     return advanced_reports(request)

# # Then register this in admin