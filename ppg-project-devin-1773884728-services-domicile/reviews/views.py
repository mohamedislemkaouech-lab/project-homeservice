from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
