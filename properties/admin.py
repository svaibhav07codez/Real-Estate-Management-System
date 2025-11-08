"""
Real Estate DBMS - Django Admin Configuration
Register models for Django admin interface
"""

from django.contrib import admin
from .models import (
    User, Location, PropertyType, Agent, Client,
    Property, PropertyImage, Appointment, Transaction, Review
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['location_id', 'street_address', 'city', 'state', 'zip_code']
    list_filter = ['city', 'state']
    search_fields = ['street_address', 'city', 'zip_code']


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['property_type_id', 'type_name', 'description']
    search_fields = ['type_name']


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['agent_id', 'get_full_name', 'license_number', 'agency_name', 'rating', 'total_sales']
    list_filter = ['agency_name', 'specialization']
    search_fields = ['user__first_name', 'user__last_name', 'license_number']
    ordering = ['-total_sales']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Agent Name'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['client_id', 'get_full_name', 'looking_for', 'budget_min', 'budget_max', 'preferred_location']
    list_filter = ['looking_for', 'preferred_contact_method']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Client Name'


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image_url', 'caption', 'is_primary', 'display_order']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'property_id', 'title', 'price', 'listing_type', 'status',
        'bedrooms', 'bathrooms', 'get_city', 'get_agent', 'listed_date'
    ]
    list_filter = ['status', 'listing_type', 'property_type', 'location__city']
    search_fields = ['title', 'description', 'location__city']
    ordering = ['-listed_date']
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'agent')
        }),
        ('Pricing & Listing', {
            'fields': ('price', 'listing_type', 'status', 'listed_date', 'sold_date')
        }),
        ('Property Details', {
            'fields': (
                'bedrooms', 'bathrooms', 'square_feet', 'lot_size',
                'year_built', 'parking_spaces'
            )
        }),
        ('Features', {
            'fields': ('has_garage', 'has_pool', 'has_garden')
        }),
        ('Location', {
            'fields': ('location',)
        }),
    )
    
    def get_city(self, obj):
        return obj.location.city
    get_city.short_description = 'City'
    
    def get_agent(self, obj):
        return f"{obj.agent.user.first_name} {obj.agent.user.last_name}"
    get_agent.short_description = 'Agent'


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['image_id', 'property', 'caption', 'is_primary', 'display_order', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['property__title', 'caption']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'appointment_id', 'get_property', 'get_client', 'get_agent',
        'appointment_date', 'status', 'created_at'
    ]
    list_filter = ['status', 'appointment_date']
    search_fields = ['property__title', 'client__user__email', 'agent__user__email']
    ordering = ['-appointment_date']
    
    def get_property(self, obj):
        return obj.property.title
    get_property.short_description = 'Property'
    
    def get_client(self, obj):
        return f"{obj.client.user.first_name} {obj.client.user.last_name}"
    get_client.short_description = 'Client'
    
    def get_agent(self, obj):
        return f"{obj.agent.user.first_name} {obj.agent.user.last_name}"
    get_agent.short_description = 'Agent'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'get_property', 'transaction_type',
        'final_price', 'commission_amount', 'payment_status',
        'transaction_date'
    ]
    list_filter = ['transaction_type', 'payment_status', 'transaction_date']
    search_fields = ['property__title', 'client__user__email']
    ordering = ['-transaction_date']
    
    readonly_fields = ['commission_amount', 'created_at']
    
    def get_property(self, obj):
        return obj.property.title
    get_property.short_description = 'Property'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'review_id', 'get_client', 'get_property', 'get_agent',
        'rating', 'is_verified', 'review_date'
    ]
    list_filter = ['rating', 'is_verified', 'review_date']
    search_fields = ['client__user__email', 'property__title', 'review_text']
    ordering = ['-review_date']
    
    def get_client(self, obj):
        return f"{obj.client.user.first_name} {obj.client.user.last_name}"
    get_client.short_description = 'Client'
    
    def get_property(self, obj):
        return obj.property.title if obj.property else 'N/A'
    get_property.short_description = 'Property'
    
    def get_agent(self, obj):
        if obj.agent:
            return f"{obj.agent.user.first_name} {obj.agent.user.last_name}"
        return 'N/A'
    get_agent.short_description = 'Agent'


# Customize admin site headers
admin.site.site_header = "Real Estate DBMS Administration"
admin.site.site_title = "Real Estate Admin"
admin.site.index_title = "Welcome to Real Estate DBMS Admin Portal"
