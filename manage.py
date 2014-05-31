from flask_script import Manager, Server
from models import forum_model, ban_model
from app import application


manager = Manager(application)

manager.add_command("runserver", Server(host=application.config.get("HOST", "0.0.0.0"), port=application.config.get("PORT", 5000), use_evalex=application.config.get("DEBUG_PYTHON_SHELL")))


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

    forum_main = forum_model.Forum(name="Test Forum", identifier="main").save()
    forum_category1 = forum_model.Category(name="Test Category 1", description="Test description #1", order=1, forum=forum_main).save()
    forum_category1_board1 = forum_model.Board("A Testboard", desctiption="Omg a boord", categories=[forum_category1], forum=forum_main).save()
    forum_category1_board2 = forum_model.Board("Another board", description="Wat", categories=[forum_category1], forum=forum_main).save()
    forum_category2 = forum_model.Category(name="Test Category 2", description="Test description #2", order=2, forum=forum_main).save()
    forum_category1_board1 = forum_model.Board("Another Testboard", description="A shitty board", categories=[forum_category2], forum=forum_main).save()

    print("Success! A basic DB is now up and running.")


@manager.option('-i', '--ip', dest="ip", default="127.0.0.1")
@manager.option('-u', '--username', dest="username", required=True)
@manager.option('-d', '--uuid', dest="uuid", required=True)
def dev_verify_ip_username(ip, username, uuid):
    """
    Verifies a ip with a username. Useful for registering users in a dev environment without the need for a Minecraft client/auth server.
    """
    from models.user_model import ConfirmedUsername

    ConfirmedUsername(username=username, ip=ip, uuid=uuid).save()

    print("Success! You can now register the user %s, %s from %s" % (username, uuid, ip))


@manager.command
def print_routes():
    for rule in application.url_map.iter_rules():
        print rule, rule.endpoint


@manager.option('-b', dest="ban_id", required=True)
def destroy_ban(ban_id):
    ban = ban_model.Ban.objects(uid=int(ban_id)).first()

    if ban is None:
        print("ban not found")
        return

    appeal = ban.appeal

    if appeal is not None:
        print("ban has appeal")
        replies = appeal.replies
        for reply in replies:
            reply.delete()
        appeal.delete()
    else:
        print("ban does not have appeal")

    ban.delete()

    print("ban deleted")


@manager.option('-u', dest="username", required=True)
@manager.option('-r', dest="role", required=True)
def add_role(username, role):
    from models.user_model import User

    user = User.objects(name=username).first()
    if user is None:
        print("no user was found with that name")

    user.roles.append(role)
    user.save()

    print("success!")

if __name__ == "__main__":
    manager.run()
