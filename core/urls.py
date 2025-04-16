from django.urls import path
from .views import HomeView, LoginView, LogoutView, DashboardView, RegisterView, send_friend_request, handle_friend_request,list_friends, search_users,create_group, group_detail, delete_group, add_expense, add_group_expense, calculate_group_split, clear_all_transactions, clear_group_splits, settle_expense, transaction_history
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', HomeView, name='home'),
    path('login/', LoginView, name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', RegisterView, name='register'),
    path('dashboard/', DashboardView, name='dashboard'),
    path('send_friend_request/<int:receiver_id>/', send_friend_request, name='send_friend_request'),
    path('handle_friend_request/<int:request_id>/<str:action>/', handle_friend_request, name='handle_friend_request'),
    path('search/', search_users, name='search_users'),
    path('friends/', list_friends, name='friends_list'),
    path("create-group/", create_group, name="create_group"),
    path('groups/<int:group_id>/add_expense/', add_group_expense, name='add_group_expense'),
    path('group/<int:group_id>/calculate_split/', calculate_group_split, name='calculate_group_split'),
    path("group/<int:group_id>/", group_detail, name="group_detail"),
    path('delete-group/<int:group_id>/', delete_group, name='delete_group'),
    path('add-expense/', add_expense, name='add_expense'),
    path('logout/', LogoutView, name='logout'),
    path('clear-all-transactions/', clear_all_transactions, name='clear_all_transactions'),
    path('group/<int:group_id>/clear_splits/', clear_group_splits, name='clear_group_splits'),
    path('settle/<int:share_id>/', settle_expense, name='settle_expense'),
    path('history/', transaction_history, name='transaction_history')

]
