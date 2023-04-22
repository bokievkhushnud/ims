from django.urls import path
from . import views


# url maps for www app
urlpatterns = [
    path('', views.homeView, name='home'),

    # Assets url
    path('items/', views.items, name='items'),
    path('item/detail/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/add/', views.add_item, name='add_item'),
    path('update/<int:pk>/', views.update, name='update_items'),
    path('update_consumabe/<int:pk>/', views.update_consumables, name='update_consumable'),



    path('accessories/add', views.add_accessory, name='add_accessories'),
    path('consumables/add', views.add_consumable, name='add_consumables'),
    path('checkout/<int:pk>', views.checkout_items, name='checkout_items'),
    path('checkin/<int:pk>', views.checkin_items, name='checkin_items'),

    # Bulk delete
    path('delete', views.delete_items, name="bulk_delete"),
    path('delete/<int:pk>/', views.delete_items, name="bulk_delete"),
    path('checkout/', views.checkout_items, name="checkout_items"),
    path('print_qr/', views.print_qr, name="print_qr"),
    path('print_qr/<int:pk>/', views.print_qr, name="print_qr"),
    path('generate_pdf/', views.generate_pdf, name="generate_pdf"),
    path('login/', views.auth, name="login"),



    # Registration
    path('register', views.register, name='register'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path("password_change", views.password_change, name="password_change"),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm, name='password_reset_confirm'),
    path('logout_user',views.logout_user, name="logout"),


    # profile page
    path('profile/',views.profilePage, name="profile"),
    path('broken/<int:pk>/', views.item_outoforder, name="broken"),
    path('fix/<int:pk>/', views.item_fixed, name="fix"),
    path('reports/',views.reportPage, name="reports"),
    path('get_monthly_added_items/<int:year>/', views.get_monthly_added_items_data, name='get_monthly_added_items'),

    # loans
    path('loans/',views.loans, name="loans"),


    # categories
    path('categories/',views.categories, name="categories" ),
    path('category/delete/<int:pk>/',views.categories_delete, name="delete_category" ),
    path('category/update/<int:pk>/',views.categories_update, name="update_category" ),





    

]