from django.core.management.base import BaseCommand
from core.models import Deposit, Profile
import requests

BITCOIN_ADDRESS = "13ZYu5dRtP8kHrunXXHuDMBoRwaLAr6MCE"  # Ton adresse de dépôt

def get_received_btc(address):
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full"
    response = requests.get(url)
    data = response.json()
    return int(data.get("total_received", 0)) / 1e8  # Satoshis to BTC

class Command(BaseCommand):
    help = "Vérifie les dépôts Bitcoin et confirme ceux reçus"

    def handle(self, *args, **kwargs):
        pending_deposits = Deposit.objects.filter(status="Pending")
        total_received = get_received_btc(BITCOIN_ADDRESS)
        print(f"Total reçu sur {BITCOIN_ADDRESS}: {total_received} BTC")

        for deposit in pending_deposits:
            # Ici, tu dois convertir le montant USD en BTC si besoin
            # Par exemple, si deposit.amount est en USD, récupère le taux BTC/USD
            # Pour l'exemple, on suppose que deposit.amount est déjà en BTC
            if total_received >= deposit.amount:
                deposit.status = "Confirmed"
                deposit.save()
                profile = Profile.objects.get(user=deposit.user)
                profile.mining_speed += deposit.amount * 0.00005  # ou ta logique
                profile.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Dépôt confirmé pour {deposit.user.username} ({deposit.amount} BTC)"
                ))