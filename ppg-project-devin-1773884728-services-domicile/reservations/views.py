from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reservation
from .forms import ReservationForm
from services.models import Service


@login_required
def create_reservation(request, service_pk):
    service = get_object_or_404(Service, pk=service_pk, is_active=True)

    if request.user == service.provider:
        messages.error(request, "Vous ne pouvez pas réserver votre propre service.")
        return redirect('service_detail', pk=service.pk)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.client = request.user
            reservation.service = service
            reservation.save()
            messages.success(request, 'Réservation effectuée avec succès !')
            return redirect('my_reservations')
    else:
        form = ReservationForm()

    return render(request, 'reservations/create_reservation.html', {
        'form': form,
        'service': service,
    })


@login_required
def my_reservations(request):
    if request.user.is_admin:
        reservations = Reservation.objects.all().order_by('-created_at')
    else:
        reservations = Reservation.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'reservations/my_reservations.html', {
        'reservations': reservations,
    })


@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if not request.user.is_admin and reservation.client != request.user and reservation.service.provider != request.user:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    return render(request, 'reservations/reservation_detail.html', {
        'reservation': reservation,
    })


@login_required
def update_reservation_status(request, pk, status):
    reservation = get_object_or_404(Reservation, pk=pk)

    if reservation.service.provider != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette réservation.")
        return redirect('dashboard')

    if status in ['accepted', 'rejected', 'completed']:
        reservation.status = status
        reservation.save()
        status_labels = {
            'accepted': 'acceptée',
            'rejected': 'refusée',
            'completed': 'marquée comme terminée',
        }
        messages.success(request, f'Réservation {status_labels.get(status, status)} !')

    return redirect('dashboard')


@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, client=request.user)
    if reservation.status == 'pending':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Réservation annulée.')
    else:
        messages.error(request, "Impossible d'annuler cette réservation.")
    return redirect('my_reservations')
