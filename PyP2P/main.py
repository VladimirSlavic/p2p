from full_peer import Peer



def start():

    bootstrap_server_port = 50007
    max_peer_neighbour = 3

    p = Peer(max_peer_neighbour, bootstrap_server_port)
    p.run()

    print ("Peer node is killed.")



if __name__ == '__main__':
    start()
