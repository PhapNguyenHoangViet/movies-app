import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from core.models import User


class EmailVerification:
    @staticmethod
    def generate_verification_token():
        return str(uuid.uuid4())

    @staticmethod
    def send_verification_email(user, request):
        token = EmailVerification.generate_verification_token()
        
        user.email_verification_token = token
        user.email_verification_token_created_at = timezone.now()
        user.is_email_verified = False
        user.save()
        
        verification_link = request.build_absolute_uri(
            reverse('user:verify_email', kwargs={'token': token})
        )
        
        # Compose email
        subject = 'Verify Your Email Address'
        message = f'''
        Hello {user.name},

        Please verify your email by clicking the link below:
        {verification_link}

        This link will expire in 24 hours.

        If you did not create an account, please ignore this email.

        Best regards,
        Your Movie Recommendation Team
        '''
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        return token

    @staticmethod
    def verify_email_token(token):
        try:
            user = User.objects.get(email_verification_token=token)
            
            token_age = timezone.now() - user.email_verification_token_created_at
            if token_age > timedelta(hours=24):
                return False, None
            
            user.is_email_verified = True
            user.email_verification_token = None
            user.email_verification_token_created_at = None
            user.save()
            
            return True, user
        
        except User.DoesNotExist:
            return False, None