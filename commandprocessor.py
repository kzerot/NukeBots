import re
import string
import random
from objects.robot import Robot


#classes
class CommandProcessor(object):
    """docstring for CommandProcessor"""
    def __init__(self, db):
        self.db = db

    def process_command(self, fullcommand, userId):
        fullcommand = fullcommand.lower().strip()
        command = fullcommand.split(' ')[0]
        args = None
        if len(fullcommand.split(' ')) > 1:
            args = fullcommand.split(' ')[1:]
        #try to call function
        answer = None
        try:
            c = getattr(CommandProcessor, command)
            if c and command in CommandProcessor.AccessList:
                answer = c(self, userId, args)
            else:
                answer = ['''can't find command''']
        except Exception as e:
            raise e
            answer = ['Wrong command', str(e)]
        return answer

    def ls(self, userId, args):
        robot = self.db.robots.find_one({'owner': userId})
        if not robot:
            self.db.robots.insert({
                "name": generate_name(),
                "inventory": [],
                "x": 0,
                "y": 0,
                "owner": userId,
                "actions": [],
                "instructions": {},
                "messages": [],
                "instructions_stage": 0,
            })
            robot = self.db.robots.find_one({'owner': userId})
        robot = Robot(robot)
        return robot.to_terminal()

    def command(self, userId, args):
        if not args or len(args) == 0:
            resultString = ['Usage: command [command name] [args]',
                            'where command like go, attack, harvest']
        else:
            robot = Robot(self.db.robots.find_one({'owner': userId}))
            tmpres = robot.add_command(args[0], args[1:])
            if tmpres == 'OK':
                resultString = ['ACCEPTED']
                self.db.robots.update(
                    {'name': robot.name, 'owner': robot.owner},
                    {'$set': robot.to_update()}
                )
            else:
                resultString = [tmpres]
        return resultString

    def show(self, userId, args):
        if not args or len(args) == 0:
            resultString = ['Usage: show [object]',
                            'where object in: robot, location, loc, stats']
        else:
            if args[0] in ['loc', 'location']:
                resultString = self.showloc(userId, args[1:])
            elif args[0] == 'robot':
                resultString = self.ls(userId, args[1:])
            else:
                resultString = ['Not available now =(']
        return resultString

    def showloc(self, userId, args):
        x = y = 0
        if args is not None and len(args) != 2 and len(args) != 0:
            return ['Usage: "show loc X Y" where X and Y are integer. ']
        elif args is not None and len(args) == 2:
            x, y = args
            if (type(x) is not int and not x.isdigit()) or \
                    (type(y) is not int and not y.isdigit()):
                return ['Error: in loc command X and Y must be integer!']
            x = int(x)
            y = int(y)
        else:
            robot = self.db.robots.find_one({'owner': userId})
            x = robot['x']
            y = robot['y']
        l = self.db.locations.find_one({'x': x,
                                        'y': y})
        if not l:
            return ['Error. Robot on neverland\'s location ' + str(x) + str(y)]
        if not l['type']['resource']:
            resultString = ['{2}, {0}/{1}'.format(x,
                                                  y,
                                                  l['type']['name'])]
        else:
            resultString = \
                ['{3}, count: {2}, {0}/{1}'.format(l['x'],
                                                   l['y'],
                                                   l['res'],
                                                   l['type']['name'])]
        return resultString

    def run(self, userId, args):
        print(args)
        if not args or len(args) == 0:
            return ['Usage: run [commandname]']
        if len(args) > 1:
            return ['Robot can run only instruction without arguments']
        robot = Robot(self.db.robots.find_one({'owner': userId}))
        if args[0] not in robot.instr.keys():
            return ['This robot don\'t have this instruction']
        robot.actions.append({'name': 'run', 'args': args})
        self.db.robots.update(
            {'owner': robot.owner},
            {'$set': {'actions': robot.actions}}
        )
        return ['ACCEPTED']

    #globals
    AccessList = ['ls', 'show', 'command', 'run']


#methods
def generate_name():
    res = ""
    for t in range(random.randint(4, 8)):
        res = res + random.choice(string.ascii_letters + string.digits)
    return res
