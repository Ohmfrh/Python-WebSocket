from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class Echo(Protocol):
    def dataReceived(self, data):
        data2 = data.rstrip()
        print data
        print self

        if data2 == 'a':
            self.transport.write('Command a selected\n')
        elif data2 == 'b':
            dad2 = self.transport
        elif data2 == 'exit':
            print 'Connection terminated'
            self.transport.loseConnection()
        else:
            self.transport.write('server: ' + data)


def main():
    f = Factory()
    f.protocol = Echo
    reactor.listenTCP(8080, f)
    reactor.run()


if __name__ == '__main__':
    main()
