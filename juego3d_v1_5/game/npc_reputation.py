
class ReputationSystem:
    def __init__(self):
        self.rep={}
    def change(self,npc_id,value):
        self.rep[npc_id]=self.rep.get(npc_id,0)+value
    def get(self,npc_id):
        return self.rep.get(npc_id,0)
