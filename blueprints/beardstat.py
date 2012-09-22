import unittest

from sqlalchemy.ext.declarative import declarative_base

def load(engine, table='stats'):

  Base = declarative_base()
  return type('Stats', ( Base, ), {
          '__tablename__': table,
          '__table_args__': ({
              'autoload': True,
              'autoload_with': engine
              })
          })

class Test(unittest.TestCase):

  def setUp(self):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import create_session
    engine = create_engine('sqlite:////mc/pve/plugins/BeardStat/stats.db', echo=True)
    self.BeardStat = load(engine)
    self.session = create_session(engine)

  def tearDown(self):
    self.session.close()

  def test_player(self):
    q = self.session.query(self.BeardStat.Stats)
    self.assertTrue(q.count() >= 0)
