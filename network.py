import socket
import pickle
import models
import threading

class PlayerServer(models.Player):
    def __init__(self,name,port,debug=False):
        self.host = "localhost"
        self.port = port
        self.debug = debug
        self.delim = b'EOT'

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host,self.port))
        self.socket.listen(1)
        self.conn, self.addr = self.socket.accept()
        if self.debug:
            print('Connected by {}'.format(self.addr))
        
        #TODO receive player name form network instead of param

        super().__init__(name)

    def send_to_client(self,action,game):
        # send action and game state
        print(action)
        print(game)
        data = pickle.dumps((action,game))
        self.conn.sendall(data + self.delim)

        # receive modified game 
        data = []
        while True:
            packet = self.conn.recv(4096)
            if self.debug:
                print(packet)
            if not packet: break
            data.append(packet)
            if self.delim in packet: break
        data_complete = b"".join(data)
        data_complete = data_complete.split(self.delim)[0]
        game_modified = pickle.loads(data_complete)

        # TODO verify that modifications are legal
        game = game_modified
        
    def play_setup_actions(self,game):
        self.send_to_client('play_setup_actions',game)

    def play_round_start_actions(self,game):
        self.send_to_client('play_round_start_actions',game)
        
    def play_round_regular_actions(self,game):
        self.send_to_client('play_round_regular_actions',game)

    def play_round_interrupt_actions(self,game):
        self.send_to_client('play_round_interrupt_actions',game)

    def play_round_end_actions(self,game):
        self.send_to_client('play_round_end_actions',game)
    
    def play_end_actions(self,game):
        self.send_to_client('play_end_actions',game)

    def __del__(self):
        self.conn.sendall(b'EOG') # be polite and warn the client
        self.conn.close()

    def __repr__(self):
        return "PlayerServer_{}".format(self.name)

class PlayerClient:
    def __init__(self,host,port,player,debug=False):
        self.host = host
        self.port = port
        self.delim = b'EOT'
        self.player = player
        self.still_connected = True
        self.debug = debug
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host,self.port))

        #TODO send player name

        while self.still_connected: 
            self.do_action_on_server_request()

    def do_action_on_server_request(self):
        # receive game state and action to perform
        data = []
        while True:
            packet = self.socket.recv(4096)
            if self.debug:
                print(packet)
            if not packet: break
            data.append(packet)
            if self.delim in packet: break
        data_complete = b"".join(data)
        data_complete = data_complete.split(self.delim)[0]

        if data_complete == b'':
            return

        if data_complete == b'EOG':
            # server should send End Of Game before closing
            self.still_connected = False
            return

        (action,game) = pickle.loads(data_complete)
        print(action)
        print(game)
        fun = getattr(self.player,action)

        # do the action and modify game state
        fun(game)

        # send back modified game state
        self.socket.sendall(pickle.dumps(game) + self.delim)