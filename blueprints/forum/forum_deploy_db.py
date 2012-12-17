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
     "desc":"The general category for all questions.",
     "boards":[{"board":"Python General",
                "desc":"General discussions related to Python.",
                "board_id":shortuuid.uuid()},
               {"board":"Python Scripts",
                "desc":"Links to Python scripts.",
                "board_id":shortuuid.uuid()},
               {"board":"Python Jobs",
               "desc":"Forum to require and offer python jobs. Are you searching for python developers to make or complete your python script ? This place is for you.",
               "board_id":shortuuid.uuid()},
        ]
    },
    {"category":"Python Coding",
     "desc":"The category for all coding questions to do with Python",
     "boards":[{"board":"Beginners..",
                "desc":"..just learning Python",
                "board_id":shortuuid.uuid()},
               {"board":"Graphical User Interface",
                "desc":"This page provides some helpful discussion for getting started with GUI programming in Python.",
                "board_id":shortuuid.uuid()},
               {"board":"Networking",
                "desc":"Python could be (is ?) the easiest way to write networking code. In this forum category we discuss specifically network code. ",
                "board_id":shortuuid.uuid()},
               {"board":"Web Programming",
                "desc":"Where Python makes a move against Perl. All about web programming right here.",
                "board_id":shortuuid.uuid()},
               {"board":"Python on Windows",
                "desc":"A place for windows-specific questions.",
                "board_id":shortuuid.uuid()},
               {"board":"System Administration",
                "desc":"System-oriented questions right here.",
                "board_id":shortuuid.uuid()},
               {"board":"Python Tools",
                "desc":"Discussion for editors, IDEs, tools, modules etc.",
                "board_id":shortuuid.uuid()},
               {"board":"Intermediate",
                "desc":"Something that might challenge most of the users on the forum? Post it here.",
                "board_id":shortuuid.uuid()},
               {"board":"Project Euler",
                "desc":"questions/discussions",
                "board_id":shortuuid.uuid()},
        ],
     },
    {"category":"Forum Activities",
     "desc":"A category for everything going on in the forum",
     "boards":[
         {"board":"Contests",
        "desc":"Compete against the best registered users of the forum in here. One competition every three months.",
        "board_id":shortuuid.uuid()},
         {"board":"Challenges",
          "desc":"Don't know were to put your knowledge to work or where to test your skills? Try searching here.",
          "board_id":shortuuid.uuid()},
         ]
    },

    {"category":"Miscellaneous",
     "desc":"Everything not already covered",
     "boards":[
         {"board":"Announcements",
          "desc":"News on the forum.",
          "board_id":shortuuid.uuid()},
         {"board":"Suggestions",
          "desc":"Anything you want to suggest is accepted. Just post it right here.",
          "board_id":shortuuid.uuid()},
         {"board":"Bar",
          "desc":"Talk about everything not only python.",
          "board_id":shortuuid.uuid()},
     ]
    }
]



from database.boards import *
from database.login import *
from database.categories import *
from database.forum import *
from database.posts import *
from database.threads import *

User.drop_collection()
Forum.drop_collection()
Board.drop_collection()
Category.drop_collection()

# Install some test users.
test_users = [User(email="test1@test.com", username="test1", active=True),
              User(email="test2@test.com", username="test2", active=True),
              User(email="test3@test.com", username="test3", active=True),
              User(email="test4@test.com", username="test4", active=True),
              User(email="test5@test.com", username="test5", active=True)]
# Hack
[user.save() for user in test_users]

python_forum = Forum()
python_forum.save()
# Install the forum.
for category in forum:
    boards = []
    for board in category['boards']:
        boards.append(Board(name=board['board'],
            description=board['desc'],
            board_id=board['board_id']))
    [board.save() for board in boards]
    cat = Category(name=category['category'],
            description=category['desc'],
            boards=boards)
    cat.save()
    python_forum.categories.append(cat)


python_forum.save()
