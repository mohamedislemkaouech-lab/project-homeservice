from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Review
from .forms import ReviewForm
from reservations.models import Reservation


@login_required
def create_review(request, reservation_pk):
    reservation = get_object_or_404(Reservation, pk=reservation_pk, client=request.user)

    if reservation.status != 'completed':
        messages.error(request, "Vous ne pouvez laisser un avis que pour une réservation terminée.")
        return redirect('my_reservations')

    if hasattr(reservation, 'review'):
        messages.info(request, "Vous avez déjà laissé un avis pour cette réservation.")
        return redirect('my_reservations')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reservation = reservation
            review.client = request.user
            review.save()
            messages.success(request, 'Avis soumis avec succès !')
            return redirect('my_reservations')
    else:
        form = ReviewForm()

    return render(request, 'reviews/create_review.html', {
        'form': form,
        'reservation': reservation,
    })


@login_required
@require_POST
def moderate_review(request, pk, action):
    """Only admins can moderate reviews"""
    if not request.user.is_admin:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')
    
    review = get_object_or_404(Review, pk=pk)
    
    if action == 'hide':
        review.is_visible = False
        review.moderation_note = "Masqué par l'administrateur"
        review.save()
        messages.success(request, "L'avis a été masqué.")
    elif action == 'show':
        review.is_visible = True
        review.moderation_note = "Validé par l'administrateur"
        review.save()
        messages.success(request, "L'avis a été affiché.")
    else:
        messages.error(request, "Action non valide.")
    
    return redirect('dashboard')
