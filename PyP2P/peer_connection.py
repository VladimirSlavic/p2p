import socket
import traceback



class PeerConnection():
    def __init__(self, peer_id, host, port, socket = None, debug = False):
        self.peer_id = peer_id
        self.debug = debug
        if not socket:
            # connect socket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect( (host, int(port)) )
        else:
            self.s = socket


    #def _make_msg(self, msg_type, msg_data):
	 #      msg_len = len(msg_data)
	 #         msg = struct.pack( "!4sL%ds" % msg_len, msg_type, msg_len, msg_data)
	 #return msg


    def send_data(self, msg_type, msg_data):
        """ Send a message through a peer connection. Returns True on successs or False if there was an error. """
    	try:

    	    msg = "Evo lude poruke ..."  # self._make_msg(msg_type, msg_data)
            print ("Message send: ", msg)
            s.send(msg.encode('utf-8'))
    	except KeyboardInterrupt:
    	    raise
    	except:
    	    if self.debug:
    		traceback.print_exc()
    	    return False
    	return True


    def recv_data(self):
        """ Receive a message from a peer connection. Returns (None, None) if there was any error. """
        try:
            msg = self.s.recv(1024).decode('utf8').split('\n')
            if not msg: return None
        except:
            pass
        return msg

    def close(self):
	""" Close the peer connection. The send and recv methods will not work after this call. """
    	self.s.close()
    	self.s = None

    def __str__(self):
        return "|%s|" % self.peer_id
