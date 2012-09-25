from sqlalchemy import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import *
from blueprints.base import Base

def beardstat(tablename='stats'):
    
    stat = type(tablename, (Base,), {

        '__tablename__': tablename,
        'player': Column(String(32), primary_key=True),
        'category': Column(String(32), primary_key=True),
        'stat': Column(String(32), primary_key=True),
        'value': Column(Integer()),

        })
    
    return stat
