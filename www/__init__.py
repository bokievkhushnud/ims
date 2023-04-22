from django.apps import AppConfig


class WwwConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'www'


    def ready(self):
        import www.templatetags.custom_filters

