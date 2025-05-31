from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .models import Wallet

@login_required
def home(request):
    wallet = getattr(request.user, 'wallet', None)
    return render(request, 'ram/home.html', {'wallet': wallet})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "चूक Username किंवा Password.")
    return render(request, 'ram/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def wallet_view(request):
    wallet = get_object_or_404(Wallet, user=request.user)
    return render(request, 'ram/wallet.html', {'wallet': wallet})

@login_required
@transaction.atomic
def transfer_view(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        amount_str = request.POST.get('amount')

        if not recipient_username or not amount_str:
            messages.error(request, "सर्व फील्ड भरा.")
            return redirect('transfer')

        try:
            amount = int(amount_str)
            if amount <= 0:
                messages.error(request, "रक्कम सकारात्मक असावी.")
                return redirect('transfer')
        except ValueError:
            messages.error(request, "अवैध रक्कम.")
            return redirect('transfer')

        if recipient_username == request.user.username:
            messages.error(request, "स्वतःला Coin ट्रान्सफर करू शकत नाही.")
            return redirect('transfer')

        recipient = User.objects.filter(username=recipient_username).first()
        if not recipient:
            messages.error(request, "प्राप्तकर्ता अस्तित्वात नाही.")
            return redirect('transfer')

        sender_wallet = get_object_or_404(Wallet, user=request.user)
        recipient_wallet = get_object_or_404(Wallet, user=recipient)

        if sender_wallet.balance < amount:
            messages.error(request, "Coin पुरेसे नाहीत.")
            return redirect('transfer')

        sender_wallet.balance -= amount
        recipient_wallet.balance += amount
        sender_wallet.save()
        recipient_wallet.save()

        messages.success(request, f"{amount} SETU coins {recipient_username} यांना ट्रान्सफर झाले.")
        return redirect('wallet')

    return render(request, 'ram/transfer.html')
