from django.apps import AppConfig


class MainappConfig(AppConfig):
    name = 'mainapp'


# mainapp/apps.py
# =====================================================
# APP CONFIG — Signal লোড করার জন্য
# =====================================================

from django.apps import AppConfig

class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'

    def ready(self):
        """
        Django app চালু হলে signals.py লোড হবে।
        এটি না করলে signal কাজ করবে না!
        """
        import mainapp.signals  # noqa: F401
