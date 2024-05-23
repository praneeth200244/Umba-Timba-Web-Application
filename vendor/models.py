from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification_email
from datetime import datetime, time, date


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

    def is_open(self):
        current_date = date.today()
        week_day = current_date.isoweekday()
        current_business_hours = OpeningHour.objects.filter(vendor=self, day=week_day)
        
        current_time = datetime.now().strftime("%H:%M:%S")

        is_operational = False
        for i in current_business_hours:
            if not i.is_closed:
                open_time = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                close_time = str(datetime.strptime(i.to_hour, "%I:%M %p").time())

                if open_time <= current_time <= close_time:
                    is_operational = True
                    break
        return is_operational

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
                        'to_email' : self.user.email,
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

DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

HOURS_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0,24) for m in (0,30)]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True, null=True)
    to_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True, null=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()