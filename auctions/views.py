from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.contrib import messages # imports messages

from .models import User, Listing, Category
from .forms import BidForm, CommentForm, NewListingForm

# Homepage
def index(request):
    return render(request, "auctions/index.html",{"listings": Listing.objects.filter(active=True)})

# Page that shows lists of categories available on the website
def categories(request):
    return render(request, "auctions/categories.html", {"categories": Category.objects.all().order_by('category_name')})

def category(request, category_id):
    return render(request, "auctions/category.html", {
        "category": Category.objects.get(pk=category_id),
        "listings": Listing.objects.filter(active=True, listing_category=category_id)})

@login_required(login_url='login')
def newlisting(request):

    if request.method =="POST":

        form = NewListingForm(request.POST)

        if form.is_valid():
            form.instance.author = request.user
            new_listing = form.save()
            return HttpResponseRedirect(reverse("listing",args=(new_listing.pk,)))

    else:
        form = NewListingForm()

    return render(request, "auctions/newlisting.html", {
        "form": form
    })        

def listing(request, listing_id):

    # Looks up relevant information from database to load the page
    listing = Listing.objects.get(pk=listing_id)
    comments = listing.comments.all()
    total_comments = comments.count()

    # Sets variable telling us if in user's watchlist
    if request.user.is_authenticated:
        is_in_watchlist = listing.is_in_watchlist(request.user)
    else:
        is_in_watchlist = False


    return render(request, "auctions/listing.html", {
        "listing": listing,
        "form": BidForm(),
        "comment_form": CommentForm(),
        "listing_id": listing_id,
        "comments": comments,
        "total_comments": total_comments,
        "is_in_watchlist": is_in_watchlist,
        "user": request.user
    })

@login_required(login_url='login')
def add_bid(request, listing_id):
    if request.method == "POST":

        listing = Listing.objects.get(pk=listing_id)

        form = BidForm(request.POST)
        # Checks if form is valid (server-side)
        if form.is_valid():
            
            # Sets user and item fields in Model
            form.instance.user = request.user
            form.instance.item = listing

            if form.instance.amount > listing.current_price():
                
                
                form.save()

                # Success message gets output
                messages.success(request, "The bid is successfully added.")

                # Page is reloaded
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

            else:
                # Error message gets output
                messages.error(request, "Your bid needs to be higher than the current price!!!")

                # Page is reloaded
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required(login_url='login')
def add_comment(request, listing_id):
    if request.method == 'POST':
        
        listing = Listing.objects.get(pk=listing_id)

        form = CommentForm(request.POST)

        if form.is_valid():

            form.instance.user = request.user
            form.instance.item = listing

    
            form.save()

            messages.success(request, "Comment successfully added.")

            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(login_url='login')
def changewatchlist(request, listing_id):
    if request.method == "POST":
        
        # Info for user and listing
        user = request.user
        listing = Listing.objects.get(pk=listing_id)

        # If the user has this on their watchlist, remove it.
        if listing.is_in_watchlist(user):
            listing.watched_by.remove(user)
        # If the user doesn't have listing on their watchlist, add it.
        else:
            user.watchlist.add(listing)

        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(login_url='login')
def watchlistremove(request, listing_id):
    if request.method == "POST":
        user = request.user
        listing = Listing.objects.get(pk=listing_id)

        listing.watched_by.remove(user)
        # Success message that will show
        messages.success(request, "Listing removed from watchlist!!!")

        return HttpResponseRedirect(reverse("watchlist"))

@login_required(login_url='login')
def close(request, listing_id):
    if request.method == "POST" and Listing.objects.get(pk=listing_id).author == request.user:
        
        Listing.objects.filter(pk=listing_id).update(active=False)

        messages.success(request, "Auction successfully closed!")
        return redirect('/')

    else:
        return render(request, "auctions/error.html", {
            "message": "You are not verified to do this."
        })

@login_required(login_url='login')
def watchlist(request):

    return render(request, "auctions/watchlist.html",{
        "watchlist": request.user.watchlist.all()
    })

def login_view(request):

        if request.method == "POST":

            # Attempt to sign user in
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                messages.error(request, "Invalid username and/or password")
                return HttpResponseRedirect(reverse("login"))

        else:
            return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
