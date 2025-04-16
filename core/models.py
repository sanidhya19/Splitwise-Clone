from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} {{self.status}}"
    

class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name='friendships1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friendships2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username} are friends"
    
    
class FriendGroup(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='friend_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Expense(models.Model):
    payer = models.ForeignKey(User, related_name='expenses_paid', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey('FriendGroup',on_delete=models.CASCADE, null=True, blank=True)
    friends = models.ManyToManyField(User, related_name='expenses_shared')
    
    
    def __str__(self):
        return f"{self.description} - {self.amount} by {self.payer}"
    

class ExpenseShare(models.Model):
    expense = models.ForeignKey(Expense, related_name='shares', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='expense_shares', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    settled = models.BooleanField(default=False)
    
    

class GroupSplit(models.Model):
    group = models.ForeignKey(FriendGroup, on_delete=models.CASCADE, related_name='splits')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owed_to')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owed_by')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    settled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    settled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user} owes {self.to_user} ₹{self.amount} in {self.group.name}"
    
    

class TransactionHistory(models.Model):
    TRANSACTION_TYPES = [
        ('expense', 'Expense'),
        ('settlement', 'Settlement')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    group = models.ForeignKey(FriendGroup, on_delete=models.CASCADE, null=True, blank=True)
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='related_transactions')
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} - {self.created_at}"
    
    