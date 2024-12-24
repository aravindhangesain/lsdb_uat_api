from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    # I want to use the built in staff and superusers for control
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notes = models.TextField(max_length=500, null=True, blank=True)
    registration_comment = models.CharField(max_length=128, null=True, blank=True)
    administration_comment = models.CharField(max_length=128, null=True, blank=True)
    user_registration_status = models.ForeignKey('UserRegistrationStatus', on_delete=models.CASCADE, null=False,
                                                 blank=False)
    allowed_templates = models.ManyToManyField('Template', blank=True)
    birth_date = models.DateField(null=True, blank=True)
    box_user = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        ordering = ('user',)

    def __str__(self):
        return "{}".format(self.user)

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         # registration = UserRegistrationStatus.objects.get(pk=1)
#         UserProfile.objects.create(user=instance,
#             # user_registration_status=registration
#             )
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()
