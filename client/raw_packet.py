'''
    Raw sockets on Linux
     
    Silver Moon (m00n.silv3r@gmail.com)
'''
 
# some imports
import socket, sys
import random
from struct import *



class Connection:
    # Local variables :
    # Destionation address of the server : (ip, port)
    dest_addr = None
    # Local address of the socket : (ip, port)
    src_addr = None
    # Socket used for this connection
    s = None
    # Indicates whether the connection is closed
    # If -1 : connection opened
    # If equal to the ACK corresponding to the FIN packet : close
    fin = -1

    def __init__(self, dest_ip, dest_port):     
        #create a raw socket
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            self.dest_addr = (dest_ip, dest_port)
            # Connect the raw socket. Thus, the only packets we will receive are those coming from our target IP address.
            self.s.connect(self.dest_addr)
            self.src_addr = self.s.getsockname()
        except socket.error , msg:
            print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

    def send_raw(self, seq_nbr, ack_nbr=-1, content = '', syn=0, fin=0, rst=0):
        # first, decide whether we have an ack packet or not
        if ack_nbr == -1:
            ack = 0
            ack_seq = 0
        else:
            ack = 1
            ack_seq = ack_nbr % (1<<32)

        # We want to raise an error if we try to send a packet on a 
        # connection closed by the server


        # unpack the addresses
        src_ip, src_port = self.src_addr
        dest_ip, dest_port = self.dest_addr
        # checksum functions needed for calculation checksum
        def checksum(msg):
            s = 0
             
            # loop taking 2 characters at a time
            for i in range(0, len(msg), 2):
                w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
                s = s + w
             
            s = (s>>16) + (s & 0xffff);
            s = s + (s >> 16);
             
            #complement and mask to 4 byte short
            s = ~s & 0xffff
             
            return s

         
        # tell kernel not to put in headers, since we are providing it, when using IPPROTO_RAW this is not necessary
        # s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
             
        # now start constructing the packet
         
        source_ip = src_ip
        dest_ip = dest_ip # or socket.gethostbyname('www.google.com')
         
         
        # tcp header fields
        tcp_source = src_port   # source port
        tcp_dest = dest_port   # destination port
        tcp_seq = seq_nbr % (1<<32)
        tcp_ack_seq = ack_seq
        tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #tcp flags
        tcp_fin = fin
        tcp_syn = syn
        tcp_rst = rst
        tcp_psh = 0
        tcp_ack = ack
        tcp_urg = 0
        tcp_window = socket.htons (5840)    #   maximum allowed window size
        tcp_check = 0
        tcp_urg_ptr = 0
         
        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
         
        # the ! in the pack format string means network order
        tcp_header = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
         
        user_data = content
         
        # pseudo header fields
        source_address = socket.inet_aton( source_ip )
        dest_address = socket.inet_aton(dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header) + len(user_data)
         
        psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
        psh = psh + tcp_header + user_data;
         
        tcp_check = checksum(psh)
        #print tcp_checksum
         
        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        tcp_header = pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('H' , tcp_check) + pack('!H' , tcp_urg_ptr)
         
        # final full packet - syn packets dont have any data
        #packet = ip_header + tcp_header + user_data
        packet = tcp_header + user_data
         
        #Send the packet finally - the port specified has no effect
        self.s.sendto(packet, (dest_ip , 0 ))    # put this in a loop if you want to flood the target
        #self.s.sendall(packet)

        # If we sent the response to a FIN packet : raise an exception to indicate that the connection is closed
        if self.fin == ack_seq:
            return False
        elif self.fin != -1:
            raise self.Closed
        return True


    def parse(self, packet):
        # Code from http://www.binarytides.com/python-packet-sniffer-code-linux/
        """
        Takes a packet as input. Returns the sequence number and the payload size
        of the packet if it corresponds to a packet from the expected flow, or (-1, -1) otherwise
        """
        ip_header = packet[0:20]
         
        #now unpack them :)
        iph = unpack('!BBHHHBBH4s4s' , ip_header)
         
        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
         
        iph_length = ihl * 4
         
        tcp_header = packet[iph_length:iph_length+20]
         
        #now unpack them :)
        tcph = unpack('!HHLLBBHHH' , tcp_header)
         
        source_port = tcph[0]
        dest_port = tcph[1]
        sequence = tcph[2]
        #acknowledgement = tcph[3]
        doff_reserved = tcph[4]
        tcph_length = doff_reserved >> 4

        fin_flag = (tcph[5] & 0x1) != 0
        rst_flag = (tcph[5] & 0x4) != 0

        #print "Src port : %d, Dest port : %s, sequence : %d" % (source_port, dest_port, sequence)
        
        expected_dest = self.src_addr[1]
        expected_src = self.dest_addr[1]

        if expected_src != source_port or expected_dest != expected_dest:
            return (-1,-1) # we could also throw an exception, but it might slow us down

        h_size = iph_length + tcph_length * 4
        data_size = len(packet) - h_size
        if fin_flag:
            # On receiving a FIN, send an ACK for the last received packet number + 1
            data_size += 1
            self.fin = sequence+data_size
        if rst_flag:
            raise self.Closed
        
        return (sequence, data_size)


    def initiate_connection(self, content="GET / HTTP/1.0\r\n\r\n"):
        """
        Establishes a 3-Way TCP handshake with the remote server, and then
        sends a request to the server. By default, request the root page
        of the remote server over HTTP 1.0.
        Returns the local sequence number of all the subsequent ACKs that will
        be sent to the server 
        """
        r = random.Random()
        local_seq = r.randint(0, 1<<32-1)
        self.send_raw(local_seq, syn=1)
        (seq,_) = self.read_packet()
        local_seq += 1
        self.send_raw(local_seq, ack_nbr=seq+1)
        self.send_raw(local_seq, ack_nbr=seq+1, content=content)
        return local_seq + len(content)

    def read_packet(self, buffer_size=65535):
        """
        Reads one packet from the socket. Returns the corresponding sequence number
        Also, ensure that the returned sequence number corresponds to a packet
        from the correct flow
        """
        while True:
            rep = self.s.recvfrom(buffer_size)
            (seq, length) = self.parse(rep[0])
            if seq >= 0:
                return (seq, length)

    def tear_down(self, seq):
        self.send_raw(seq, fin=1, ack_nbr=self.fin)
        self.fin = -1
        _ = self.read_packet() # wait for the ACK
        self.send_raw(seq+1, ack_nbr=self.fin, rst=1)

        
    class Closed(Exception):
        pass


