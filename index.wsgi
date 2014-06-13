import sae

from manage import app

application = sae.create_wsgi_app(app)
