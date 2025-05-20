from . import models
from . import controllers
from . import hooks  # Això és correcte

def post_init_hook(cr, registry):
    from .hooks import archive_default_shop
    archive_default_shop(cr, registry)
