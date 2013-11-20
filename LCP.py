
from Structs import *
import socket

from dummy import *

class LCP(object):

    def _create_connection(self, addr):
        return {
            'addr': addr,
            'itag': 2, # input tag
            'otag': 1, # output tag
            'tick': self._tick,
            'rtt': self.default_rtt,
            'buffer': [],
        }

    def __init__(self, **kargs):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if kargs.get('port', None): self.socket.bind(('', kargs['port']))
        self.socket.setblocking(0)
        self.connections = {}
        # assuming 30 process() per second for default values...
        self.default_rtt = kargs.get('default_rtt', 10)
        self.ping_freq = kargs.get('ping_freq',  30)
        self.timeout = kargs.get('timeout', 300)
        
        self.hook_accept = kargs.get('hook_accept', dummy_true)
        self.hook_forget = kargs.get('hook_forget', dummy)
        
        self._tick = 0
        
    def send(self, data, addr):
        self.socket.sendto(STRUCT_BYTE.pack(0) + data, addr["addr"] if isinstance(addr, dict) else addr)
        
    def send_reliable(self, data, addr):
        addr = addr["addr"] if isinstance(addr, dict) else addr
        if addr not in self.connections: raise Exception("Address (%s) has no connection." % addr)
        conn = self.connections[addr]
        conn['buffer'].append(data)
        if len(conn['buffer']) == 1:
            self.socket.sendto(STRUCT_BYTE.pack(conn['otag']) + data, addr)
            conn['tick'] = self._tick
    
    def connect(self, data, addr):
        addr = addr["addr"] if isinstance(addr, dict) else addr
        if addr in self.connections: raise Exception("Address (%s) already connected." % addr)
        self.connections[addr] = self._create_connection(addr)
        self.send_reliable(data, addr)

    def process(self):
        while 1:
            try:
                packet, addr = self.socket.recvfrom(4096)
                
                tag = STRUCT_BYTE.unpack_from(packet)[0]
                if not tag:
                    self.receive(buffer(packet, 1), self.connections.get(addr, {"addr": addr}))
                    
                else:
                    if addr not in self.connections:
                        if tag != 1: continue
                        new_connection = self._create_connection(addr)
                        if self.hook_accept(buffer(packet, 1), new_connection):
                            self.connections[addr] = new_connection
                        continue
                    conn = self.connections[addr]
                
                    if tag > 100: # if returning tag
                        tag -= 100
                        if tag == conn['otag']:
                         
                            conn['otag'] += 1
                            if conn['otag'] == 100: conn['otag'] = 4
                          
                            conn['buffer'][:] = conn['buffer'][1:]
                            conn['rtt'] = (conn['rtt'] + self._tick - conn['tick']) / 2.
                            if len(conn['buffer']):
                                self.socket.sendto(STRUCT_BYTE.pack(conn['otag']) + conn['buffer'][0], addr)
                                conn['tick'] = self._tick
        
                    else:
                        if tag == conn['itag']:
                         
                            conn['itag'] += 1
                            if conn['itag'] == 100: conn['itag'] = 4
                            
                            if len(packet) > 1:
                                self.receive(buffer(packet, 1), conn)
                            self.socket.sendto(STRUCT_BYTE.pack(tag + 100), addr)
                        
                        elif tag == conn['itag'] - 1 or (tag == 100 and conn['itag'] == 4):
                            self.socket.sendto(STRUCT_BYTE.pack(tag + 100), addr)

            except socket.error:
                break
            #except:
            #    continue
        for addr, conn in self.connections.items():
            if conn['buffer']:
                if (self._tick - conn['tick']) % (-conn['rtt'] * 2) == -1:
                    self.socket.sendto(STRUCT_BYTE.pack(conn['otag']) + conn['buffer'][0], addr)
            else:
                if (self._tick - conn['tick']) % -self.ping_freq == -1:
                    conn['buffer'].append('')
                    self.socket.sendto(STRUCT_BYTE.pack(conn['otag']), addr)
                    conn['tick'] = self._tick
            if (self._tick - conn['tick']) > self.timeout:
                self.disconnect(conn)
        self._tick += 1

#    def disconnected(self, conn):
#    def is_connection_accepted(self, data, conn):

    def disconnect(self, addr):
        addr = addr["addr"] if isinstance(addr, dict) else addr
        conn = self.connections[addr]
        self.hook_forget(conn)
        del self.connections[conn["addr"]]








