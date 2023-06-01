from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_email, MaxValueValidator, MinValueValidator
from django.utils import timezone


class Book(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="images/")
    writer = models.CharField(max_length=100)
    description = models.TextField(max_length=10000)
    price = models.FloatField()
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    rate = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(0)])

    def __str__(self):
        return self.book.name


class Profile(models.Model):
    login_info = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    favorite = models.ManyToManyField(Book, related_name="profiles")

    def __str__(self):
        return self.login_info.username


class Message(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200,validators=[validate_email])
    message = models.TextField(max_length=5000)

    def __str__(self):
        return self.name

