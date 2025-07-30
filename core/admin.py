from django.contrib import admin
from .models import Profile, Deposit, Withdraw

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'date')
    list_filter = ('status',)
    actions = ['mark_as_confirmed']

    def mark_as_confirmed(self, request, queryset):
        for deposit in queryset:
            if deposit.status != 'Confirmed':
                deposit.status = 'Confirmed'
                deposit.save()
                profile = deposit.user.profile
                # Calcul proportionnel : 2$ = 100MH/s
                added_speed = (deposit.amount / 2) * 100
                profile.mining_speed += added_speed
                profile.save()
                if profile.referred_by:
                    ref_profile = profile.referred_by.profile
                    referral_bonus = added_speed * 0.2  # 20% du minage du filleul
                    ref_profile.mining_speed += referral_bonus
                    ref_profile.save()
        self.message_user(request, "Selected deposits marked as confirmed and mining speed updated.")

admin.site.register(Profile)
admin.site.register(Withdraw)