from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Count, Avg, Sum, Min, Max
from django.db.models.functions import TruncMonth, TruncDay
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count, Avg
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import JsonResponse
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import download
from .models import MenuItem, Feedback,PasswordReset
from .forms import MenuItemForm

# Initialize NLTK components
download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# ============================================================================
# Authentication Views
# ============================================================================

def RegisterView(request):
    """
    Handle user registration with validation for username, email, and password.
    """
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_data_has_error = False

        # Validate user input
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Username already exists")

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "Email already exists")

        if len(password) < 5:
            user_data_has_error = True
            messages.error(request, "Password must be at least 5 characters")

        if user_data_has_error:
            return redirect('register')
        
        # Create new user if validation passes
        new_user = User.objects.create_user(
            email=email, 
            username=username,
            password=password
        )
        messages.success(request, "Account created. Login now")
        return redirect('login')

    return render(request, 'Registration/register.html')

def LoginView(request):
    """
    Handle user authentication and login.
    """
    request.session.pop('_messages', None)  # Clear any stored messages

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        
        messages.error(request, "Invalid login credentials")
        return redirect('login')

    return render(request, 'Login/login.html')

def LogoutView(request):
    """
    Handle user logout.
    """
    logout(request)
    return redirect('login')

# ============================================================================
# Password Reset Views
# ============================================================================

def ForgotPasswordView(request):
    """
    Handle password reset request and send reset email.
    """
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Create password reset record
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            # Generate reset URL and send email
            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})
            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
            
            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
            email_message = EmailMessage(
                'Reset your password',
                email_body,
                settings.EMAIL_HOST_USER,
                [email]
            )
            email_message.fail_silently = True
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request, 'Login/forgot_password.html')

def ResetPasswordView(request, reset_id):
    """
    Handle password reset confirmation and validation.
    """
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            passwords_have_error = False

            # Validate password reset
            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            # Check if reset link has expired (10 minutes)
            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)
            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')
                password_reset_id.delete()

            if not passwords_have_error:
                # Update password and cleanup
                user = password_reset_id.user
                user.set_password(password)
                user.save()
                password_reset_id.delete()
                
                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            
            return redirect('reset-password', reset_id=reset_id)

    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'Login/reset_password.html')
def ResetPasswordSentView(request, reset_id):
    """
    Confirmation view shown after password reset email is sent.
    """
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'Login/password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

# ============================================================================
# Feedback and Review Views
# ============================================================================

@csrf_exempt
def Feedback_view(request):
    """
    Handle customer feedback submission with sentiment analysis.
    """
    if request.method == 'POST':
        # Collect feedback data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        menu_item_id = request.POST.get('menu_item')
        message = request.POST.get('message')

        if not name or not message:
            messages.error(request, 'Name and message are required.')
            return redirect('home')

        # Create and save feedback with sentiment analysis
        menu_item = MenuItem.objects.filter(id=menu_item_id).first()
        feedback = Feedback(
            name=name,
            email=email,
            phone=phone,
            message=message,
            menu_item=menu_item
        )

        # Perform sentiment analysis using VADER
        sentiment_scores = sia.polarity_scores(message)
        feedback.review_scores = sentiment_scores['compound']
        feedback.review_sentiment = (
            "positive" if feedback.review_scores >= 0.05 else
            "negative" if feedback.review_scores <= -0.05 else
            "neutral"
        )

        feedback.save()
        messages.success(request, 'Thank you for your feedback!')
        return redirect('home')

    # Get data for display
    reviews = Feedback.objects.all()
    menu_items = MenuItem.objects.filter(is_available=True) 
    main_course_items = MenuItem.objects.filter(category="Main Course", is_available=True)

    return render(request, 'Website/index.html', {
        'reviews': reviews,
        'menu_items': menu_items,
        'main_course_items': main_course_items,
        'CATEGORY_CHOICES': MenuItem.CATEGORY_CHOICES
    })

# ============================================================================
# Admin Dashboard Views
# ============================================================================

@login_required
def Dashboard(request):
    """
    Admin dashboard view showing feedback analysis.
    """
    feedbacks = Feedback.objects.select_related('menu_item').all()

    # Aggregate feedback sentiments
    sentiment_counts = (
        Feedback.objects.values('review_sentiment')
        .annotate(count=Count('id'))
    )

    feedback_counts = {
        'positive': next((item['count'] for item in sentiment_counts if item['review_sentiment'] == 'positive'), 0),
        'negative': next((item['count'] for item in sentiment_counts if item['review_sentiment'] == 'negative'), 0),
        'neutral': next((item['count'] for item in sentiment_counts if item['review_sentiment'] == 'neutral'), 0),
    }

    return render(request, 'Admin/manage_reviews.html', {
        'feedbacks': feedbacks,
        'feedback_counts': feedback_counts,
    })
def delete_feedback(request, feedback_id):
    """
    Delete a specific feedback entry.
    """
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.delete()
    return redirect('dashboard')

@login_required
def admin_dashboard(request):
    """
    Advanced admin dashboard with statistical analysis.
    """
    # Get basic stats for display
    total_menu_items = MenuItem.objects.count()
    available_items = MenuItem.objects.filter(is_available=True).count()
    total_feedback = Feedback.objects.count()
    avg_review_score = Feedback.objects.aggregate(avg=Avg('review_scores'))['avg']
    
    context = {
        'user': request.user,
        'total_menu_items': total_menu_items,
        'available_items': available_items,
        'total_feedback': total_feedback,
        'avg_review_score': round(avg_review_score, 1) if avg_review_score else 0,
    }
    
    return render(request, 'Admin/admin_dashboard.html', context)

def get_chart_data(request):
    """
    API endpoint for dashboard charts data.
    """
    # Basic category data (already in your code)
    category_counts = MenuItem.objects.values('category').annotate(total=Count('id'))
    category_avg_reviews = Feedback.objects.values('menu_item__category').annotate(avg_score=Avg('review_scores'))
    sentiment_counts = Feedback.objects.values('review_sentiment').annotate(total=Count('id'))
    
    # Monthly feedback trend (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_feedback = (
        Feedback.objects
        .filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Format for chart.js
    months = [item['month'].strftime('%b %Y') for item in monthly_feedback]
    feedback_counts = [item['count'] for item in monthly_feedback]
    
    # Top rated menu items
    top_items = (
        Feedback.objects
        .values('menu_item__name')
        .annotate(avg_score=Avg('review_scores'))
        .filter(avg_score__isnull=False)
        .order_by('-avg_score')
        .values('menu_item__name', 'avg_score')[:5]
    )
    
    # Price distribution by category
    price_by_category = (
        MenuItem.objects
        .values('category')
        .annotate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price')
        )
        .order_by('category')
    )
    
    return JsonResponse({
        "category_counts": list(category_counts),
        "category_avg_reviews": list(category_avg_reviews),
        "sentiment_counts": list(sentiment_counts),
        "monthly_feedback": {
            "months": months,
            "counts": feedback_counts
        },
        "top_rated_items": list(top_items),
        "price_distribution": list(price_by_category)
    })

# ============================================================================
# Menu Management Views
# ============================================================================

def menu_list(request):
    """
    Display all menu items for management.
    """
    menu_items = MenuItem.objects.all()
    return render(request, 'Admin/menu_management.html', {'menu_items': menu_items})

def add_menu_item(request):
    """
    Handle creation of new menu items.
    """
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('menu_list')
    else:
        form = MenuItemForm()
    return render(request, 'Admin/menu_form.html', {'form': form})

def update_menu_item(request, item_id):
    """
    Handle updates to existing menu items.
    """
    menu_item = get_object_or_404(MenuItem, id=item_id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            form.save()
            return redirect('menu_list')
    else:
        form = MenuItemForm(instance=menu_item)
    return render(request, 'Admin/menu_form.html', {'form': form})

@csrf_exempt
def delete_menu_item(request, item_id):
    """
    Handle deletion of menu items via AJAX.
    """
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id)
        menu_item.delete()
        return JsonResponse({'message': 'Menu item deleted successfully.'}, status=200)
    return JsonResponse({'message': 'Invalid request method.'}, status=400)

def get_menu_items(request):
    """
    API endpoint to get menu items filtered by category.
    """
    category = request.GET.get('category', None)
    menu_items = MenuItem.objects.filter(category=category, is_available=True).values('id', 'name')
    return JsonResponse({'menu_items': list(menu_items)})