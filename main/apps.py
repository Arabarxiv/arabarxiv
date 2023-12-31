from django.apps import AppConfig
from django.conf import settings

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from django.contrib.auth.models import User, Group
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        import main.signals

        @receiver(post_save, sender=User)
        def add_to_default_group(sender, **kwargs):
            user = kwargs["instance"]
            if kwargs['created']:
                user.groups.add(Group.objects.get(name='default'))

        post_save.connect(add_to_default_group,
                          sender=settings.AUTH_USER_MODEL)
        
    