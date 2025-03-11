from django.db import models

# Create your models here.

class SnackItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity_available = models.IntegerField()
    
    def __str__(self):
        return self.name
