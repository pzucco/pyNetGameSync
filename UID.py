
UID_CLASSES = []

def UID_register_class(class_):
    if hasattr(class_, "CID"): raise Exception("Class already registered!")
    class_.CID = len(UID_CLASSES)
    UID_CLASSES.append(class_)
    class_.INT_NEXT_IID = 1
    class_.INSTANCES = {}
    return class_

def UID_register(instance, IID=0):
    if getattr(instance, "IID", 0): raise Exception("Instance already registered!")
    class_ = UID_CLASSES[instance.CID]
    if not IID: IID = class_.INT_NEXT_IID
    while IID in class_.INSTANCES:
        IID = 1 + IID % 32000
    class_.INT_NEXT_IID = IID
    class_.INSTANCES[IID] = instance
    instance.IID = IID

def UID_remove(instance):
    class_ = UID_CLASSES[instance.CID]
    del class_.INSTANCES[instance.IID]
    instance.IID = 0

def UID_request(CID, IID):
    if CID >= len(UID_CLASSES): raise Exception("Unknown class requested!")
    class_ = UID_CLASSES[CID]
    if IID in class_.INSTANCES: 
        return class_, class_.INSTANCES[IID]
    else:
        return class_, None

@UID_register_class
class UID_Function(object):

#    @staticmethod
#    def from_data(data, offset, conn):
#        return None, 1
   
    def is_feed_accepted(self, conn):
        return 0
   
    @staticmethod
    def is_remove_accepted(self, conn):
        return 0

UID_NULL = (0, 0)

def UID_get(instance):
    return getattr(instance, "CID", 0), getattr(instance, "IID", 0)

