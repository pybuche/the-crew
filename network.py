import socket
import pickle
import struct
import models

class PlayerServer(models.Player):
    def __init__(self,name,port,debug=False):
        self.host = "localhost"
        self.port = port
        self.debug = debug

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host,self.port))
        self.socket.listen(1)
        self.conn, self.addr = self.socket.accept()
        if self.debug:
            print('Connected by {}'.format(self.addr))
        
        #TODO receive player name form network instead of param

        super().__init__(name)

    def send_to_client(self,action,game_state):
        # send action and game state
        data = pickle.dumps((action,game_state))
        self.conn.sendall(struct.pack('>I',len(data)))
        self.conn.sendall(data)

        # receive modified game 
        data_size = struct.unpack('>I', self.conn.recv(4))[0]
        received_payload = b""
        remaining_payload_size = data_size
        while remaining_payload_size != 0:
            received_payload += self.conn.recv(remaining_payload_size)
            remaining_payload_size = data_size - len(received_payload)
        game_state_modified = pickle.loads(received_payload)
        game_state.set_state(game_state_modified)
        
    def play_setup_actions(self,game_state):
        self.send_to_client('play_setup_actions',game_state)

    def play_round_start_actions(self,game_state):
        self.send_to_client('play_round_start_actions',game_state)
        
    def play_round_regular_actions(self,game_state):
        self.send_to_client('play_round_regular_actions',game_state)

    def play_round_interrupt_actions(self,game_state):
        self.send_to_client('play_round_interrupt_actions',game_state)

    def play_round_end_actions(self,game_state):
        self.send_to_client('play_round_end_actions',game_state)
    
    def play_end_actions(self,game_state):
        self.send_to_client('play_end_actions',game_state)

    def __repr__(self):
        return "PlayerServer_{}".format(self.name)

class PlayerClient:
    def __init__(self,host,port,player,debug=False):
        self.host = host
        self.port = port
        self.player = player
        self.still_connected = True
        self.debug = debug
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host,self.port))

        #TODO get initial state and display 
        #TODO send player name

        while self.still_connected: 
            self.do_action_on_server_request()

    def do_action_on_server_request(self):
        # receive game state and action to perform
        data_size = struct.unpack('>I', self.socket.recv(4))[0]
        received_payload = b""
        remaining_payload_size = data_size
        while remaining_payload_size != 0:
            received_payload += self.socket.recv(remaining_payload_size)
            remaining_payload_size = data_size - len(received_payload)
        (action,game_state) = pickle.loads(received_payload)

        fun = getattr(self.player,action)
        fun(game_state) 

        # send back modified game state
        data = pickle.dumps(game_state)
        self.socket.sendall(struct.pack('>I',len(data)))
        self.socket.sendall(data)