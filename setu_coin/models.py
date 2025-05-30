from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=100)  # सुरुवातीला 100 coins

    def _str_(self):
        return f"{self.user.username} - {self.balance} SETU"
