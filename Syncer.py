
from Structs import *
from UID import *
from LCP import *

STRUCT_UID = StructBase("!Bh")

class Syncer(LCP):

    SINGLETON = None

    def __init__(self, port=None):
        if Syncer.SINGLETON: raise("Syncer SINGLETON already exists!")
        Syncer.SINGLETON = self
        LCP.__init__(self, port=port)
       
    def _create_connection(self, addr):
        conn = LCP._create_connection(self, addr)
        conn['ufeed'] = ""
        conn['rfeed'] = ""
        return conn
    
    def feed(self, instance):
        data = STRUCT_UID.pack(instance.CID, instance.IID) + instance.get_data()
        for addr, conn in self.connections.iteritems(): 
            if instance.is_feed_to(conn):
                conn["ufeed"] += data

    def feed_reliable(self, instance):
        data = STRUCT_UID.pack(instance.CID, instance.IID) + instance.get_data()
        for addr, conn in self.connections.iteritems(): 
            if instance.is_feed_to(conn):
                conn["rfeed"] += data
   
    def remove(self, instance):
        data = STRUCT_UID.pack(instance.CID, -instance.IID)
        for addr, conn in self.connections.iteritems(): 
            if instance.is_remove_to(conn):
                conn["ufeed"] += data

    def remove_reliable(self, instance):
        data = STRUCT_UID.pack(instance.CID, -instance.IID)
        for addr, conn in self.connections.iteritems(): 
            if instance.is_remove_to(conn):
                conn["rfeed"] += data            

    def feed_direct(self, instance, conn):
        data = STRUCT_UID.pack(instance.CID, instance.IID) + instance.get_data()
        conn["ufeed"] += data

    def feed_reliable_direct(self, instance, conn):
        data = STRUCT_UID.pack(instance.CID, instance.IID) + instance.get_data()
        conn["rfeed"] += data

    def remove_direct(self, instance, conn):
        data = STRUCT_UID.pack(instance.CID, -instance.IID)
        conn["ufeed"] += data

    def remove_reliable_direct(self, instance, conn):
        data = STRUCT_UID.pack(instance.CID, -instance.IID)
        conn["rfeed"] += data      

    
    def process(self):
        for addr, conn in self.connections.iteritems():
            if conn["ufeed"]:
                self.send(conn["ufeed"], addr)
                conn["ufeed"] = ""
            if conn["rfeed"]:
                self.send_reliable(conn["rfeed"], addr)
                conn["rfeed"] = ""
        LCP.process(self)
    
    def receive(self, data, conn):
        offset = 0
        while offset < len(data):
            (CID, IID), offset = STRUCT_UID.unpacking(data, offset)
            # Positive feed
            if IID > 0:
                class_, instance = UID_request(CID, IID)
                if class_:
                    if class_.is_feed_accepted(instance, conn):
                        if not instance:
                            instance = class_()
                            UID_register(instance, IID)
                        offset = instance.set_data(data, offset, conn)
                    else:
                        print "Received rejected feed!"
                        offset = len(data)
                else:
                    print "Received unknown class feed!"
                    offset = len(data)
            # Negative feed (instance removal)
            else:
                class_, instance = UID_request(CID, -IID)
                if class_:
                    if instance:
                        if instance.is_remove_accepted(conn):
                            UID_remove(instance)
                        else:
                            print "Received rejected remove!"
                            offset = len(data)
                else:
                    print "Received unknown class remove!"
                    offset = len(data)

