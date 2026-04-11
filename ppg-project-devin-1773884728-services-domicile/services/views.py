from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Service, Category, Availability
from .forms import ServiceForm, AvailabilityForm
from accounts.models import User
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on Earth in kilometers."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def category_api(request, pk):
    category = get_object_or_404(Category, pk=pk)
    # Use category image if available, else a stylized stock photo URL
    if category.image:
        image_url = category.image.url
    else:
        image_url = f"https://source.unsplash.com/600x400/?{category.name.lower().replace(' ', ',')},service"
    
    desc = category.description
    if not desc:
        desc = f"Découvrez nos professionnels qualifiés pour vos besoins en {category.name.lower()}. Des experts de confiance, sélectionnés pour vous offrir un service de qualité à domicile."
        
    return JsonResponse({
        'id': category.id,
        'name': category.name,
        'description': desc,
        'image_url': image_url,
    })


def category_prestataires(request, pk):
    category = get_object_or_404(Category, pk=pk)
    # Get all active services in this category
    services = Service.objects.filter(category=category, is_active=True).select_related('provider')
    
    # Extract unique providers
    providers_dict = {}
    for service in services:
        provider = service.provider
        if provider.id not in providers_dict:
            providers_dict[provider.id] = {
                'provider': provider,
                'service': service,
                'price': service.price,
                'city': service.city,
                'rating': service.average_rating,
                'reviews_count': service.total_reviews,
            }
            
    # Sort providers by rating descending
    providers_info = sorted(list(providers_dict.values()), key=lambda x: x['rating'], reverse=True)
    
    return render(request, 'services/category_prestataires.html', {
        'category': category,
        'providers_info': providers_info,
    })


def service_list(request):
    services = Service.objects.filter(is_active=True).select_related('provider')
    categories = Category.objects.all()

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    city = request.GET.get('city', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', '')
    
    # Distance filtering params
    user_lat = request.GET.get('lat', '')
    user_lon = request.GET.get('lon', '')
    distance_km = request.GET.get('distance', '50')

    if query:
        services = services.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(provider__first_name__icontains=query) |
            Q(provider__last_name__icontains=query)
        )
    if category_id:
        services = services.filter(category_id=category_id)
    if city:
        services = services.filter(city__icontains=city)
    if min_price:
        services = services.filter(price__gte=min_price)
    if max_price:
        services = services.filter(price__lte=max_price)
    
    # Distance filtering using Haversine formula
    if user_lat and user_lon and distance_km:
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            max_distance = float(distance_km)
            
            # Filter services by provider location
            filtered_services = []
            for service in services:
                provider = service.provider
                if provider.latitude is not None and provider.longitude is not None:
                    dist = haversine_distance(user_lat, user_lon, provider.latitude, provider.longitude)
                    if dist <= max_distance:
                        service.distance = round(dist, 1)
                        filtered_services.append(service)
            
            services = filtered_services
        except (ValueError, TypeError):
            pass

    if sort == 'price_asc':
        services = sorted(services, key=lambda x: x.price) if isinstance(services, list) else services.order_by('price')
    elif sort == 'price_desc':
        services = sorted(services, key=lambda x: x.price, reverse=True) if isinstance(services, list) else services.order_by('-price')
    elif sort == 'newest':
        services = sorted(services, key=lambda x: x.created_at, reverse=True) if isinstance(services, list) else services.order_by('-created_at')
    elif sort == 'distance' and hasattr(services[0], 'distance') if services else False:
        services = sorted(services, key=lambda x: getattr(x, 'distance', float('inf')))

    return render(request, 'services/service_list.html', {
        'services': services,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'city': city,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'lat': user_lat,
        'lon': user_lon,
        'distance': distance_km,
    })


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    from reviews.models import Review
    reviews = Review.objects.filter(reservation__service=service)
    availabilities = Availability.objects.filter(provider=service.provider, is_available=True)
    related_services = Service.objects.filter(
        category=service.category, is_active=True
    ).exclude(pk=service.pk)[:4]
    return render(request, 'services/service_detail.html', {
        'service': service,
        'reviews': reviews,
        'availabilities': availabilities,
        'related_services': related_services,
    })


def category_services(request, pk):
    category = get_object_or_404(Category, pk=pk)
    services = Service.objects.filter(category=category, is_active=True)
    return render(request, 'services/category_services.html', {
        'category': category,
        'services': services,
    })


@login_required
def service_create(request):
    if not request.user.is_prestataire:
        messages.error(request, "Seuls les prestataires peuvent créer des services.")
        return redirect('home')

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            messages.success(request, 'Service créé avec succès !')
            return redirect('service_detail', pk=service.pk)
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Créer un service'})


@login_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service mis à jour !')
            return redirect('service_detail', pk=service.pk)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Modifier le service'})


@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service supprimé.')
        return redirect('dashboard')
    return render(request, 'services/service_delete.html', {'service': service})


@login_required
def manage_availability(request):
    if not request.user.is_prestataire:
        messages.error(request, "Accès réservé aux prestataires.")
        return redirect('home')

    availabilities = Availability.objects.filter(provider=request.user)

    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.provider = request.user
            availability.save()
            messages.success(request, 'Disponibilité ajoutée !')
            return redirect('manage_availability')
    else:
        form = AvailabilityForm()

    return render(request, 'services/manage_availability.html', {
        'availabilities': availabilities,
        'form': form,
    })


@login_required
def delete_availability(request, pk):
    availability = get_object_or_404(Availability, pk=pk, provider=request.user)
    availability.delete()
    messages.success(request, 'Disponibilité supprimée.')
    return redirect('manage_availability')
