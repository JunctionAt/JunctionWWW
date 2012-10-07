You need to create a local_config.py file that includes PORT to listen on, SQLALCHEMY_DATABASE_URI for a mysql connection string,
and any other configs you want for your test environment:

    $ cat <<EOF> local_config.py
    > DEBUG = True
    > PORT = 9001
    > SQLALCHEMY_DATABASE_URI = 'mysql://wiggitywhack:wiggitywhack@localhost/wiggitywhack'
    > EOF


If you want to create all the tables (at least the ones wiggity has added models for):

    $ python
    >>> import app
    >>> from blueprints.base import db
    >>> db.create_all()


Launch as a usual flask app:

    $ python app.py
     * Running on http://127.0.0.1:9001/
     * Restarting with reloader
