# début du "memoire" version "15"
version = ('memoire.py', 15)

class Memoire:
    def __init__(self):
        self.ram = bytearray(512 * 1024)
        self.here = 256
        self.latest = 0
        self.state = 0
        self.ip = 0
        self.sp = 0x7FFF0
        self.SP0 = self.sp
        self.rp = 0x7FF00
        self.RP0 = self.rp
    
    def wpoke(self, addr, val):
        if addr + 3 >= len(self.ram):
            raise MemoryError(f"wpoke overflow @ {addr:#x}")
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
# fin du "memoire" version "15"