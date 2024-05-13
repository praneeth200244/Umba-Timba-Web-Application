from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification_email

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='user_profile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=100)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name
    
    def save(self, *args, **kwargs):
        # If is_approved status is updated
        if self.pk is not None:
            original_status = Vendor.objects.get(pk=self.pk)
            if original_status.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                        'user':self.user,
                        'is_approved':self.is_approved,
                }
                if self.is_approved == True:
                    # Send Notification Email
                    mail_subject = 'Congratulations...!Your account has been approved'
                    send_notification_email(mail_subject, mail_template, context)
                else:
                    # Send notification Email
                    mail_subject = 'We regret to inform you that you do not meet the criteria to list your food menu on our marketplace'
                    send_notification_email(mail_subject, mail_template, context) 
        return super(Vendor, self).save(*args, **kwargs)
