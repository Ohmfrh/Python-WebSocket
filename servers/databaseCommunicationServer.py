import MySQLdb
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

db = MySQLdb.connect(host="localhost",
                     user="daniel",
                     passwd="123456",
                     db="Tests")



class DBConnect(Protocol):
    def dataReceived(self, data):
        data2 = data.rstrip()
        data2 = data2.split(':')

        try:
            if data2[0] == 'read':
                query = """SELECT %s FROM student""" % (data2[1])
                cursor = db.cursor()
                cursor.execute(query)
                for row in cursor.fetchall():
                    self.transport.write(str(row) + '\n')
                cursor.close()
                self.transport.loseConnection()
            elif data2[0] == 'write':
                query = """INSERT INTO student (name,lastName,account) VALUES ('%s','%s',%d)""" % ('Pablo','Tortis',500)
                cursor = db.cursor()
                cursor.execute(query)
                db.commit()
                cursor.close()
                self.transport.loseConnection()
            elif data2 == 'exit':
                self.transport.loseConnection()
            else:
                self.transport.write('ERROR\n')
                self.transport.loseConnection()
        except IndexError:
            print "INDEX ERROR"
            self.transport.write('Insufficient Data\n')
            self.transport.loseConnection()
        except MySQLdb.Error, e:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            self.transport.write('Mysql Query Error\n')
            self.transport.loseConnection()


def main():
    f = Factory()
    f.protocol = DBConnect
    reactor.listenTCP(8000, f)
    reactor.run()


if __name__ == '__main__':
    main()

