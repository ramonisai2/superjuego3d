
class DialogueMemory:
    def __init__(self):
        self.visits=0
    def speak(self):
        self.visits+=1
        msgs=[
        "Arggg... ¿Qué quieres?",
        "Otra vez tú...",
        "Empiezo a reconocerte.",
        "Supongo que somos conocidos."
        ]
        return msgs[min(self.visits-1,len(msgs)-1)]
