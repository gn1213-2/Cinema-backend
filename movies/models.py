from django.db import models
from users.models import User

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    poster_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title

class Theater(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    
    def __str__(self):
        return self.name

class Showing(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.movie.title} - {self.theater.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showing = models.ForeignKey(Showing, on_delete=models.CASCADE)
    seats = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.showing} - {self.seats} seats"
