from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SitemapCfgConfig(AppConfig):
    #default_auto_field = 'django.db.models.BigAutoField'
    name = 'sitemap_cfg'
    verbose_name = _("Generate sitemaps from configuration")

