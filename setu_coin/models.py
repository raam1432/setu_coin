from django.db import models
from django.contrib.auth.models import User

# वॉलेट मॉडेल - प्रत्येक यूजरसाठी एक वॉलेट
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=100)  # सुरुवातीला 100 SETU coins

    def _str_(self):
        return f"{self.user.username} - {self.balance} SETU"

# ट्रान्सफर इतिहासासाठी मॉडेल (आवश्यक असल्यास)
class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.sender.username} ➝ {self.recipient.username}: {self.amount} SETU"
