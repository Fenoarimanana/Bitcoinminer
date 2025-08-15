from django.core.management.base import BaseCommand
from core.models import Deposit, Profile
import requests

BITCOIN_ADDRESS = "13ZYu5dRtP8kHrunXXHuDMBoRwaLAr6MCE"  # Ton adresse de dépôt
TOKEN = "977de9fce3374d2ca550c9d3e38bd36f"  # Remplace par ton token BlockCypher

def get_received_btc(address, token):
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full?token={token}"
    response = requests.get(url)
    data = response.json()
    return int(data.get("total_received", 0)) / 1e8  # Satoshis to BTC

def get_btc_usd_rate():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return float(data["bitcoin"]["usd"])

class Command(BaseCommand):
    help = "Check Bitcoin deposits and confirm those received"

    def handle(self, *args, **kwargs):
        pending_deposits = Deposit.objects.filter(status="Pending")
        total_received = get_received_btc(BITCOIN_ADDRESS, TOKEN)
        btc_usd_rate = get_btc_usd_rate()
        print(f"Total received on {BITCOIN_ADDRESS}: {total_received} BTC (BTC/USD: {btc_usd_rate})")

        for deposit in pending_deposits:
            # Convert USD deposit to BTC
            deposit_btc = deposit.amount / btc_usd_rate
            if total_received >= deposit_btc:
                deposit.status = "Confirmed"
                deposit.save()
                profile = Profile.objects.get(user=deposit.user)
                # Ajoute la vitesse de minage : 2$ = 100MH/s
                added_speed = (deposit.amount / 2) * 100
                profile.mining_speed += added_speed
                profile.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Deposit confirmed for {deposit.user.username} ({deposit.amount}$, {deposit_btc:.8f} BTC)"
                ))