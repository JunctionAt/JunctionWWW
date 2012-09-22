from flask import Flask

application = Flask(__name__)
application.config.from_object("local_config")
application.config.from_object("config")

SECRET_KEY="WeAOcOqFruPTsb6bXKNU"

for blueprint in application.config["BLUEPRINTS"]:
    application.register_blueprint(**blueprint)

if __name__ == "__main__":
    application.run(port=application.config['PORT'])
