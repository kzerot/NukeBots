from random import choice

robotTemplate = '''Robot: {0}'''


class Robot(object):
    def __init__(self, data):
        self.data = data
        self.name = data['name']
        self.inventory = data['inventory']
        self.x = data['x']
        self.y = data['y']
        self.owner = data['owner']
        self.actions = data['actions']
        self.instr = data['instructions']
        self.messages = data['messages']
        self.instr_stage = data["instructions_stage"]
        self.available_commands = [
            'go',
            'attack',
            'harvest'
        ]

    def _go_north(self):
        self.x += 1
        self.add_message('REPORT: GO NORTH COMPLITE')
        return 'OK'

    def _go_south(self):
        self.x -= 1
        self.add_message('REPORT: GO SOUTH COMPLITE')
        return 'OK'

    def _go_west(self):
        self.y -= 1
        self.add_message('REPORT: GO WEST COMPLITE')
        return 'OK'

    def _go_east(self):
        self.y += 1
        self.add_message('REPORT: GO EAST COMPLITE')
        return 'OK'

    def _go_random(self):
        f = choice([
            self._go_east, self._go_north, self._go_south, self._go_west
        ])
        return f()

    def _go(self, args):
        if len(args) == 1:
            try:
                c = getattr(Robot, '_go_{}'.format(args[0]))
                return c(self)
            except:
                self.add_message('Invalide attribute ' + args[0])
                return 'BREAK'
        elif len(args) == 2:
            return self.go_xy(args[0], args[1])

    def go_xy(self, x, y):
        try:
            x = int(x)
            y = int(y)
            if abs(self.x - x) > abs(self.y - y):
                #Go on X axis
                self.x += - int(abs(self.x - x) // (self.x - x))
            else:
                #Go on Y axis
                self.y += - abs(self.y - y) // (self.y - y)
            self.add_message(
                'REPORT: NEW COORDINATES {}/{}:'.format(self.x, self.y)
            )
            if self.x == x and self.y == y:
                if self.actions[0] == 'run':
                    return 'OK'
                else:
                    self.actions = self.actions[1:]
            return 'CONT'
        except:
            self.add_message('Can\'t go to coordinates {}/{}'.format(x, y))
            return 'BREAK'

    def __str__(self):
        return robotTemplate.format(self.name)

    def to_terminal(self):
        return [str(self), 'Coordinates: {}/{}'.format(self.x, self.y)]

    def to_update(self):
        return {'actions': self.actions, 'instructions': self.instr,
                'x': self.x, 'y': self.y, 'messages': self.messages}

    def process_action(self):
        if not self.actions or len(self.actions) == 0:
            return
        action = self.actions[0]
        name = action['name']
        args = action['args']
        if name == 'go' and len(args) == 2:
            self.go(args[0], args[1])
        elif name == 'run':
            self.run(args[0])

    def add_command(self, com, args):
        if com not in self.available_commands:
            return 'Not available command'
        #verify command
        if com == 'go':
            if(not args or len(args) != 2):
                return 'Not available arguments'
            elif(len(args) == 2 and
                (not str(args[0]).isdigit() or
                    not str(args[1]).isdigit())):
                return 'Arguments not numbers'
        self.actions.append({'name': com, 'args': args})
        return 'OK'

    def run(self, command):
        instr = self.instr[command].split('\n')
        if self.instr_stage >= len(instr):
            self.instr_stage = 0
            self.actions = self.actions[1:]
        act = instr[self.instr_stage].split(' ')
        com = act[0]
        args = act[1:]
        print('Process {}, stage {}, command {}'.format(
            command, self.instr_stage, com
        ))

        if com == 'jmp' and args[0] and str(args[0]).isdigit():
            self.instr_stage = int(args[0])
            print('jump to {}'.format(self.instr_stage))
        elif com == 'jmp':
            self.instr_stage = 0
            self.actions = self.actions[1:]
            self.add_message(
                'Incorrect usage jmp on stage {}'.format(self.instr_stage)
            )
            return

        result = 'OK'
        try:
            c = getattr(Robot, '_{}'.format(com))
            result = c(self, args)
        except:
            self.add_message(
                'Invalide instruction at line {}'.format(self.instr_stage)
            )
        if result == 'OK':
            self.instr_stage += 1
        elif result == 'BREAK':
            self.instr_stage = 0
            self.actions = self.actions[1:]
        elif result == 'CONT':
            pass
        else:
            self.instr_stage = 0
            self.actions = self.actions[1:]

    def add_message(self, message):
        self.messages.append(message)
        if(len(self.messages) > 3):
            self.messages = self.messages[-3:]
