from django.contrib import admin
from .models import Book, Rating, Message


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("name", "writer", "price")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("book", "rate")
