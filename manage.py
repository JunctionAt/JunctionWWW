__author__ = 'HansiHE'

from app import application
from flask.ext.script import Manager, Server

manager = Manager(application)

manager.add_command("runserver", Server(host=application.config.get("HOST", "0.0.0.0"), port=application.config.get("PORT", 5000), use_evalex=False))

@manager.command
def bootstrap_db(confirm=False):
    """
    Puts useful stuff in the db. Good for setting up a dev environment.
    """

    if confirm is not True:
        print("IMPORTANT")
        print("This command might overwrite existing db data. "
              "Make sure you ONLY do this if you are setting up a NEW instance.")
        print("use --confirm to continue.")
        exit(-1)

    # Bootstrap forums
    from blueprints.forum.database import forum

    forum_main = forum.Forum(name="Test Forum", identifier="main").save()
    forum_category1 = forum.Category(name="Test Category 2", description="Test description #1", order=1, forum=forum_main).save()
    forum_category1_board1 = forum.Board("A Testboard", desctiption="Omg a boord", categories=[forum_category1], forum=forum_main).save()
    forum_category1_board2 = forum.Board("Another board", description="Wat", categories=[forum_category1], forum=forum_main).save()
    forum_category2 = forum.Category(name="Test Category 2", description="Test description #2", order=2, forum=forum_main).save()
    forum_category1_board1 = forum.Board("Another Testboard", description="A shitty board", categories=[forum_category2], forum=forum_main).save()

    print("Success! A basic DB is now up and running.")


@manager.option('-i', '--ip', dest="ip", default="127.0.0.1")
@manager.option('-u', '--username', dest="username", required=True)
def dev_verify_ip_username(ip, username):
    """
    Verifies a ip with a username. Useful for registering users in a dev environment without the need for a minecraft client/auth server
    """
    from blueprints.auth.user_model import ConfirmedUsername

    ConfirmedUsername(username=username, ip=ip).save()

    print("Success! You can now register the user %s from %s" % (username, ip))


@manager.command
def print_routes():
    for rule in application.url_map.iter_rules():
        print rule

if __name__ == "__main__":
    manager.run()