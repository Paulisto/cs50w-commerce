from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max

class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=300)

    def __str__(self):
        return self.category_name
    
    # Orders category names in alphabetical order
    class Meta:
        ordering = ['category_name']

class Listing(models.Model):
    listing_name = models.CharField(max_length=350)
    listing_description = models.TextField(max_length=1000)
    listing_image = models.URLField(max_length=1000, null=True, blank=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    listing_category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default='', blank=True, null=True)
    active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    created_on = models.DateTimeField(auto_now_add=True)
    watched_by = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def __str__(self):
        return f"{self.listing_name}"

    # Returns the total number of bids on the listing
    def no_of_bids(self):
        return self.bids.all().count()

    # Works out the current highest bid or if there are no bids, the starting price
    def current_price(self):
        if self.no_of_bids() > 0:
            return round(self.bids.aggregate(Max('amount'))['amount__max'],2)
        else:
            return self.starting_bid

    # Tells us who is currently winning the listing
    def current_winner(self):
        if self.no_of_bids() > 0:
            return self.bids.get(amount=self.current_price()).user
        else:
            return None

    # Tells us if it's in the watchlist
    def is_in_watchlist(self, user):
        return user.watchlist.filter(pk=self.pk).exists()

    # Orders listings by most recent first
    class Meta:
        ordering = ['-created_on']

class Bid(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.IntegerField()

    def __str__(self):
        return str(self.amount)

class Comment(models.Model):
    comment = models.TextField(max_length=3000)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.comment)

        # Ordering comments by most recent first
        class Meta:
            ordering = ['-comment_time']