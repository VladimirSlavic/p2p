import socket
import threading
from time import sleep
import traceback
from peer_connection import PeerConnection
import json
from networkbase import NetworkBase


class Peer():

    def __init__(self, max_peer_neighbours, bootstrap_server_port):
        self.max_peer_neighbours = max_peer_neighbours
        self.bootstrap_server_port = bootstrap_server_port

        # list (dictionary/hash table) of known neighbour peers
        self.peers = {}

        # lock ensuring proper access to peer list (maybe better to use threading.RLock (reentrant))
        self.peer_lock = threading.Lock()

        # used to shutdown the main loop
        self.shutdown = False
        self.handlers = {}
        self.router = None
        self.debug = 0



    def connection_with_bootstrap(self):
        bootstrap_server_ip = '192.168.43.130'

        # create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connection to hostname on the port.
        s.connect((bootstrap_server_ip, self.bootstrap_server_port))

        while True:

            sleep(2)
            response = s.recv(1024)
            response_dic = json.loads(response.decode('utf8'))

            print(response_dic)

            if NetworkBase.MESSAGE_TYPE in response_dic:
                self.peers = response_dic[NetworkBase.IP_ADDRESSES]

            if len(self.peers) > 0:
                return


    def get_peer(self, peer_id):
        return self.peers[peer_id]

    def remove_peer(self, peer_id):
        if peer_id in self.peers:
             del self.peers[peer_id]

    def add_peer(self, peer_id, host, port):
        """ Adds a peer name and host:port mapping to the known list of peers. """
        if (peer_id not in self.peers) and (len(self.peers) < self.max_peer_neighbours):
            self.peers[peer_id] = (host, int(port))
            return True
        else:
            return False


    def get_peer_ids(self):
        """ Return list of known peer ids. """
        return self.peers.keys()

    def number_of_peers(self):
        """ Return number of known peers. """
        return len(self.peers)


    def _make_server_socket(self, port, backlog=5):
        """ Setting up socket that listens for incoming connections from other peers """
        # AF_INET = using IPv4, SOCK_STREAM = protocol with TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR = port number of the socket will be immediately reusable after the socket is closed
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind it to a port on which to listen for connections
        s.bind( ('', port) )
        # begin listening for connections
        s.listen(backlog)
        return s


    def _handle_peer(self, client_socket):
        """ Method looks for the appropriate handler for a message, dispatches the request to an appropriate handler (function or method) for processing. """
        print('Connected ' + str(client_socket.getpeername()) )
        host, port = client_socket.getpeername()
        peer_connection = PeerConnection(host=host, port=port , socket=client_socket,  peer_id=None, debug=False)

        try:
            # to implement
            msg_data = peer_connection.recv_data()
            print ("Message data primljen: ", msg_data)
            #if msg_type:
            #    msg_type = msg_type.lower()

            # self.handlers are message type handlers, hash table with function pointer
            #if msg_type not in self.handlers:
            #    self.__debug( 'Handling peer msg: %s: %s' % (msg_type, msg_data) )
            #    self.handlers[ msg_type ]( peer_connection, msg_data )
        except KeyboardInterrupt:
    	    pass
    	print( 'Disconnecting ' + str(client_socket.getpeername()) )
    	peer_connection.close()


    def check_live_peers(self):
        """ Attempts to ping all known peers to ensure that they are still active. If they are not active remove from list --> Simple stabilizer. """
        to_delete = []
        # loop over peers and send msg PING
        for p_id in self.peers:
            is_active = False
            try:
                print( 'Check live %s' % p_id )
                host, port = self.peers[p_id]
                peer_connection = PeerConnection(p_id, host, port, debug=self.debug)
                peer_connection.senddata( 'PING', '' )
                is_active = True
            except:
                to_delete.append(p_id)

            if is_active:
                peer_connection.close()
         # acquire lock to delete non active peers
        self.peer_lock.acquire()
        try:
            for p_id in to_delete:
                if p_id in self.peers:
                    del self.peers[p_id]
        except:
            pass

    def add_route_method(self, route_method):
        """
            Routing function (or method) with the Peer class to help decide how messages should be forwarded, given a destination peer id. The router
	        function should return a tuple of three values: (next-peer-id, host,port). If the message cannot be routed, the next-peer-id should be None.
        """
        self.route_method = route_method



    def connect_to_neighbours(self):
        print ("neigbours ", self.peers)
        for peer_ip in self.peers:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port = 50007

            s.connect((peer_ip, port))




    def run(self):
        """ Server socket after created in the main loop continously accpets connections. After the connection
            accepted new Thread is invoking method for handling messages """

        # Bootstrap in helper Thread
        self.connection_with_bootstrap()

        # Thread try to connect with neigbourds
        self.connect_to_neighbours()

        s = self._make_server_socket(self.bootstrap_server_port)
        s.settimeout(2)
        print('Server started: (%d)' % (self.bootstrap_server_port))

        while not self.shutdown:
            try:
                print( 'Listening for connections...' )
                # accepting connections on socket
                clientsock, clientaddr = s.accept()
                clientsock.settimeout(None)

                # if connection on socket accepted, invoke new thread for handling peer connections
                t = threading.Thread(target = self._handle_peer, args = [clientsock])
                t.start()

            except KeyboardInterrupt:
                self.shutdown = True
                continue


    	print('Main loop exiting')
    	s.close()
