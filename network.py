import socketserver
import socket
import threading

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):

        self.request.sendall("input")

        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)

        self.request.sendall("game_over")

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
            # Connect to server 
            sock.connect((host, port))
            # loop until the server sends a termination signal
            while True:
                # read until you are asked to respond
                received = str(sock.recv(1024), "utf-8")
                if received == "game_over":
                    break
                if received == "input": 
                    sock.sendall(bytes(data + "\n", "utf-8"))
                    received = ""

                print("Received: {}".format(received))
                print("Sent:     {}".format(data))