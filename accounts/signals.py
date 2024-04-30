from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from accounts.models import User, UserProfile

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        # Create userprofile after creating user
        UserProfile.objects.create(user=instance)
    else:
        try:
            # If user is updated, reflecct changes in user profile
            user_profile = UserProfile.objects.get(user=instance)
            user_profile.save()
        except:
            # If user is updated, but corresponding user profile is not present. Create user profile in this case
            UserProfile.objects.create(user=instance)

@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    print(f"User profile is being created for {instance.username}")