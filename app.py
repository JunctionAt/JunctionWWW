from flask import Flask

application = Flask(__name__)

application.secret_key = "WeAOcOqFruPTsb6bXKNU"

application.config.from_object("local_config")

with application.app_context():
    application.config.from_object("config")

for blueprint in application.config["BLUEPRINTS"]:
    application.register_blueprint(**blueprint)

def run():
    application.run(
        host=application.config.get('HOST', None),
        port=application.config.get('PORT', None),
        use_evalex=False)

if __name__ == "__main__": run()
