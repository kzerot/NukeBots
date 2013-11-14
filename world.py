from pymongo import MongoClient
from objects.robot import Robot
import time


class World(object):
    """docstring for World"""
    def __init__(self):
        self.time_to_sleep = 5
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['game_database']
        self.sleep_time = time.time()

    def update(self):
        print('time start', time.time())
        for robot in self.db.robots.find():
            self.process_robot(robot)
        print('time end', time.time())

    def run(self):
        while True:
            self.update()
            time.sleep(self.time_to_sleep - (time.time()-self.sleep_time))
            self.sleep_time = time.time()

    def process_robot(self, json):
        print('process robot', json['name'])
        robot = Robot(json)
        robot.process_action()
        self.db.robots.update({'name': robot.name, 'owner': robot.owner},
                              {'$set': robot.to_update()})


if __name__ == '__main__':
    w = World()
    w.run()
