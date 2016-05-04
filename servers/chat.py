import MySQLdb
from twisted.protocols import basic
from twisted.internet import reactor, protocol

import json
modules = []


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

                    connections = databaseQuery('', 'checkLogged')

                    if usrId != -1 and connections <= 5:
                        print usrId
                        modules[i]['thread'].transport.write('1')
                        for module in modules:
                            if module['module'] == 'audio/video':
                                print "Enviar a misterchanz"
                                video = databaseQuery(usrId, 'video')
                                audio = databaseQuery(usrId, 'audio')
                                user = databaseQuery(usrId, 'user')
                                print user
                                persona = {}
                                data = {}
                                persona['nombre'] = user['name']
                                persona['audio'] = audio
                                persona['img'] = video

                                data['persona'] = persona
                                if user['logged'] == '0':
                                    data['accion'] = 'in'
                                    print databaseQuery(usrId, 'login')
                                elif user['logged'] == '1':
                                    data['accion'] = 'out'
                                    print databaseQuery(usrId, 'logout')
                                else:
                                    print "????"

                                json_data = json.dumps(data)
                                j=0
                                for module in modules:
                                    if module['module'] == 'audio/video':
                                        databaseQuery(json_data, 'pipeline')
                                        modules[j]['thread'].transport.write(json_data)
                                        break
                                    j += 1

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
    db = MySQLdb.connect(host="localhost", user="daniel", passwd="12345", db="aula")
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
        db.close()
        return usrId
    elif module == 'video':
        query = """SELECT usr.name, usr.last_names, i.name, i.path, s.address FROM usuarios_usersys AS usr
                RIGHT JOIN imagenes_userimage AS ui ON usr.id=ui.user_id LEFT JOIN imagenes_image AS i
                ON i.id=ui.image_id LEFT JOIN multimedia_server AS s ON s.id=i.server_id WHERE usr.id=%i;""" % (line)
        cursor = db.cursor()
        cursor.execute(query)
        list = buildJSONDB(cursor, 'video')

        db.close()
        cursor.close()

        return list

    elif module == 'audio':
        query = """SELECT s.address, a.path, a.name, a.album, a.artist, a.image FROM usuarios_usersys AS usr
                RIGHT JOIN musica_usersong AS ua ON usr.id=ua.user_id LEFT JOIN musica_song AS a ON a.id=ua.song_id
                LEFT JOIN multimedia_server AS s ON s.id=a.server_id WHERE usr.id=%i""" % (line)
        cursor = db.cursor()
        cursor.execute(query)
        list = buildJSONDB(cursor, 'audio')
        cursor.close()
        db.close()


        return list
    elif module == 'user':
        obj = {}
        query = """SELECT name, last_names, logged FROM usuarios_usersys WHERE id=%i;""" % (line)
        cursor = db.cursor()
        cursor.execute(query)
        for row in cursor.fetchall():
            name = row[0] + ' ' + row[1]
            logged = row[2]

            break
        obj['name'] = name
        obj['logged'] = logged
        cursor.close()
        db.close()

        return obj
    elif module == 'logout':
        print "LOGOUT"
        query = """UPDATE usuarios_usersys SET logged=0 WHERE id=%i""" % (line)
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
    elif module=='login':
        print "LOGIN"
        query = """UPDATE usuarios_usersys SET logged=1 WHERE id=%i""" % (line)
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
    elif module == 'checkLogged':
        print "IN LOGGED"
        count = 0
        query = """SELECT COUNT(*) FROM usuarios_usersys WHERE logged='1'"""
        cursor = db.cursor()
        cursor.execute(query)
        for row in cursor.fetchall():
            return row[0]
    elif module == 'pipeline':
        query = """INSERT INTO home_pipeline (pipe) VALUES ('%s')""" % (line)
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()
    else:
        db.close()
        return -1


def buildJSONDB(cursor, module):
    obj = {}
    list = []
    if module == 'video':
        for row in cursor.fetchall():
            path = 'http://' + row[4] + row[3] + row[2]
            list.append(path)

        return list
    elif module == 'audio':
        for row in cursor.fetchall():
            list.append({'nombre': row[2],  'src': 'http://' + row[0] + row[1] + row[2], 'artista':row[3],
                         'album':row[4], 'imagen': row[5]})
        print list
        return list


factory = protocol.ServerFactory()
factory.protocol = MyChat
factory.clients = []
reactor.listenTCP(9090, factory)
reactor.run()
