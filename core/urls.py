from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 🏠 Home page
    path('', views.home, name='home'),

    # 🔐 Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 👥 Registration
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/lawyer/', views.register_lawyer, name='register_lawyer'),

    # 👤 Profile & Subscription
    path('profile/', views.profile, name='profile'),
    path('lawyer/subscribe/', views.lawyer_subscribe, name='lawyer_subscribe'),

    # ⚖️ Lawyers listing & details
    path('lawyers/', views.lawyer_list, name='lawyer_list'),
    path('lawyers/<int:pk>/', views.lawyer_detail, name='lawyer_detail'),
    path('lawyers/<int:pk>/start-chat/', views.start_chat_with_lawyer, name='start_chat_with_lawyer'),

    # ❓ General & Customer Questions
    path('general-questions/', views.general_questions, name='general_questions'),
    path('questions/', views.customer_questions_list, name='customer_questions_list'),
    path('questions/new/', views.create_customer_question, name='create_customer_question'),
    path('questions/<int:pk>/answer/', views.lawyer_answer_customer_question, name='lawyer_answer_customer_question'),

    # 💬 Chat & Payment
    path('chat/<int:chat_id>/', views.chat_view, name='chat_view'),
    path('payment/<int:chat_id>/', views.payment_view, name='payment_view'),

    # 💳 Stripe webhook (for real payments later)
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
