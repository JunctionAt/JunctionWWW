You need to create a local_config.py file that includes PORT to listen on,
and any other configs you want for your test environment:

    $ cat <<EOF> local_config.py
    > DEBUG = True
    > PORT = 9001
    > EOF

Launch as a usual flask app:

    $ sudo -u www-data python app.py
     * Running on http://127.0.0.1:9001/
     * Restarting with reloader
