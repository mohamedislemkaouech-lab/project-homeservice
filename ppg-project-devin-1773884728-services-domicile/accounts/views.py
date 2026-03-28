from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ClientRegistrationForm, PrestataireRegistrationForm, LoginForm, ProfileUpdateForm
from .models import User


def home(request):
    from services.models import Category, Service
    categories = Category.objects.all()
    featured_services = Service.objects.filter(is_active=True)[:6]
    top_providers = User.objects.filter(role='prestataire')[:4]
    return render(request, 'home.html', {
        'categories': categories,
        'featured_services': featured_services,
        'top_providers': top_providers,
    })


def register_choice(request):
    return render(request, 'accounts/register_choice.html')


def register_client(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte client créé avec succès !')
            return redirect('home')
    else:
        form = ClientRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'client'})


def register_prestataire(request):
    if request.method == 'POST':
        form = PrestataireRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte prestataire créé avec succès ! Votre pièce d\'identité est en cours de vérification.')
            return redirect('home')
    else:
        form = PrestataireRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'prestataire'})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenue, {user.get_full_name()} !')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('home')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'profile_user': request.user})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès !')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


def provider_profile(request, pk):
    provider = get_object_or_404(User, pk=pk, role='prestataire')
    services = provider.services.filter(is_active=True)
    from reviews.models import Review
    reviews = Review.objects.filter(reservation__service__provider=provider).order_by('-created_at')[:10]
    return render(request, 'accounts/provider_profile.html', {
        'provider': provider,
        'services': services,
        'reviews': reviews,
    })


@login_required
def dashboard(request):
    if request.user.is_prestataire:
        from reservations.models import Reservation
        services = request.user.services.all()
        pending_reservations = Reservation.objects.filter(
            service__provider=request.user, status='pending'
        )
        active_reservations = Reservation.objects.filter(
            service__provider=request.user, status='accepted'
        )
        completed_reservations = Reservation.objects.filter(
            service__provider=request.user, status='completed'
        )
        return render(request, 'accounts/dashboard_prestataire.html', {
            'services': services,
            'pending_reservations': pending_reservations,
            'active_reservations': active_reservations,
            'completed_reservations': completed_reservations,
        })
    elif request.user.is_admin:
        from reservations.models import Reservation
        reservations = Reservation.objects.all().order_by('-created_at')
        pending_providers = User.objects.filter(role='prestataire', verification_status='pending')
        return render(request, 'accounts/dashboard_client.html', {
            'reservations': reservations,
            'pending_providers': pending_providers,
            'is_admin_view': True,
        })
    else:
        from reservations.models import Reservation
        reservations = Reservation.objects.filter(client=request.user).order_by('-created_at')
        return render(request, 'accounts/dashboard_client.html', {
            'reservations': reservations,
        })

@login_required
def update_provider_status(request, pk, status):
    if not request.user.is_admin:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
        
    provider = get_object_or_404(User, pk=pk, role='prestataire')
    if status in ['approved', 'rejected']:
        provider.verification_status = status
        provider.save()
        status_label = "validé" if status == 'approved' else "rejeté"
        messages.success(request, f'Le prestataire {provider.get_full_name()} a été {status_label}.')
    return redirect('dashboard')

