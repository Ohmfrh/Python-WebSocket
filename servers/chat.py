import MySQLdb
from twisted.protocols import basic
from twisted.internet import reactor, protocol
from twisted.application import service, internet

import json
modules = []
db = MySQLdb.connect(host="localhost",
                     user="daniel",
                     passwd="12345",
                     db="aula")

class MyChat(basic.LineReceiver):
    def connectionMade(self):
        self.factory.clients.append(self)
        print "Got new client!"

    def connectionLost(self, reason):
        print "Lost a client!"

        self.factory.clients.remove(self)

    def lineReceived(self, line):
        split = line.split('=')

        if line == 'exit':
            self.transport.loseConnection()

        if split[0] == 'module':
            obj = {}
            obj['module'] = split[1]
            obj['thread'] = self
            modules.append(obj)
        else:
            if len(modules) > 0:
                i = 0
                for module in modules:
                    if module['thread'] == self:
                        print "Encontrado: " + module['module']
                        break
                    i += 1
                print modules[i]['module']
                if modules[i]['module'] == 'RFID':
                    query = """select string from identificacion_identify WHERE string = '%s'""" % (line)
                    cursor = db.cursor()
                    cursor.execute(query)
                    if cursor.fetchall():
                        modules[i]['thread'].transport.write('1')
                        for module in modules:
                            if module['module'] == 'audio/video':
                                print "Enviar a misterchanz"
                            else:
                                print "NO A/V MODULE"
                    else:
                        self.transport.write('0')
                    cursor.close()
                elif modules[i]['module'] == 'audio/video':
                    print "De misterchanz"
            else:
                print "NO MODULES"



    def message(self, message):
        # data = {}
        # data['name'] = 'daniel'
        # json_data = json.dumps(data)
        # self.transport.write(json_data)
        self.transport.write(message)


factory = protocol.ServerFactory()
factory.protocol = MyChat
factory.clients = []
reactor.listenTCP(8080, factory)
reactor.run()
