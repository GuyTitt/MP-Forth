# début du "memoire" version "14"
print("début de memoire.py v14")
version = ('memoire.py', 14)

class Memoire:
    def __init__(self):
        self.ram = bytearray(512 * 1024)
        self.here = 256
        self.latest = 0
        self.state = 0
        self.ip = 0
        # CORRECTION: adresses cohérentes avec piles.py pour 512KB RAM
        self.sp = 0x7FFF0    # 524272 (top of data stack)
        self.SP0 = self.sp
        self.rp = 0x7FF00    # 524032 (top of return stack)
        self.RP0 = self.rp
    
    def wpoke(self, addr, val):
        if addr + 3 >= len(self.ram):
            raise MemoryError(f"wpoke overflow @ {addr:#x}")
        # CORRECTION: MicroPython ne supporte pas signed=False
        self.ram[addr:addr+4] = val.to_bytes(4, 'little')
    
    def wpeek(self, addr):
        if addr + 3 >= len(self.ram):
            raise MemoryError(f"wpeek overflow @ {addr:#x}")
        return int.from_bytes(self.ram[addr:addr+4], 'little')
    
    def cpoke(self, addr, val):
        if addr >= len(self.ram):
            raise MemoryError(f"cpoke overflow @ {addr:#x}")
        self.ram[addr] = val & 0xFF
    
    def cpeek(self, addr):
        if addr >= len(self.ram):
            raise MemoryError(f"cpeek overflow @ {addr:#x}")
        return self.ram[addr]
    
    def reset_memory(self):
        self.here = 256
        self.latest = 0
        self.state = 0
        self.ip = 0
        self.sp = self.SP0
        self.rp = self.RP0

mem = Memoire()
print(f"fin de memoire.py v14 - SP0={mem.SP0:#x}, RP0={mem.RP0:#x}")
# fin du "memoire" version "14"