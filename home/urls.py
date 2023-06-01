from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup", views.signup),
    path("login", views.log_in),
    path("logout", views.log_out),
    path("cart", views.cart),
    path("product/<int:pk>", views.product_details),
    path("add/<int:pk>", views.add_to_cart),
    path("delete/<int:pk>", views.delete_from_cart),
    path("rate/<int:pk>", views.rate_product),
    path("checkout/", views.checkout),
    path("success", views.success),
    path("cancel", views.cancel),
    path("contact", views.contact),
    path("about", views.about),
]
