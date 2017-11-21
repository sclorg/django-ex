from django.conf import settings


def settings_processor(request):
    return {
        'gtm_id': settings.GTM_ID,
        'proxy_root_path': settings.FORCE_SCRIPT_NAME,
        'show_debug': settings.ENVIRONMENT in ['localdev', 'dev', 'test']
    }
