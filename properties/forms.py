"""
Real Estate DBMS - Django Forms
Forms for CRUD operations
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User, Property, Location, PropertyType, Agent, Client,
    Appointment, Transaction, Review, PropertyImage
)
from datetime import datetime


class UserRegistrationForm(UserCreationForm):
    """User registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(max_length=20, required=False)
    user_type = forms.ChoiceField(
        choices=[('client', 'Client'), ('agent', 'Agent')],
        required=True
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'user_type', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Use email as username
        if commit:
            user.save()
        return user


class ClientProfileForm(forms.ModelForm):
    """Client profile information form"""
    class Meta:
        model = Client
        fields = [
            'preferred_contact_method',
            'budget_min',
            'budget_max',
            'preferred_location',
            'looking_for'
        ]
        widgets = {
            'budget_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum Budget'}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Maximum Budget'}),
            'preferred_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Boston, MA'}),
        }


class AgentProfileForm(forms.ModelForm):
    """Agent profile information form"""
    class Meta:
        model = Agent
        fields = [
            'license_number',
            'agency_name',
            'commission_rate',
            'specialization',
            'years_experience'
        ]
        widgets = {
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_name': forms.TextInput(attrs={'class': 'form-control'}),
            'commission_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Residential, Commercial'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class LocationForm(forms.ModelForm):
    """Location/Address form"""
    class Meta:
        model = Location
        fields = [
            'street_address',
            'city',
            'state',
            'zip_code',
            'country',
            'latitude',
            'longitude'
        ]
        widgets = {
            'street_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 Main Street'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Boston'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Massachusetts'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '02108'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'value': 'USA'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001', 'placeholder': 'Optional'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001', 'placeholder': 'Optional'}),
        }


class PropertyForm(forms.ModelForm):
    """Property listing form"""
    
    # Add location fields inline
    street_address = forms.CharField(max_length=200, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=50, required=True)
    zip_code = forms.CharField(max_length=10, required=True)
    
    class Meta:
        model = Property
        fields = [
            'property_type',
            'title',
            'description',
            'price',
            'listing_type',
            'bedrooms',
            'bathrooms',
            'square_feet',
            'lot_size',
            'year_built',
            'parking_spaces',
            'has_garage',
            'has_pool',
            'has_garden',
            'listed_date',
            'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Beautiful Victorian Home...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'listing_type': forms.Select(attrs={'class': 'form-control'}),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'square_feet': forms.NumberInput(attrs={'class': 'form-control'}),
            'lot_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'year_built': forms.NumberInput(attrs={'class': 'form-control'}),
            'parking_spaces': forms.NumberInput(attrs={'class': 'form-control'}),
            'listed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing property, populate location fields
        if self.instance and self.instance.pk:
            self.fields['street_address'].initial = self.instance.location.street_address
            self.fields['city'].initial = self.instance.location.city
            self.fields['state'].initial = self.instance.location.state
            self.fields['zip_code'].initial = self.instance.location.zip_code


class PropertySearchForm(forms.Form):
    """Property search/filter form"""
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, city, or description...'
        })
    )
    listing_type = forms.ChoiceField(
        choices=[('', 'Any'), ('sale', 'For Sale'), ('rent', 'For Rent')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    property_type = forms.ModelChoiceField(
        queryset=PropertyType.objects.all(),
        required=False,
        empty_label="Any Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Price'})
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Price'})
    )
    min_bedrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Bedrooms'})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'Any Status'),
            ('available', 'Available'),
            ('pending', 'Pending'),
            ('sold', 'Sold'),
            ('rented', 'Rented')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class AppointmentForm(forms.ModelForm):
    """Appointment scheduling form"""
    class Meta:
        model = Appointment
        fields = [
            'appointment_date',
            'duration_minutes',
            'notes'
        ]
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': datetime.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'value': 60}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests?'}),
        }


class AppointmentUpdateForm(forms.ModelForm):
    """Form to update appointment status"""
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TransactionForm(forms.ModelForm):
    """Transaction creation form"""
    class Meta:
        model = Transaction
        fields = [
            'transaction_type',
            'transaction_date',
            'final_price',
            'payment_status',
            'lease_start_date',
            'lease_end_date',
            'notes'
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'transaction_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'final_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'lease_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lease_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lease_start_date'].required = False
        self.fields['lease_end_date'].required = False


class ReviewForm(forms.ModelForm):
    """Review submission form"""
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this property or agent...'
            }),
        }


class PropertyImageForm(forms.ModelForm):
    """Property image upload form"""
    class Meta:
        model = PropertyImage
        fields = ['image_url', 'caption', 'is_primary', 'display_order']
        widgets = {
            'image_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/media/property_images/image.jpg'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image description'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
        }
