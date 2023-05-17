from django import forms

from .models import Category, Bid, Comment, Listing

# Model form for new listing
class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['listing_name', 'listing_description', 'starting_bid', 'listing_image', 'listing_category']
        widgets = {
            'listing_name': forms.TextInput(attrs={'class':'form-control'}),
            'listing_description': forms.Textarea(attrs={'rows':2, 'max-length': 3000, 'class':'form-control'}),
            'starting_bid': forms.NumberInput(attrs={'class':'form-control'}),
            'listing_image': forms.URLInput(attrs={'class':'form-control'}),
            'listing_category': forms.Select(attrs={'class':'form-control'})
        }

        labels = {
            'listing_image': 'Insert image URL'
        }

# Model form for placing new bid on a listing
class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class':'form-control'})
        }

        labels = {
            'amount': 'Enter new bid'
        }
    
# Modal form for a new comment on a listing
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows':2, 'max-length': 5000, 'class':'form-control'})
        }

        labels = {
            'message': 'Insert comment'
        }