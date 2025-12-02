# début du "piles" version "15"
version = ('piles.py', 15)
import uasyncio as asyncio

class Piles:
    def __init__(self):
        from memoire import mem
        self.mem = mem
        self.SP0 = self.mem.SP0
        self.RP0 = self.mem.RP0
    
    async def push(self, value):
        self.mem.sp -= 4
        if self.mem.sp < self.mem.here + 0x1000:
            raise MemoryError(f"Data stack overflow (sp={self.mem.sp:#x}, here={self.mem.here:#x})")
        self.mem.wpoke(self.mem.sp, value & 0xFFFFFFFF)
    
    async def pop(self):
        if self.mem.sp >= self.SP0:
            raise IndexError(f"Data stack underflow (sp={self.mem.sp:#x})")
        val = self.mem.wpeek(self.mem.sp)
        self.mem.sp += 4
        return val
    
    async def rpush(self, value):
        self.mem.rp -= 4
        if self.mem.rp < self.mem.sp:
            raise MemoryError(f"Return stack overflow (rp={self.mem.rp:#x}, sp={self.mem.sp:#x})")
        self.mem.wpoke(self.mem.rp, value)
    
    async def rpop(self):
        if self.mem.rp >= self.RP0:
            raise IndexError(f"Return stack underflow (rp={self.mem.rp:#x})")
        val = self.mem.wpeek(self.mem.rp)
        self.mem.rp += 4
        return val
    
    async def pop_string(self):
        s = ""
        while True:
            c = await self.pop()
            if c == 0:
                break
            s += chr(c & 0xFF)
        return s[::-1]
    
    def depth(self):
        return (self.SP0 - self.mem.sp) // 4
    
    def rdepth(self):
        return (self.RP0 - self.mem.rp) // 4

piles = Piles()
# fin du "piles" version "15"