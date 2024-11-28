from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from core.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class EmailVerification:
    @staticmethod
    def generate_verification_token():
        return str(uuid.uuid4())

    @staticmethod
    def validate_email_format(email):
        """
        Validate email format using Django's built-in email validator
        """
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    @staticmethod
    def send_verification_email(user, request):
        """
        Send verification email with improved error handling and HTML email
        """
        # Validate email first
        if not EmailVerification.validate_email_format(user.email):
            raise ValueError("Invalid email format")

        # Generate token
        token = EmailVerification.generate_verification_token()
        
        # Save verification details
        user.email_verification_token = token
        user.email_verification_token_created_at = timezone.now()
        user.is_email_verified = False
        user.save()
        
        # Create verification link
        verification_link = request.build_absolute_uri(
            reverse('user:verify_email', kwargs={'token': token})
        )
        
        # Prepare email context
        email_context = {
            'user': user,
            'verification_link': verification_link,
            'site_name': settings.SITE_NAME,  # Add this to your settings
            'expiration_hours': 24
        }
        
        # Render HTML and plain text versions of the email
        html_message = render_to_string('verification_email.html', email_context)
        plain_message = strip_tags(html_message)
        
        try:
            # Send email with both HTML and plain text versions
            send_mail(
                f'Verify Your Email Address on {settings.SITE_NAME}',
                plain_message,
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            # Log the error and re-raise
            user.delete()  # Optional: remove user if email fails
            raise ValueError(f"Failed to send verification email: {str(e)}")
        
        return token

    @staticmethod
    def verify_email_token(token):
        """
        Verify email token with improved error handling
        """
        if not token:
            return False, None

        try:
            # Find user with the exact token
            user = User.objects.get(email_verification_token=token)
            
            # Check token expiration
            token_age = timezone.now() - user.email_verification_token_created_at
            if token_age > timedelta(hours=24):
                # Optionally, you could clear the token here
                user.email_verification_token = None
                user.save()
                return False, None
            
            # Mark user as verified and clear token
            user.is_email_verified = True
            user.email_verification_token = None
            user.email_verification_token_created_at = None
            user.save()
            
            return True, user
        
        except User.DoesNotExist:
            return False, None
