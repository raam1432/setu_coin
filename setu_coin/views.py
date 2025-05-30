from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    wallet = None
    if hasattr(request.user, 'wallet'):
        wallet = request.user.wallet
    return render(request, 'home.html', {'wallet': wallet})
