# début du "piles" version "12"
version = ('piles.py', 12)
import uasyncio as asyncio

class Piles:
    def __init__(self):
        # Adresses fixes dans la zone mémoire (512KB = 0x80000)
        # Zone haute pour les piles
        self.SP0 = 0x7FFF0    # Top of data stack (environ 512KB - 16 bytes)
        self.RP0 = 0x7FF00    # Top of return stack (256 bytes plus bas)
        
        from memoire import mem
        self.mem = mem
        
        # Initialisation des pointeurs
        self.mem.sp = self.SP0
        self.mem.rp = self.RP0

    async def push(self, value):
        """Empile une valeur 32 bits sur la pile de données"""
        self.mem.sp -= 4
        if self.mem.sp < self.mem.here + 0x1000:  # protection basique
            raise MemoryError(f"Data stack overflow (sp={self.mem.sp:#x}, here={self.mem.here:#x})")
        self.mem.wpoke(self.mem.sp, value & 0xFFFFFFFF)

    async def pop(self):
        """Dépile une valeur 32 bits de la pile de données"""
        if self.mem.sp >= self.SP0:
            raise IndexError(f"Data stack underflow (sp={self.mem.sp:#x})")
        val = self.mem.wpeek(self.mem.sp)
        self.mem.sp += 4
        return val

    async def rpush(self, value):
        """Empile sur la pile de retour"""
        self.mem.rp -= 4
        if self.mem.rp < self.mem.sp:
            raise MemoryError(f"Return stack overflow (rp={self.mem.rp:#x}, sp={self.mem.sp:#x})")
        self.mem.wpoke(self.mem.rp, value)

    async def rpop(self):
        """Dépile de la pile de retour"""
        if self.mem.rp >= self.RP0:
            raise IndexError(f"Return stack underflow (rp={self.mem.rp:#x})")
        val = self.mem.wpeek(self.mem.rp)
        self.mem.rp += 4
        return val

    async def pop_string(self):
        """Dépile une chaîne terminée par 0 (empilée à l'envers par C!")"""
        s = ""
        while True:
            c = await self.pop()
            if c == 0:
                break
            s += chr(c & 0xFF)
        return s[::-1]  # inverse car empilée à l'envers

    def depth(self):
        """Profondeur actuelle de la pile de données"""
        return (self.SP0 - self.mem.sp) // 4

    def rdepth(self):
        """Profondeur de la pile de retour"""
        return (self.RP0 - self.mem.rp) // 4

# Instance globale
piles = Piles()
print("piles.py v12 chargé – adresses corrigées pour 512KB RAM")
# fin du "piles" version "12"