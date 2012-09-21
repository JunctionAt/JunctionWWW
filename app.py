from flask import Flask, render_template

application = Flask(__name__, template_folder="templates")
application.debug = True

@application.route('/')
def index():
    return render_template('index.html')
