import socket
import pickle
import struct
import models
import ssl

#TODO make it more secure using TLS/SSL 
#TODO make the server validate changes made to gamestate (anti-cheat)

def send_payload(sock,msg):
    sock.sendall(struct.pack('>I',len(msg)))
    sock.sendall(msg)

def recv_payload(sock):
    data_size = struct.unpack('>I', sock.recv(4))[0]
    received_payload = b""
    remaining_payload_size = data_size
    while remaining_payload_size != 0:
        received_payload += sock.recv(remaining_payload_size)
        remaining_payload_size = data_size - len(received_payload)
    return received_payload

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

    def validate(self,action,game_state,game_state_modified):
        #TODO implement gamestate change validation to prevent cheating
        return True

    def send_to_client(self,action,game_state):
        # send action and game state
        data = pickle.dumps((action,game_state))
        send_payload(self.conn,data)

        # receive modified game 
        received_payload = recv_payload(self.conn)
        game_state_modified = pickle.loads(received_payload)

        # validate changes
        if self.validate(action,game_state,game_state_modified):
            game_state.set_state(game_state_modified)
        else:
            print("Cheating is bad, play again")
            self.send_to_client(action,game_state)
        
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
        received_payload = recv_payload(self.socket)
        (action,game_state) = pickle.loads(received_payload)

        print(game_state.player_str())

        fun = getattr(self.player,action)
        fun(game_state)

        # send back modified game state
        data = pickle.dumps(game_state)
        send_payload(self.socket,data)

        # disconnect if we are done playing
        if game_state.last_round() and action == 'play_end_actions':
            self.still_connected = False
