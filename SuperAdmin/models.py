from django.db import models
from django.contrib.auth.models import User
import uuid

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"
    
class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('Main Course', 'Main Course'),
        ('Snacks', 'Snacks'),
        ('Beverages', 'Beverages'),
        ('Desserts', 'Desserts'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.category} (${self.price})"
    
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)  # Email is optional
    phone = models.CharField(max_length=15, blank=True, null=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="feedbacks", null=True, blank=True)
    message = models.TextField()
    review_scores = models.FloatField(null=True, blank=True)
    review_sentiment = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.menu_item.name if self.menu_item else 'No Dish'}"

    

