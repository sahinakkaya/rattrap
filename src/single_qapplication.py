import sys
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtNetwork as QtNetwork


class SingleQApplication(QtWidgets.QApplication):
    visibility_changed = QtCore.pyqtSignal(bool)

    def __init__(self, argv, key):
        super().__init__(argv)
        QtCore.QSharedMemory(key).attach()

        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString())
        self._name = key
        self._timeout = 1000
        if not self.is_running():
            self._server = QtNetwork.QLocalServer(self)
            self._server.newConnection.connect(self.handle_message)
            self._server.setSocketOptions(QtNetwork.QLocalServer.WorldAccessOption)
            self._server.listen(self._name)

        try:
            self.visibility = False if argv[1] == "--run-in-background" else True
        except IndexError:
            self.visibility = True

    def is_running(self):
        return self._running

    def handle_message(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            data = socket.readAll().data().decode('utf-8')

            visibility = eval(data)  # data can be either 'True' or 'False'. So this operation is safe.
            self.visibility_changed.emit(visibility)
            socket.disconnectFromServer()
        else:
            QtCore.qDebug(socket.errorString())

    def send_message(self, message):
        if self.is_running():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._name, QtCore.QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                raise Exception(socket.errorString())
            if not isinstance(message, bytes):
                message = str(message).encode('utf-8')
            socket.write(message)
            if not socket.waitForBytesWritten(self._timeout):
                raise Exception(socket.errorString())
            socket.disconnectFromServer()
            sys.exit(0)
        else:
            self.visibility_changed.emit(self.visibility)


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.edit = QtWidgets.QLineEdit(self)
        self.edit.setMinimumWidth(300)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.edit)


if __name__ == '__main__':
    app_name = 'Single Application'
    app = SingleQApplication(sys.argv, app_name)
    window = Window()
    app.visibility_changed.connect(window.setVisible)
    app.send_message(app.visibility)
    sys.exit(app.exec_())
