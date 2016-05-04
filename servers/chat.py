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
                    usrId = databaseQuery(line, modules[i]['module'])

                    if usrId != -1:
                        print usrId
                        modules[i]['thread'].transport.write('1')
                        for module in modules:
                            if module['module'] == 'audio/video':
                                print "Enviar a misterchanz"
                                databaseQuery(usrId, 'video')
                                databaseQuery(usrId, 'audio')
                                break
                            else:
                                print "SEARCHING"
                    else:
                        self.transport.write('0')
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


def databaseQuery(line, module):
    if module == 'RFID':
        usrId = -1
        query = """SELECT usr.id AS userId FROM usuarios_usersys AS usr
                LEFT JOIN identificacion_identify AS id
                ON usr.id=id.usersys_id WHERE id.string='%s';""" % (line)
        cursor = db.cursor()
        cursor.execute(query)

        for row in cursor.fetchall():
            usrId = row[0]
        cursor.close()
        return usrId
    elif module == 'video':
        query = """SELECT usr.name, usr.last_names, i.name, i.path, s.address FROM usuarios_usersys AS usr
                RIGHT JOIN imagenes_userimage AS ui ON usr.id=ui.user_id LEFT JOIN imagenes_image AS i
                ON i.id=ui.image_id LEFT JOIN multimedia_server AS s ON s.id=i.server_id WHERE usr.id=%i;""" % (line)
        cursor = db.cursor()
        cursor.execute(query)

        for row in cursor.fetchall():
            print str(row)
    elif module == 'audio':
        query = """SELECT usr.name, usr.last_names, a.name, a.path, s.address FROM usuarios_usersys AS usr
        RIGHT JOIN musica_usersong AS ua ON usr.id=ua.user_id LEFT JOIN musica_song AS a ON a.id=ua.song_id
        LEFT JOIN multimedia_server AS s ON s.id=a.server_id WHERE usr.id=%i;""" % (line)
        cursor = db.cursor()
        cursor.execute(query)

        for row in cursor.fetchall():
            print str(row)
        cursor.close()

    else:
        return -1

factory = protocol.ServerFactory()
factory.protocol = MyChat
factory.clients = []
reactor.listenTCP(9090, factory)
reactor.run()
