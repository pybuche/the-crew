import socketserver
import socket

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)

        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

class Server:
    def __init__(self,port):
        self.host = "localhost"
        self.port = port
        with socketserver.TCPServer((self.host, port), TCPHandler) as server:
            #TODO interrupt when you exit the game using server.
            # shutdown() in another thread
            server.serve_forever()

class Client:
    def __init__(self,host,port):
        self.host = host
        self.port = port

        data = "blabla"

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((host, port))
            sock.sendall(bytes(data + "\n", "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

        print("Sent:     {}".format(data))
        print("Received: {}".format(received))