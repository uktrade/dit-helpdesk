from .development import *

READ_ONLY = env.bool("READ_ONLY", True)
if READ_ONLY:
    INSTALLED_APPS += ["readonly"]
    SITE_READ_ONLY = True

CMS_ENABLED = env.bool("CMS_ENABLED", False)
if CMS_ENABLED:
    INSTALLED_APPS += ["cms"]
