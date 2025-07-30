from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mining_speed = models.FloatField(default=0.0)
    mined_amount = models.FloatField(default=0.0)
    referral_code = models.CharField(max_length=100, unique=True)
    referred_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')

    def __str__(self):
        return self.user.username
    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, referral_code=f"ref{instance.id}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

class Withdraw(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    btc_address = models.CharField(max_length=100, null=True, blank=True )
    status = models.CharField(max_length=20, default='Pending')
    date = models.DateTimeField(auto_now_add=True)

