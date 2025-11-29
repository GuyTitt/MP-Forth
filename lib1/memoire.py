# début du "memoire" version "12"
print("début de memoire.py v12")
version = ('memoire.py', 12)
class Memoire:
    def __init__(self):
        self.ram = bytearray(512 * 1024)
        self.here = 256
        self.latest = 0
        self.state = 0
        self.ip = 0
        self.sp = 131072
        self.SP0 = self.sp
        self.rp = 196608
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
print("fin de memoire.py v12")
# fin du "memoire" version "12"