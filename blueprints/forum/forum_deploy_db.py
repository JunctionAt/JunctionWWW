import datetime
from mongoengine import *
import sys
import shortuuid

if __name__ != "__main__":
    sys.exit(1)

#try:
#    host = sys.argv[1]
#    cont = sys.argv[3]
#except IndexError:
#    host = raw_input("Give me a host in the URI format: ")
#    cont = bool(raw_input("WARNING, this wipes the database, type y to continue: ") == 'y')

host = "mongodb://localhost/pf"
cont = True

if not cont:
    sys.exit(1)

forum = [
    {"category":"General",
     "desc":"Something",
     "boards":[{"board":"General Something",
                "desc":"Some Description"},
               {"board":"Something else",
                "desc":"What is this?"},
               {"board":"A third general thing",
               "desc":"Generally something else"},
        ]
    },
    {"category":"Something Minecraft",
     "desc":"A category for something",
     "boards":[
         {"board":"Minecraft blocks",
        "desc":"Blocks of minecraft"},
         {"board":"Minecraft animals",
          "desc":"Something about animals"},
         ]
    }
]



from database.boards import *
#from database.login import *
from database.categories import *
from database.forum import *
from database.posts import *
#from database.counters import *

User.drop_collection()
Forum.drop_collection()
Board.drop_collection()
Category.drop_collection()
#Counter.drop_collection()

# Install some test users.
#test_users = [User(email="test1@test.com", username="test1", active=True),
#              User(email="test2@test.com", username="test2", active=True),
#              User(email="test3@test.com", username="test3", active=True),
#              User(email="test4@test.com", username="test4", active=True),
#              User(email="test5@test.com", username="test5", active=True)]
# Hack
#[user.save() for user in test_users]

python_forum = Forum()
python_forum.save()
# Install the forum.
for category in forum:
    boards = []
    for board in category['boards']:
        boards.append(Board(name=board['board'],
            description=board['desc']))
    [board.save() for board in boards]
    cat = Category(name=category['category'],
            description=category['desc'],
            boards=boards)
    cat.save()
    python_forum.categories.append(cat)

#Counter(name="topicid").save()


python_forum.save()
