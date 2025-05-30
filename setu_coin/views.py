from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction

# Assuming Wallet model with 'user' OneToOneField and 'balance' field exists
from .models import Wallet

@login_required
def home(request):
    wallet = getattr(request.user, 'wallet', None)
    return render(request, 'home.html', {'wallet': wallet})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not username or not password or not password2:
            messages.error(request, "All fields are required.")
        elif password != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, password=password)
            Wallet.objects.create(user=user, balance=100)  # Initial coin balance
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def wallet_view(request):
    wallet = get_object_or_404(Wallet, user=request.user)
    return render(request, 'wallet.html', {'wallet': wallet})

@login_required
@transaction.atomic
def transfer_view(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        amount_str = request.POST.get('amount')

        if not recipient_username or not amount_str:
            messages.error(request, "Please fill all fields.")
            return redirect('transfer')

        try:
            amount = int(amount_str)
            if amount <= 0:
                messages.error(request, "Amount must be positive.")
                return redirect('transfer')
        except ValueError:
            messages.error(request, "Invalid amount.")
            return redirect('transfer')

        if recipient_username == request.user.username:
            messages.error(request, "You cannot transfer coins to yourself.")
            return redirect('transfer')

        recipient = User.objects.filter(username=recipient_username).first()
        if not recipient:
            messages.error(request, "Recipient does not exist.")
            return redirect('transfer')

        sender_wallet = get_object_or_404(Wallet, user=request.user)
        recipient_wallet = get_object_or_404(Wallet, user=recipient)

        if sender_wallet.balance < amount:
            messages.error(request, "Insufficient balance.")
            return redirect('transfer')

        # Deduct and add coins atomically
        sender_wallet.balance -= amount
        recipient_wallet.balance += amount
        sender_wallet.save()
        recipient_wallet.save()

        messages.success(request, f"Successfully transferred {amount} SETU coins to {recipient_username}.")
        return redirect('wallet')

    return render(request, 'transfer.html')

