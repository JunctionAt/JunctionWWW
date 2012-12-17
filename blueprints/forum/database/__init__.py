import os
from mongoengine import connect

# Try and connect to the development server.
# For security reasons the server location isn't pushed with the project.
# Try and import that location here
#try:
#    from ..config import db_uri as host
#except ImportError:
    # On failing to import that information look for an environ variable to tell us where to connect
    # Failing that just try for a local host connection
host = os.environ.get("PF_MONGO_SERVER", "mongodb://localhost/pf")

try:
    forum = connect("pf")
except Exception as e:
    print e.message
    print host
    raise e
