"""
Real Estate DBMS - Django Models
Maps to existing MySQL database schema
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class User(AbstractUser):
    """
    Extended User model mapping to Users table
    """
    user_id = models.AutoField(primary_key=True, db_column='user_id')
    phone = models.CharField(max_length=20, null=True, blank=True)
    user_type = models.CharField(
        max_length=10,
        choices=[
            ('admin', 'Admin'),
            ('agent', 'Agent'),
            ('client', 'Client'),
        ],
        default='client'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Map Django's password field to MySQL's password_hash
    password = models.CharField(max_length=255, db_column='password_hash')
    
    # Override username field to use email
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    
    # Fix the clash with Django's built-in User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'Users'
        managed = False
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_type})"
    
    
class Location(models.Model):
    """Location model for property addresses"""
    location_id = models.AutoField(primary_key=True, db_column='location_id')
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='USA')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    class Meta:
        db_table = 'Locations'
        managed = False
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['zip_code']),
        ]
    
    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"


class PropertyType(models.Model):
    """Property type categories"""
    property_type_id = models.AutoField(primary_key=True, db_column='property_type_id')
    type_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'PropertyTypes'
        managed = False
    
    def __str__(self):
        return self.type_name


class Agent(models.Model):
    """Real estate agent model"""
    agent_id = models.AutoField(primary_key=True, db_column='agent_id')
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')
    license_number = models.CharField(max_length=50, unique=True)
    agency_name = models.CharField(max_length=100, null=True, blank=True)
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('3.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    specialization = models.CharField(max_length=100, null=True, blank=True)
    years_experience = models.IntegerField(default=0)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_sales = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'Agents'
        managed = False
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.agency_name}"


class Client(models.Model):
    """Property buyer/renter model"""
    client_id = models.AutoField(primary_key=True, db_column='client_id')
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')
    preferred_contact_method = models.CharField(
        max_length=10,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('text', 'Text'),
        ],
        default='email'
    )
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    preferred_location = models.CharField(max_length=100, null=True, blank=True)
    looking_for = models.CharField(
        max_length=10,
        choices=[
            ('buy', 'Buy'),
            ('rent', 'Rent'),
            ('sell', 'Sell'),
        ]
    )
    
    class Meta:
        db_table = 'Clients'
        managed = False
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Looking to {self.looking_for}"


class Property(models.Model):
    """Main property listing model"""
    property_id = models.AutoField(primary_key=True, db_column='property_id')
    location = models.ForeignKey(Location, on_delete=models.RESTRICT, db_column='location_id')
    property_type = models.ForeignKey(PropertyType, on_delete=models.RESTRICT, db_column='property_type_id')
    agent = models.ForeignKey(Agent, on_delete=models.RESTRICT, db_column='agent_id')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    listing_type = models.CharField(
        max_length=10,
        choices=[
            ('sale', 'For Sale'),
            ('rent', 'For Rent'),
        ]
    )
    bedrooms = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=0, validators=[MinValueValidator(0)])
    square_feet = models.IntegerField(null=True, blank=True)
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    year_built = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('pending', 'Pending'),
            ('sold', 'Sold'),
            ('rented', 'Rented'),
            ('off_market', 'Off Market'),
        ],
        default='available'
    )
    listed_date = models.DateField()
    sold_date = models.DateField(null=True, blank=True)
    parking_spaces = models.IntegerField(default=0)
    has_garage = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Properties'
        managed = False
        ordering = ['-listed_date']
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['status']),
            models.Index(fields=['listing_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - ${self.price:,.0f}"
    
    def get_price_per_sqft(self):
        """Calculate price per square foot"""
        if self.square_feet and self.square_feet > 0:
            return self.price / self.square_feet
        return 0


class PropertyImage(models.Model):
    """Property images model"""
    image_id = models.AutoField(primary_key=True, db_column='image_id')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, db_column='property_id', related_name='images')
    image_url = models.CharField(max_length=500)
    caption = models.CharField(max_length=200, null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'PropertyImages'
        managed = False
        ordering = ['display_order']
    
    def __str__(self):
        return f"Image for {self.property.title}"


class Appointment(models.Model):
    """Property viewing appointments"""
    appointment_id = models.AutoField(primary_key=True, db_column='appointment_id')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, db_column='property_id')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='client_id')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, db_column='agent_id')
    appointment_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60, validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show'),
        ],
        default='scheduled'
    )
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Appointments'
        managed = False
        ordering = ['-appointment_date']
        indexes = [
            models.Index(fields=['appointment_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Appointment for {self.property.title} on {self.appointment_date}"


class Transaction(models.Model):
    """Property sale/rental transactions"""
    transaction_id = models.AutoField(primary_key=True, db_column='transaction_id')
    property = models.ForeignKey(Property, on_delete=models.RESTRICT, db_column='property_id')
    client = models.ForeignKey(Client, on_delete=models.RESTRICT, db_column='client_id')
    agent = models.ForeignKey(Agent, on_delete=models.RESTRICT, db_column='agent_id')
    transaction_type = models.CharField(
        max_length=10,
        choices=[
            ('sale', 'Sale'),
            ('rental', 'Rental'),
        ]
    )
    transaction_date = models.DateField()
    final_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    lease_start_date = models.DateField(null=True, blank=True)
    lease_end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Transactions'
        managed = False
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.transaction_type.title()} - {self.property.title} - ${self.final_price:,.0f}"


class Review(models.Model):
    """Property and agent reviews"""
    review_id = models.AutoField(primary_key=True, db_column='review_id')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='client_id')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, db_column='property_id', related_name='reviews')
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, db_column='agent_id', related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(null=True, blank=True)
    review_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'Reviews'
        managed = False
        ordering = ['-review_date']
    
    def __str__(self):
        if self.property:
            return f"{self.rating} stars for {self.property.title}"
        elif self.agent:
            return f"{self.rating} stars for agent {self.agent.user.first_name}"
        return f"Review #{self.review_id}"
