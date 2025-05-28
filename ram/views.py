from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Wallet, Transaction
from .forms import LoginForm, RegisterForm, TransferForm

def home(request):
    return render(request, 'ram/index.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Wallet.objects.create(user=user)
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'ram/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('wallet')
            messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'ram/index.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def wallet_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(recipient=request.user)
    transactions = transactions.order_by('-timestamp')
    return render(request, 'ram/wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
        'transfer_form': TransferForm()
    })

@login_required
def transfer_view(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient']
            amount = form.cleaned_data['amount']
            try:
                recipient = User.objects.get(username=recipient_username)
                if recipient == request.user:
                    messages.error(request, "You can't transfer coins to yourself.")
                    return redirect('wallet')

                sender_wallet = Wallet.objects.get(user=request.user)
                recipient_wallet, _ = Wallet.objects.get_or_create(user=recipient)

                if sender_wallet.balance >= amount:
                    sender_wallet.balance -= amount
                    recipient_wallet.balance += amount
                    sender_wallet.save()
                    recipient_wallet.save()
                    Transaction.objects.create(sender=request.user, recipient=recipient, amount=amount)
                    messages.success(request, "Transfer successful!")
                else:
                    messages.error(request, "Insufficient balance.")
            except User.DoesNotExist:
                messages.error(request, "Recipient not found.")
    return redirect('wallet')
