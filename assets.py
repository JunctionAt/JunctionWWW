__author__ = 'HansiHE'

from flask.ext.assets import Environment, Bundle

assets_folder = '../assets/'


def assets(app):
    environment = Environment(app)
    environment.url = "static"
    #environment.config['COMPASS_CONFIG'] = {"sass_dir": environment.directory+"../../assets/sass"}
    #print(environment.directory)

    css_main = Bundle(assets_folder+'sass/app.scss', filters='scss' if app.debug else 'scss,cssmin', depends=(assets_folder+'sass/*.scss', assets_folder+'sass/**/*.scss'), output='css/gen/main.%(version)s.css')
    environment.register('css_main', css_main)

    js_base = Bundle(assets_folder+'js/vendor/zepto.js', assets_folder+'js/foundation/foundation.js',
                     assets_folder+'js/foundation/foundation.dropdown.js',
                     assets_folder+'js/foundation/foundation.topbar.js')
    js_main = Bundle(js_base, output='js/gen/app.%(version)s.js')
    environment.register('js_main', js_main)