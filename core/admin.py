from django.contrib import admin
from .models import FriendRequest, Friendship, FriendGroup, Expense, ExpenseShare
# Register your models here.
admin.site.register(ExpenseShare)
admin.site.register(Expense)