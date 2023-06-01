from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,JsonResponse
from django.contrib.auth import authenticate, login, logout
from .validators import validate_signup, validate_login
from .models import Profile, Book, Message
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_avg(obj):
    tot = 0
    count = 0
    for i in obj.ratings.all():
        tot += i.rate
        count += 1
    raters = count
    if count == 0:
        count = 1
        raters = 0
    return int(tot/count), raters


def home(request):
    books = Book.objects.all().order_by("date_added")
    for book in books:
        book.rate, book.raters = get_avg(book)
    try:
        favorites = request.user.profile.favorite.all()
    except:
        favorites = []
    return render(request, "home.html",
                  context={
                      'books': books,
                      'logged': request.user.is_authenticated,
                      "super": request.user.is_superuser,
                      'favorites': favorites,
                  }
    )


def contact(request):
    if request.method == "GET":
        typ = request.GET.get("type", "")
        return render(request, "contact.html", context={'logged': request.user.is_authenticated,"super": request.user.is_superuser,"type":typ})
    if request.method == "POST":
        try:
            name = request.POST.get("name", "UNKNOWN")
            email = request.POST.get("email", "email@example.com")
            message = request.POST.get("message", "empty message")
            Message.objects.create(name=name, email=email, message=message)
            return redirect("/contact?type=success")
        except:
            return redirect("/contact?type=failed")


def about(request):
    return render(request, "about.html", context={'logged': request.user.is_authenticated, "super": request.user.is_superuser,})


def signup(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to="/")
        return render(request, "signup.html", context={'message': ''})
    if request.method == "POST":
        if request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to="/")
        data = {
            "username": request.POST.get("username", None),
            "email": request.POST.get("email", None),
            "password1": request.POST.get("password1", None),
            "password2": request.POST.get("password2", None)
        }
        url = request.GET.get("url", "/")
        check = validate_signup(data)
        if not check[0]:
            return render(request, "signup.html", context={'message': check[1]})
        user = User.objects.create_user(username=data["username"], email=data["email"], password=data["password1"])
        prof = Profile.objects.create(login_info=user)
        login(request, user=user)
        return HttpResponseRedirect(redirect_to=url)


def log_in(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to="/")
        return render(request, "login.html", context={'message': ''})
    if request.method == "POST":
        if request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to="/")
        data = {
            "username": request.POST.get("username", None),
            "password": request.POST.get("password", None),
        }
        url = request.GET.get("url","/")
        check = validate_login(data)
        if not check[0]:
            return render(request, "login.html", context={'message': check[1]})
        user = authenticate(request, username=data["username"], password=data["password"])
        if not user:
            return render(request, "login.html", context={'message': "USERNAME OR PASSWORD IS INCORRECT, PLEASE TRY AGAIN"})
        login(request, user=user)
        return HttpResponseRedirect(redirect_to=url)


def log_out(request):
    if request.method == "GET":
        logout(request)
        return HttpResponseRedirect(redirect_to="/")


def cart(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            try:
                books = request.user.profile.favorite.all()
            except:
                prof = Profile.objects.create(login_info=request.user)
                books = request.user.profile.favorite.all()
            typ = request.GET.get("type", "")
            total = 0
            for i in books:
                total += i.price
                i.rate, i.raters = get_avg(i)
            return render(request, "cart.html", context={
                'books': books,
                'logged': request.user.is_authenticated,
                "total": round(total, 2),
                "type": typ,
                "number": len(books),
                "super": request.user.is_superuser,
            })
        else:
            return HttpResponseRedirect(redirect_to="/login?url=/cart")


def product_details(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.rate, book.raters = get_avg(book)
    try:
        favorites = request.user.profile.favorite.all()
    except:
        favorites = []
    return render(request, "product.html", context={'book': book, 'logged': request.user.is_authenticated, 'favorites': favorites, "super": request.user.is_superuser,})


def add_to_cart(request, pk):
    if request.method == "GET":
        if request.user.is_authenticated:
            book = get_object_or_404(Book, pk=pk)
            url = request.GET.get("url", "/")
            try:
                request.user.profile.favorite.add(book)
            except:
                prof = Profile.objects.create(login_info=request.user)
                request.user.profile.favorite.add(book)
            return HttpResponseRedirect(redirect_to=url)
        else:
            return HttpResponseRedirect(redirect_to=f"/login?url=/add/{pk}")


def delete_from_cart(request, pk):
    if request.method == "GET":
        if request.user.is_authenticated:
            book = get_object_or_404(Book, pk=pk)
            request.user.profile.favorite.remove(book)
            return HttpResponseRedirect(redirect_to="/cart")
        else:
            return HttpResponseRedirect(redirect_to=f"/login?url=/delete/{pk}")


def rate_product(request, pk):
    if request.method == "POST":
        if request.user.is_authenticated:
            rate = int(request.POST.get("rateby", 0))
            book = get_object_or_404(Book, pk=pk)
            try:
                curr_rate = book.ratings.filter(user=request.user).last()
                curr_rate.rate = rate
                curr_rate.save()
            except:
                book.ratings.create(user=request.user, rate=rate)
            return HttpResponseRedirect(redirect_to=f"/product/{pk}")
        else:
            return HttpResponseRedirect(redirect_to=f"/login?url=/product/{pk}")


def checkout(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            try:
                books = request.user.profile.favorite.all()
            except:
                prof = Profile.objects.create(login_info=request.user)
                books = request.user.profile.favorite.all()
            total_price = 0
            list_books = []
            for book in books:
                total_price += book.price
                list_books.append(book.name)
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "product_data": {
                                    "name": "&&&".join(list_books),
                                },
                                "unit_amount": int(total_price) * 100,
                            },
                            "quantity": 1,
                        },
                    ],
                    mode="payment",
                    success_url=settings.SUCCESS_URL,
                    cancel_url=settings.CANCEL_URL,
                )
                return redirect(checkout_session.url)
            except:
                return redirect("/cart?message=Something went wrong, please try again later&type=failed")
        else:
            return redirect("/login?url=/cart")


def success(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            fav = request.user.profile.favorite
            fav.clear()
            return redirect("/cart?type=success")
        else:
            return HttpResponseRedirect(redirect_to="/login")


def cancel(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/cart?type=failed")
        else:
            return HttpResponseRedirect(redirect_to="/login")
