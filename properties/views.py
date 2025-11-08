"""
Real Estate DBMS - Django Views
All CRUD operations for the application
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from django.db import connection
from django.http import HttpResponseForbidden
from datetime import datetime, date
from decimal import Decimal

from .models import (
    User, Property, Location, PropertyType, Agent, Client,
    Appointment, Transaction, Review, PropertyImage
)
from .forms import (
    UserRegistrationForm, ClientProfileForm, AgentProfileForm,
    PropertyForm, PropertySearchForm, AppointmentForm,
    TransactionForm, ReviewForm, PropertyImageForm,
    AppointmentUpdateForm, LocationForm
)


# =====================================================
# AUTHENTICATION VIEWS
# =====================================================

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user_type = form.cleaned_data.get('user_type')
                
                # Create corresponding profile (Agent or Client)
                if user_type == 'agent':
                    # Redirect to agent profile completion
                    messages.success(request, 'Account created! Please complete your agent profile.')
                    login(request, user)
                    return redirect('agent_profile_create')
                else:
                    # Redirect to client profile completion
                    messages.success(request, 'Account created! Please complete your profile.')
                    login(request, user)
                    return redirect('client_profile_create')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# =====================================================
# HOME AND DASHBOARD VIEWS
# =====================================================

def home_view(request):
    """Homepage view"""
    # Get featured/latest properties
    featured_properties = Property.objects.filter(status='available').order_by('-listed_date')[:6]
    
    # Get statistics
    total_properties = Property.objects.count()
    available_properties = Property.objects.filter(status='available').count()
    total_agents = Agent.objects.count()
    
    context = {
        'featured_properties': featured_properties,
        'total_properties': total_properties,
        'available_properties': available_properties,
        'total_agents': total_agents,
    }
    return render(request, 'home.html', context)


@login_required
def dashboard_view(request):
    """User dashboard - redirects based on user type"""
    user = request.user
    
    if user.user_type == 'admin':
        return redirect('admin_dashboard')
    elif user.user_type == 'agent':
        return redirect('agent_dashboard')
    else:
        return redirect('client_dashboard')


@login_required
def client_dashboard(request):
    """Client dashboard view"""
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        messages.warning(request, 'Please complete your profile.')
        return redirect('client_profile_create')
    
    # Get client's appointments
    appointments = Appointment.objects.filter(client=client).order_by('-appointment_date')[:5]
    
    # Get client's reviews
    reviews = Review.objects.filter(client=client).order_by('-review_date')[:5]
    
    # Get recommended properties based on client preferences
    recommended_properties = Property.objects.filter(status='available')
    if client.budget_min and client.budget_max:
        recommended_properties = recommended_properties.filter(
            price__gte=client.budget_min,
            price__lte=client.budget_max
        )
    if client.preferred_location:
        recommended_properties = recommended_properties.filter(
            location__city__icontains=client.preferred_location
        )
    recommended_properties = recommended_properties[:6]
    
    context = {
        'client': client,
        'appointments': appointments,
        'reviews': reviews,
        'recommended_properties': recommended_properties,
    }
    return render(request, 'dashboard/client_dashboard.html', context)


@login_required
def agent_dashboard(request):
    """Agent dashboard view"""
    try:
        agent = Agent.objects.get(user=request.user)
    except Agent.DoesNotExist:
        messages.warning(request, 'Please complete your agent profile.')
        return redirect('agent_profile_create')
    
    # Get agent's properties
    properties = Property.objects.filter(agent=agent)
    active_listings = properties.filter(status='available').count()
    
    # Get upcoming appointments
    appointments = Appointment.objects.filter(agent=agent, status='scheduled').order_by('appointment_date')[:5]
    
    # Get recent transactions
    transactions = Transaction.objects.filter(agent=agent).order_by('-transaction_date')[:5]
    
    # Calculate statistics
    total_commission = Transaction.objects.filter(
        agent=agent, 
        payment_status='completed'
    ).aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    
    context = {
        'agent': agent,
        'properties': properties,
        'active_listings': active_listings,
        'appointments': appointments,
        'transactions': transactions,
        'total_commission': total_commission,
    }
    return render(request, 'dashboard/agent_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    if request.user.user_type != 'admin':
        return HttpResponseForbidden("Access denied")
    
    # System-wide statistics
    total_properties = Property.objects.count()
    total_users = User.objects.count()
    total_agents = Agent.objects.count()
    total_clients = Client.objects.count()
    total_transactions = Transaction.objects.count()
    
    # Recent activities
    recent_properties = Property.objects.order_by('-created_at')[:5]
    recent_transactions = Transaction.objects.order_by('-transaction_date')[:5]
    
    # Revenue statistics
    total_revenue = Transaction.objects.filter(
        payment_status='completed'
    ).aggregate(Sum('final_price'))['final_price__sum'] or 0
    
    context = {
        'total_properties': total_properties,
        'total_users': total_users,
        'total_agents': total_agents,
        'total_clients': total_clients,
        'total_transactions': total_transactions,
        'total_revenue': total_revenue,
        'recent_properties': recent_properties,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# =====================================================
# PROFILE VIEWS (CREATE & UPDATE)
# =====================================================

@login_required
def client_profile_create(request):
    """Create client profile"""
    # Check if profile already exists
    if Client.objects.filter(user=request.user).exists():
        messages.info(request, 'Profile already exists.')
        return redirect('client_profile_update')
    
    if request.method == 'POST':
        form = ClientProfileForm(request.POST)
        if form.is_valid():
            try:
                client = form.save(commit=False)
                client.user = request.user
                client.save()
                messages.success(request, 'Profile created successfully!')
                return redirect('client_dashboard')
            except Exception as e:
                messages.error(request, f'Error creating profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientProfileForm()
    
    return render(request, 'profile/client_profile_form.html', {'form': form, 'action': 'Create'})


@login_required
def client_profile_update(request):
    """Update client profile"""
    client = get_object_or_404(Client, user=request.user)
    
    if request.method == 'POST':
        form = ClientProfileForm(request.POST, instance=client)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('client_dashboard')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
    else:
        form = ClientProfileForm(instance=client)
    
    return render(request, 'profile/client_profile_form.html', {'form': form, 'action': 'Update'})


@login_required
def agent_profile_create(request):
    """Create agent profile"""
    # Check if profile already exists
    if Agent.objects.filter(user=request.user).exists():
        messages.info(request, 'Profile already exists.')
        return redirect('agent_profile_update')
    
    if request.method == 'POST':
        form = AgentProfileForm(request.POST)
        if form.is_valid():
            try:
                agent = form.save(commit=False)
                agent.user = request.user
                agent.save()
                messages.success(request, 'Agent profile created successfully!')
                return redirect('agent_dashboard')
            except Exception as e:
                messages.error(request, f'Error creating profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AgentProfileForm()
    
    return render(request, 'profile/agent_profile_form.html', {'form': form, 'action': 'Create'})


@login_required
def agent_profile_update(request):
    """Update agent profile"""
    agent = get_object_or_404(Agent, user=request.user)
    
    if request.method == 'POST':
        form = AgentProfileForm(request.POST, instance=agent)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('agent_dashboard')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
    else:
        form = AgentProfileForm(instance=agent)
    
    return render(request, 'profile/agent_profile_form.html', {'form': form, 'action': 'Update'})


# =====================================================
# PROPERTY VIEWS (CRUD)
# =====================================================

def property_list_view(request):
    """List all properties with search/filter"""
    properties = Property.objects.filter(status='available').select_related(
        'location', 'property_type', 'agent__user'
    )
    
    # Search and filter
    form = PropertySearchForm(request.GET)
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        listing_type = form.cleaned_data.get('listing_type')
        property_type = form.cleaned_data.get('property_type')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        min_bedrooms = form.cleaned_data.get('min_bedrooms')
        city = form.cleaned_data.get('city')
        status = form.cleaned_data.get('status')
        
        if search_query:
            properties = properties.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__city__icontains=search_query)
            )
        
        if listing_type:
            properties = properties.filter(listing_type=listing_type)
        
        if property_type:
            properties = properties.filter(property_type=property_type)
        
        if min_price:
            properties = properties.filter(price__gte=min_price)
        
        if max_price:
            properties = properties.filter(price__lte=max_price)
        
        if min_bedrooms:
            properties = properties.filter(bedrooms__gte=min_bedrooms)
        
        if city:
            properties = properties.filter(location__city__icontains=city)
        
        if status:
            properties = properties.filter(status=status)
    
    context = {
        'properties': properties,
        'form': form,
    }
    return render(request, 'properties/property_list.html', context)


def property_detail_view(request, pk):
    """Property detail view"""
    property_obj = get_object_or_404(
        Property.objects.select_related('location', 'property_type', 'agent__user'),
        pk=pk
    )
    
    # Get property images
    images = PropertyImage.objects.filter(property=property_obj).order_by('display_order')
    
    # Get reviews
    reviews = Review.objects.filter(property=property_obj).select_related('client__user')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Check if user can schedule appointment
    can_schedule = False
    if request.user.is_authenticated and request.user.user_type == 'client':
        try:
            client = Client.objects.get(user=request.user)
            can_schedule = True
        except Client.DoesNotExist:
            pass
    
    context = {
        'property': property_obj,
        'images': images,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'can_schedule': can_schedule,
    }
    return render(request, 'properties/property_detail.html', context)


@login_required
def property_create_view(request):
    """Create new property (Agent only)"""
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("Only agents can create properties")
    
    try:
        agent = Agent.objects.get(user=request.user)
    except Agent.DoesNotExist:
        messages.error(request, 'Please complete your agent profile first.')
        return redirect('agent_profile_create')
    
    if request.method == 'POST':
        property_form = PropertyForm(request.POST)
        
        if property_form.is_valid():
            try:
                # Create location first
                location = Location.objects.create(
                    street_address=property_form.cleaned_data['street_address'],
                    city=property_form.cleaned_data['city'],
                    state=property_form.cleaned_data['state'],
                    zip_code=property_form.cleaned_data['zip_code'],
                    country='USA'
                )
                
                # Create property
                property_obj = property_form.save(commit=False)
                property_obj.location = location
                property_obj.agent = agent
                property_obj.save()
                
                messages.success(request, 'Property created successfully!')
                return redirect('property_detail', pk=property_obj.pk)
            except Exception as e:
                messages.error(request, f'Error creating property: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        property_form = PropertyForm(initial={'listed_date': date.today()})
    
    return render(request, 'properties/property_form.html', {
        'form': property_form,
        'action': 'Create'
    })


@login_required
def property_update_view(request, pk):
    """Update property (Agent only - own properties)"""
    property_obj = get_object_or_404(Property, pk=pk)
    
    # Check if user is the agent who listed this property
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("Only agents can update properties")
    
    try:
        agent = Agent.objects.get(user=request.user)
        if property_obj.agent != agent:
            return HttpResponseForbidden("You can only update your own properties")
    except Agent.DoesNotExist:
        return redirect('agent_profile_create')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_obj)
        
        if form.is_valid():
            try:
                # Update location
                location = property_obj.location
                location.street_address = form.cleaned_data['street_address']
                location.city = form.cleaned_data['city']
                location.state = form.cleaned_data['state']
                location.zip_code = form.cleaned_data['zip_code']
                location.save()
                
                # Update property
                form.save()
                
                messages.success(request, 'Property updated successfully!')
                return redirect('property_detail', pk=property_obj.pk)
            except Exception as e:
                messages.error(request, f'Error updating property: {str(e)}')
    else:
        form = PropertyForm(instance=property_obj)
    
    return render(request, 'properties/property_form.html', {
        'form': form,
        'action': 'Update',
        'property': property_obj
    })


@login_required
def property_delete_view(request, pk):
    """Delete property (Agent only - own properties)"""
    property_obj = get_object_or_404(Property, pk=pk)
    
    # Check permissions
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("Only agents can delete properties")
    
    try:
        agent = Agent.objects.get(user=request.user)
        if property_obj.agent != agent:
            return HttpResponseForbidden("You can only delete your own properties")
    except Agent.DoesNotExist:
        return redirect('agent_profile_create')
    
    if request.method == 'POST':
        try:
            property_title = property_obj.title
            property_obj.delete()
            messages.success(request, f'Property "{property_title}" deleted successfully!')
            return redirect('agent_dashboard')
        except Exception as e:
            messages.error(request, f'Error deleting property: {str(e)}')
    
    return render(request, 'properties/property_confirm_delete.html', {
        'property': property_obj
    })


# =====================================================
# APPOINTMENT VIEWS (CRUD)
# =====================================================

@login_required
def appointment_create_view(request, property_pk):
    """Schedule appointment (Client only)"""
    if request.user.user_type != 'client':
        return HttpResponseForbidden("Only clients can schedule appointments")
    
    property_obj = get_object_or_404(Property, pk=property_pk)
    
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('client_profile_create')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                appointment = form.save(commit=False)
                appointment.property = property_obj
                appointment.client = client
                appointment.agent = property_obj.agent
                appointment.status = 'scheduled'
                appointment.save()
                
                messages.success(request, 'Appointment scheduled successfully!')
                return redirect('appointment_list')
            except Exception as e:
                messages.error(request, f'Error scheduling appointment: {str(e)}')
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/appointment_form.html', {
        'form': form,
        'property': property_obj,
        'action': 'Schedule'
    })


@login_required
def appointment_list_view(request):
    """List user's appointments"""
    if request.user.user_type == 'client':
        try:
            client = Client.objects.get(user=request.user)
            appointments = Appointment.objects.filter(client=client).select_related(
                'property', 'agent__user'
            ).order_by('-appointment_date')
        except Client.DoesNotExist:
            appointments = []
    elif request.user.user_type == 'agent':
        try:
            agent = Agent.objects.get(user=request.user)
            appointments = Appointment.objects.filter(agent=agent).select_related(
                'property', 'client__user'
            ).order_by('-appointment_date')
        except Agent.DoesNotExist:
            appointments = []
    else:
        appointments = Appointment.objects.all().select_related(
            'property', 'client__user', 'agent__user'
        ).order_by('-appointment_date')
    
    context = {
        'appointments': appointments
    }
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def appointment_update_view(request, pk):
    """Update appointment status"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check permissions
    if request.user.user_type == 'client':
        client = Client.objects.get(user=request.user)
        if appointment.client != client:
            return HttpResponseForbidden("You can only update your own appointments")
    elif request.user.user_type == 'agent':
        agent = Agent.objects.get(user=request.user)
        if appointment.agent != agent:
            return HttpResponseForbidden("You can only update appointments for your properties")
    
    if request.method == 'POST':
        form = AppointmentUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Appointment updated successfully!')
                return redirect('appointment_list')
            except Exception as e:
                messages.error(request, f'Error updating appointment: {str(e)}')
    else:
        form = AppointmentUpdateForm(instance=appointment)
    
    return render(request, 'appointments/appointment_update.html', {
        'form': form,
        'appointment': appointment
    })


@login_required
def appointment_delete_view(request, pk):
    """Cancel/delete appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check permissions
    if request.user.user_type == 'client':
        client = Client.objects.get(user=request.user)
        if appointment.client != client:
            return HttpResponseForbidden("You can only cancel your own appointments")
    elif request.user.user_type == 'agent':
        agent = Agent.objects.get(user=request.user)
        if appointment.agent != agent:
            return HttpResponseForbidden("Access denied")
    
    if request.method == 'POST':
        try:
            appointment.delete()
            messages.success(request, 'Appointment cancelled successfully!')
            return redirect('appointment_list')
        except Exception as e:
            messages.error(request, f'Error cancelling appointment: {str(e)}')
    
    return render(request, 'appointments/appointment_confirm_delete.html', {
        'appointment': appointment
    })


# =====================================================
# TRANSACTION VIEWS (CRUD)
# =====================================================

@login_required
def transaction_create_view(request, property_pk):
    """Create transaction (Agent only)"""
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("Only agents can create transactions")
    
    property_obj = get_object_or_404(Property, pk=property_pk)
    agent = get_object_or_404(Agent, user=request.user)
    
    if property_obj.agent != agent:
        return HttpResponseForbidden("You can only create transactions for your properties")
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        client_id = request.POST.get('client_id')
        
        if form.is_valid() and client_id:
            try:
                client = Client.objects.get(client_id=client_id)
                
                transaction = form.save(commit=False)
                transaction.property = property_obj
                transaction.client = client
                transaction.agent = agent
                
                # Calculate commission
                commission = transaction.final_price * (agent.commission_rate / 100)
                transaction.commission_amount = commission
                
                transaction.save()
                
                # Update property status
                if transaction.transaction_type == 'sale':
                    property_obj.status = 'sold'
                else:
                    property_obj.status = 'rented'
                property_obj.sold_date = transaction.transaction_date
                property_obj.save()
                
                # Update agent stats
                agent.total_sales += 1
                agent.save()
                
                messages.success(request, 'Transaction created successfully!')
                return redirect('transaction_list')
            except Client.DoesNotExist:
                messages.error(request, 'Client not found.')
            except Exception as e:
                messages.error(request, f'Error creating transaction: {str(e)}')
    else:
        form = TransactionForm(initial={
            'transaction_date': date.today(),
            'final_price': property_obj.price
        })
    
    # Get potential clients (those who have appointments for this property)
    potential_clients = Client.objects.filter(
        appointment__property=property_obj
    ).distinct()
    
    return render(request, 'transactions/transaction_form.html', {
        'form': form,
        'property': property_obj,
        'potential_clients': potential_clients,
        'action': 'Create'
    })


@login_required
def transaction_list_view(request):
    """List transactions"""
    if request.user.user_type == 'agent':
        agent = get_object_or_404(Agent, user=request.user)
        transactions = Transaction.objects.filter(agent=agent).select_related(
            'property', 'client__user'
        ).order_by('-transaction_date')
    elif request.user.user_type == 'client':
        client = get_object_or_404(Client, user=request.user)
        transactions = Transaction.objects.filter(client=client).select_related(
            'property', 'agent__user'
        ).order_by('-transaction_date')
    else:
        transactions = Transaction.objects.all().select_related(
            'property', 'client__user', 'agent__user'
        ).order_by('-transaction_date')
    
    context = {
        'transactions': transactions
    }
    return render(request, 'transactions/transaction_list.html', context)


@login_required
def transaction_detail_view(request, pk):
    """Transaction detail view"""
    transaction = get_object_or_404(
        Transaction.objects.select_related('property', 'client__user', 'agent__user'),
        pk=pk
    )
    
    # Check permissions
    if request.user.user_type == 'client':
        client = Client.objects.get(user=request.user)
        if transaction.client != client:
            return HttpResponseForbidden("Access denied")
    elif request.user.user_type == 'agent':
        agent = Agent.objects.get(user=request.user)
        if transaction.agent != agent:
            return HttpResponseForbidden("Access denied")
    
    return render(request, 'transactions/transaction_detail.html', {
        'transaction': transaction
    })


# =====================================================
# REVIEW VIEWS (CRUD)
# =====================================================

@login_required
def review_create_view(request, property_pk):
    """Create review for property (Client only)"""
    if request.user.user_type != 'client':
        return HttpResponseForbidden("Only clients can write reviews")
    
    property_obj = get_object_or_404(Property, pk=property_pk)
    client = get_object_or_404(Client, user=request.user)
    
    # Check if client has already reviewed this property
    if Review.objects.filter(client=client, property=property_obj).exists():
        messages.warning(request, 'You have already reviewed this property.')
        return redirect('property_detail', pk=property_pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.client = client
                review.property = property_obj
                review.agent = property_obj.agent
                review.save()
                
                messages.success(request, 'Review submitted successfully!')
                return redirect('property_detail', pk=property_pk)
            except Exception as e:
                messages.error(request, f'Error submitting review: {str(e)}')
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/review_form.html', {
        'form': form,
        'property': property_obj
    })


@login_required
def review_delete_view(request, pk):
    """Delete review"""
    review = get_object_or_404(Review, pk=pk)
    
    # Check if user owns this review
    client = get_object_or_404(Client, user=request.user)
    if review.client != client and request.user.user_type != 'admin':
        return HttpResponseForbidden("You can only delete your own reviews")
    
    if request.method == 'POST':
        try:
            property_pk = review.property.pk if review.property else None
            review.delete()
            messages.success(request, 'Review deleted successfully!')
            if property_pk:
                return redirect('property_detail', pk=property_pk)
            return redirect('client_dashboard')
        except Exception as e:
            messages.error(request, f'Error deleting review: {str(e)}')
    
    return render(request, 'reviews/review_confirm_delete.html', {
        'review': review
    })


# =====================================================
# ANALYTICS/REPORTING VIEWS (BONUS)
# =====================================================

@login_required
def analytics_view(request):
    """Analytics dashboard"""
    if request.user.user_type not in ['admin', 'agent']:
        return HttpResponseForbidden("Access denied")
    
    # Property statistics
    total_properties = Property.objects.count()
    available_properties = Property.objects.filter(status='available').count()
    sold_properties = Property.objects.filter(status='sold').count()
    
    # Average prices
    avg_price = Property.objects.filter(status='available').aggregate(Avg('price'))['price__avg'] or 0
    
    # Properties by type
    properties_by_type = Property.objects.values('property_type__type_name').annotate(
        count=Count('property_id')
    )
    
    # Properties by city
    properties_by_city = Property.objects.values('location__city').annotate(
        count=Count('property_id')
    ).order_by('-count')[:10]
    
    context = {
        'total_properties': total_properties,
        'available_properties': available_properties,
        'sold_properties': sold_properties,
        'avg_price': avg_price,
        'properties_by_type': properties_by_type,
        'properties_by_city': properties_by_city,
    }
    
    return render(request, 'analytics/analytics.html', context)
