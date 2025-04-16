from django import forms
from .models import Expense, Friendship
from django.contrib.auth.models import User
from django.db import models


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'group', 'friends']
        
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop(user)
        super(ExpenseForm,self).__init__(*args, **kwargs)
        
        friendships = Friendship.objects.filter(models.Q(user1=user) | models.Q(user2=user))
        friend_ids = set()
        for f in friendships:
            friend_ids.add(f.user1.id)
            friend_ids.add(f.user2.id)
        friend_ids.discard(user.id)

        self.fields['friends'].queryset = User.objects.filter(id__in=friend_ids)
