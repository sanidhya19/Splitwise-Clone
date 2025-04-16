from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required
from .models import FriendRequest, Friendship, FriendGroup, Expense, ExpenseShare, GroupSplit, TransactionHistory
from .forms import ExpenseForm
from django.db.models import Sum
from django.db import models
from decimal import Decimal
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone



# Create your views here.

def HomeView(request):
    return render(request,'home.html')


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return{
        'refresh':str(refresh),
        'access':str(refresh.access_token)
    }

def LoginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            tokens = get_tokens_for_user(user)
            
            request.session['access_token']  = tokens['access']
            request.session['refresh_token'] = tokens['refresh']
            
            messages.success(request, "Login successful")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
        
    return render(request, 'login.html')

def RegisterView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
       
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')
        
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
        user.save()
        
        login(request, user)
        tokens = get_tokens_for_user(user)
        request.session['access_token']  = tokens['access']
        request.session['refresh_token'] = tokens['refresh']
        return redirect("dashboard") if user.is_authenticated else redirect("login")

    return render(request, 'register.html')
    

@login_required
def DashboardView(request):
    pending_requests = FriendRequest.objects.filter(receiver=request.user, status="pending")

    sent = FriendRequest.objects.filter(sender=request.user, status="accepted").values_list('receiver', flat=True)
    received = FriendRequest.objects.filter(receiver=request.user, status="accepted").values_list('sender', flat=True)
    friends_id = list(sent) + list(received)
    friends = User.objects.filter(id__in=friends_id)

    user_groups = FriendGroup.objects.filter(members=request.user)

    # Get all shares where user is involved
    shares = ExpenseShare.objects.filter(
        models.Q(user=request.user) | models.Q(expense__payer=request.user),
        settled=False
    ).select_related('expense', 'user', 'expense__payer', 'expense__group')

    # Categorize debts correctly
    you_owe = []
    you_are_owed = []
    
    for share in shares:
        # Skip shares where user is both payer and participant
        if share.user == share.expense.payer:
            continue

        # User is part of the expense participants
        if share.user == request.user:
            if share.amount < 0:  # Negative balance means user owes
                you_owe.append({
                    'amount': abs(share.amount),
                    'to_user': share.expense.payer,
                    'expense': share.expense,
                    'is_group': share.expense.group is not None,
                    'share_id': share.id  
                })
            elif share.amount > 0:  # Positive balance means user is owed
                you_are_owed.append({
                    'amount': share.amount,
                    'from_user': share.expense.payer,
                    'expense': share.expense,
                    'is_group': share.expense.group is not None,
                    'share_id': share.id 
                })
        
        # User is the payer and others owe them
        elif share.expense.payer == request.user:
            if share.amount < 0:  # Negative amount means others owe the payer
                you_are_owed.append({
                    'amount': abs(share.amount),
                    'from_user': share.user,
                    'expense': share.expense,
                    'is_group': share.expense.group is not None,
                    'share_id': share.id  
                })

    # Calculate totals (with default 0 if lists are empty)
    you_owe_total = sum(item['amount'] for item in you_owe) if you_owe else 0
    you_are_owed_total = sum(item['amount'] for item in you_are_owed) if you_are_owed else 0
    total_balance = you_are_owed_total - you_owe_total

    return render(request, 'dashboard.html', {
        'pending_requests': pending_requests,
        'user_groups': user_groups,
        'friends': friends,
        'you_owe_total': round(you_owe_total, 2),
        'you_are_owed_total': round(you_are_owed_total, 2),
        'total_balance': round(total_balance, 2),
        'you_owe': you_owe,
        'you_are_owed': you_are_owed
    })

    

def send_friend_request(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)

    # Check if the request already exists
    if FriendRequest.objects.filter(sender=request.user, receiver=receiver, status="pending").exists():
        messages.error(request, "Friend request already sent!")
        return redirect('dashboard')

    FriendRequest.objects.create(sender=request.user, receiver=receiver)
    messages.success(request, f"Friend request sent to {receiver.username}")
    return redirect('dashboard')


@login_required
def handle_friend_request(request, request_id, action):
    friend_request = get_object_or_404(FriendRequest, id=request_id, status="pending")

    if friend_request.receiver != request.user:
        messages.error(request, "You cannot respond to this request!")
        return redirect('dashboard')

    if action == "accept":
        Friendship.objects.create(user1=friend_request.sender, user2=friend_request.receiver)
        friend_request.status = "accepted"
        friend_request.save()
        messages.success(request, f"You are now friends with {friend_request.sender.username}")
    elif action == "reject":
        messages.info(request, f"You rejected {friend_request.sender.username}'s request.")
        friend_request.delete()

    return redirect('dashboard')

def search_users(request):
    query = request.GET.get('q', '')  # Get search query from URL
    users = User.objects.filter(username__icontains=query) if query else []
    
    return render(request, 'search_results.html', {'users': users, 'query': query})


@login_required
def list_friends(request):
    friends = Friendship.objects.filter(user1=request.user) | Friendship.objects.filter(user2=request.user)
    friend_list = [friend.user1 if friend.user2 == request.user else friend.user2 for friend in friends]

    return render(request, 'friends_list.html', {'friends': friend_list})


def create_group(request):
    if request.method == "POST":
        name = request.POST.get("name")
        selected_friends = request.POST.getlist("friends")
        
        if not name:
            messages.error(request, "Group name is required")
            return redirect('dashboard')
        
        group = FriendGroup.objects.create(name=name)
        group.members.add(request.user)
        
        for friend_id in selected_friends:
            friend = User.objects.get(id=friend_id)
            group.members.add(friend)

        group.save()
        messages.success(request, "Group created successfully!")
        return redirect("dashboard")

    friendships = Friendship.objects.filter(user1=request.user) | Friendship.objects.filter(user2=request.user)
    friends = [f.user1 if f.user2 == request.user else f.user2 for f in friendships]

    return render(request, "create_group.html", {"friends": friends})


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(FriendGroup, id=group_id)

    if request.user not in group.members.all():
        messages.error(request, "You are not a member of this group.")
        return redirect("dashboard")

    # Get all group splits (both settled and unsettled)
    # Change this line if you only want unsettled splits:
    # splits = GroupSplit.objects.filter(group=group, settled=False)
    splits = GroupSplit.objects.filter(group=group)
    
    # Debug information
    print(f"Group: {group.name}, Split count: {splits.count()}")
    
    user_owes = splits.filter(from_user=request.user)
    user_is_owed = splits.filter(to_user=request.user)
    
    print(f"User owes count: {user_owes.count()}")
    print(f"User is owed count: {user_is_owed.count()}")
    
    group_expenses = Expense.objects.filter(group=group).prefetch_related('shares', 'payer')

    return render(request, 'group_detail.html', {
        'group': group,
        'splits': splits,
        'user_owes': user_owes, 
        'user_is_owed': user_is_owed,
        'group_expenses': group_expenses,
    })

    
    
@login_required
def calculate_group_split(request, group_id):
    group = get_object_or_404(FriendGroup, id=group_id)

    if request.method == "POST":
        members = list(group.members.all())
        member_map = {member.id: member for member in members}
        member_ids = list(member_map.keys())

        paid = {uid: Decimal('0.00') for uid in member_ids}
        total_group_expense = Decimal('0.00')

        # Sum actual contributions from ExpenseShare
        for expense in Expense.objects.filter(group=group):
            total_group_expense += expense.amount
            for share in ExpenseShare.objects.filter(expense=expense):
                user_id = share.user.id
                paid[user_id] += (share.amount + (expense.amount / len(members)))

        if total_group_expense == 0 or not members:
            messages.warning(request, "No expenses found for this group or no members in group.")
            return redirect('group_detail', group_id=group.id)

        equal_share = total_group_expense / len(members)

        # Calculate net balances
        net_balance = {
            uid: (paid[uid] - equal_share).quantize(Decimal('0.01'))
            for uid in member_ids
        }

        GroupSplit.objects.filter(group=group).delete()

        owes = [(uid, -bal) for uid, bal in net_balance.items() if bal < 0]
        gets = [(uid, bal) for uid, bal in net_balance.items() if bal > 0]

        owes.sort(key=lambda x: x[1], reverse=True)
        gets.sort(key=lambda x: x[1], reverse=True)

        SMALL_AMT = Decimal('0.01')
        i = j = 0

        while i < len(owes) and j < len(gets):
            owe_id, owe_amt = owes[i]
            get_id, get_amt = gets[j]

            transfer = min(owe_amt, get_amt)

            if transfer >= SMALL_AMT:
                GroupSplit.objects.create(
                    group=group,
                    from_user=member_map[owe_id],
                    to_user=member_map[get_id],
                    amount=transfer
                )

            owes[i] = (owe_id, (owe_amt - transfer).quantize(Decimal('0.01')))
            gets[j] = (get_id, (get_amt - transfer).quantize(Decimal('0.01')))

            if owes[i][1] <= SMALL_AMT:
                i += 1
            if gets[j][1] <= SMALL_AMT:
                j += 1

        messages.success(request, "Splits calculated successfully.")
        return redirect('group_detail', group_id=group.id)

    return redirect('group_detail', group_id=group.id)

@login_required
@transaction.atomic
def add_group_expense(request, group_id):
    if request.method == "POST":
        group = get_object_or_404(FriendGroup, id=group_id)
        description = request.POST.get("description")
        total_amount = Decimal(request.POST.get("amount"))
        
        # Track actual payments from all members
        contributions = {}
        total_contributed = Decimal('0.00')
        for member in group.members.all():
            amount_paid = Decimal(request.POST.get(f"paid_{member.id}", '0.00'))
            if amount_paid > 0:
                contributions[member] = amount_paid
                total_contributed += amount_paid

        # Validate total contributions match expense amount
        if abs(total_contributed - total_amount) > Decimal('0.01'):
            messages.error(request, "Total contributions don't match expense amount")
            return redirect('group_detail', group_id=group.id)

        # Find main payer (who paid the most)
        main_payer = max(contributions.items(), key=lambda x: x[1], default=(None, 0))[0]
        
        # Create expense with actual main payer
        expense = Expense.objects.create(
            group=group,
            description=description,
            amount=total_amount,
            payer=main_payer
        )

        # Calculate equal share per member
        num_members = group.members.count()
        share_amount = total_amount / num_members

        # Create main expense history record for the payer
        TransactionHistory.objects.create(
            user=main_payer,
            transaction_type='expense',
            amount=total_amount,
            group=group,
            description=description
        )

        # Create shares showing net balance for each member
        for member in group.members.all():
            paid = contributions.get(member, Decimal('0.00'))
            net_balance = paid - share_amount
            
            ExpenseShare.objects.create(
                expense=expense,
                user=member,
                amount=net_balance.quantize(Decimal('0.01'))
            )
            
            # Create history record for each participant
            if member != main_payer:
                TransactionHistory.objects.create(
                    user=member,
                    transaction_type='expense',
                    amount=-share_amount.quantize(Decimal('0.01')),
                    group=group,
                    description=f"Share of {description}",
                    related_user=main_payer
                )

        messages.success(request, "Expense added successfully!")
        return redirect('group_detail', group_id=group.id)
    
    return redirect('group_detail', group_id=group_id)
    


@login_required
def delete_group(request, group_id):
    group = get_object_or_404(FriendGroup, id=group_id)

    if request.user in group.members.all():
        group.delete()
        messages.success(request, "Group deleted successfully!")
    else:
        messages.error(request, "You are not allowed to delete this group.")

    return redirect('dashboard')


def get_friends(user):
    friendships = Friendship.objects.filter(models.Q(user1=user) | models.Q(user2=user))
    friends = []
    for friendship in friendships:
        if friendship.user1 == user:
            friends.append(friendship.user2)
        else:
            friends.append(friendship.user1)
    return friends


@login_required
def add_expense(request):
    if request.method == "POST":
        description = request.POST.get("description")
        amount = float(request.POST.get("amount"))
        friend_ids = request.POST.getlist("friends")

        if amount <= 0 or not friend_ids:
            messages.error(request, "Invalid amount or no friends selected.")
            return redirect('add_expense')

        payer = request.user
        friends = User.objects.filter(id__in=friend_ids)
        total_people = len(friends) + 1
        share_per_person = amount / total_people

        expense = Expense.objects.create(
            description=description,
            amount=amount,
            payer=payer
        )
        expense.friends.set(friends)
        
        TransactionHistory.objects.create(
            user=request.user,
            amount=amount,
            description=description,
            group=expense.group
        )
        
        for friend in friends:
            TransactionHistory.objects.create(
                user=friend,
                amount=share_per_person,
                description=f"Share of {description}",
                group=expense.group,
                related_user=payer
            )

        # Create shares with proper net balances
        # Payer's share: total paid - their fair share
        ExpenseShare.objects.create(
            expense=expense,
            user=payer,
            amount=round(amount - share_per_person, 2)
        )

        # Friends' shares: 0 paid - their fair share
        for friend in friends:
            ExpenseShare.objects.create(
                expense=expense,
                user=friend,
                amount=round(-share_per_person, 2)
            )

        messages.success(request, "Expense added and split successfully!")
        return redirect('dashboard')

    friends = get_friends(request.user)
    return render(request, "add_expense.html", {"friends": friends})




def LogoutView(request):
    request.session.flush()
    logout(request)
    messages.success(request,"Logout successful")
    return redirect('home')


@login_required
def clear_all_transactions(request):
    user = request.user

    # Delete expenses where user is payer
    Expense.objects.filter(payer=user).delete()

    # Delete shares where user was involved as a friend
    ExpenseShare.objects.filter(user=user).delete()

    messages.success(request, "All your transactions have been cleared.")
    return redirect('dashboard')


def clear_group_splits(request, group_id):
    group = get_object_or_404(FriendGroup, id=group_id)

    if request.method == 'POST':
        GroupSplit.objects.filter(group=group).delete()
        messages.success(request, 'All transactions have been cleared!')
    
    return redirect('group_detail', group_id=group.id)


@login_required
@transaction.atomic
def settle_expense(request, share_id):
    share = get_object_or_404(ExpenseShare, id=share_id)
    
    # Validate user can settle this
    if request.user != share.expense.payer and request.user != share.user:
        messages.error(request, "You can't settle this expense")
        return redirect('dashboard')
    
    share.settled = True
    share.save()

    # Handle group settlements
    if share.expense.group:
        # Update GroupSplit
        GroupSplit.objects.filter(
            group=share.expense.group,
            from_user=share.user,
            to_user=share.expense.payer,
            amount=abs(share.amount)
        ).update(settled=True)

    # Create/update TransactionHistory records
    TransactionHistory.objects.update_or_create(
        user=request.user,
        description=f"Settled: {share.expense.description}",
        defaults={
            'transaction_type': 'settlement',
            'amount': -abs(share.amount),
            'group': share.expense.group,
            'related_user': share.expense.payer,
            'settled_at': timezone.now()
        }
    )

    TransactionHistory.objects.update_or_create(
        user=share.expense.payer,
        description=f"Received settlement for {share.expense.description}",
        defaults={
            'transaction_type': 'settlement',
            'amount': abs(share.amount),
            'group': share.expense.group,
            'related_user': request.user,
            'settled_at': timezone.now()
        }
    )
    
    messages.success(request, f"Successfully settled ₹{abs(share.amount)}")
    return redirect('dashboard')

@login_required
def transaction_history(request):
    history = TransactionHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transaction_history.html', {'history': history})


