# début du "piles" version "9"
from memoire import mem
import uasyncio as asyncio

TRACE = False  # Désactiver pour version de production

def trace(msg):
    if TRACE:
        print(f"[PILES] {msg}")

class Piles:
    async def push(self, x):
        """Empiler une valeur sur la data stack"""
        if mem.sp < 256:
            raise MemoryError(f"Data stack overflow (sp={mem.sp})")
        mem.sp -= 4
        val_masked = x & 0xFFFFFFFF
        mem.wpoke(mem.sp, val_masked)
        trace(f"push({x}) -> sp={mem.sp}")
    
    async def pop(self):
        """Dépiler une valeur de la data stack"""
        if mem.sp >= mem.SP0:
            raise IndexError(f"Data stack underflow (sp={mem.sp}, SP0={mem.SP0})")
        v = mem.wpeek(mem.sp)
        trace(f"pop() -> {v} (sp={mem.sp})")
        mem.sp += 4
        return v

piles = Piles()

version = ('piles.py', 9)
print(f"piles.py v{version[1]} – stable")
# fin du "piles" version "9"