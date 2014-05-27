# Junction.at WWW
How to get a local dev environment for the Junction.at website up and running... *For Dummies*

## New way with Vagrant

 * Install VirtualBox
 * Install Vagrant
 * Navigate to the root of this project, run 'vagrant up'
 * Sit back and enjoy while your vm is being downloaded and set up
 * When it's done, type 'vagrant ssh' to get a shell
 * Cd to ~/www-src/
 * Run 'python2 manage.py runserver'
 * Done!

## First steps
Make sure you have everything installed. Best to do this in a virtualenv so you don't have to install Python packages globally. Of course, we're assuming you already have Python, pip, and virtualenv installed. You do, right? Right?

    $ pip install -r requirements.txt

Also, make sure you have MongoDB installed.

    # apt-get install mongodb

## Running locally
Most everything is handled by the amazing `manage.py` Python script.

### Database
First, you should create a database.

    $ python manage.py bootstrap_db

Of course, just doing that will scream at you to let you know **you will overwrite data**. Adding --confirm as an option will let it know that, yes, you've read that.

    $ python manage.py bootstrap_db --confirm

### Local configuration
Well, that's over. Now we can continue on to making your local configuration, which is stored in `config/local_config.py`.

    $ cp config/local_config.py.default config/local_config.py
    $ nano config/local_config.py

The local config is defaulted to run on all hosts on port 8080. That's easily changeable, as you can see in the file. Also, API keys, etc. aren't stored in that file. You'll have to supply your own for dev.

Well, you're done staring at that now. Let's continue.

### Running the damn thing.
Now you're almost there! Almost to the finish line! Come on, you can do it!

    $ python manage.py runserver

Yes, it's that easy. But wait, you can't log in!

### Making a user without a MC auth server.
Now that you have it running, you can register at http://your.host.here/register/

Of course, you don't have the Junction.at MC auth server set up on your own server, so you can't. But wait! There's a workaround. You'll need a username, preferrably your MC one, and your IP if you're not running the website locally.

    $ python manage.py dev_verify_ip_username -u <username>

If not running it locally:

    $ python manage.py dev_verify_ip_username -u <username> -i <ip_addr>

There you go, you've verified your account!

Have fun!