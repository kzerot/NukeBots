from pymongo import MongoClient
from random import choice


class LocTypes:
    clear = {'id': 1, 'resource': False, 'name': 'Clear location'}
    nucleum = {'id': 2, 'resource': True, 'name': 'Resource: nucleum'}
    gasolium = {'id': 3, 'resource': True, 'name': 'Resource: gasolium'}
    sand = {'id': 4, 'resource': False, 'name': 'Sands'}
    ruins = {'id': 5, 'resource': False, 'name': 'Ruins'}
    homebase = {'id': 6, 'resource': False, 'name': 'Homebase'}

    @staticmethod
    def dic():
        return [LocTypes.clear, LocTypes.nucleum, LocTypes.gasolium,
                LocTypes.sand, LocTypes.ruins]

    @staticmethod
    def by_id(lid):
        if lid == LocTypes.homebase['id']:
            return LocTypes.homebase['id']
        for l in LocTypes.dic():
            if lid == l['id']:
                return l


class Location(object):
    """docstring for Location"""
    def __init__(self, x, y, loctype, rescount=100):
        self.x = x
        self.y = y
        self.type = loctype
        self.rescount = rescount
        if not self.type['resource']:
            self.rescount = 0

    def toDic(self):
        return {'x': self.x, 'y': self.y,
                'type': self.type, 'res': self.rescount}

    def __str__(self):
        if not self.type['resource']:
            return '{2}, {0}/{1}'.format(self.x, self.y, self.type['name'])
        return '{3}, resource count: {2}, {0}/{1}'.format(self.x,
                                                          self.y,
                                                          self.rescount,
                                                          self.type['name'])


class Map(object):
    """docstring for Map"""
    def __init__(self):
        self.locs = {}
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['game_database']
        self.map = self.db.locations

    def generate(self, size):
        self.map.remove()
        for x in range(-size, size):
            for y in range(-size, size):
                loc = Location(x, y, choice(LocTypes.dic()))
                self.locs = []
                self.map.insert(loc.toDic())


if __name__ == "__main__":
    m = Map()
    m.generate(100)
