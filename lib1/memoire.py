# début du "memoire" version "17"
version = ('memoire.py', 17)
import gc

class Memoire:
    def __init__(self):
        # CORRECTION: Détection automatique de la RAM disponible
        gc.collect()
        ram_libre = gc.mem_free()
        
        # Tenter 512KB, puis 256KB, puis 128KB si échec
        for taille_kb in [512, 256, 128, 64]:
            try:
                self.ram = bytearray(taille_kb * 1024)
                print(f"RAM Forth allouée: {taille_kb}KB (libre: {ram_libre//1024}KB)")
                break
            except MemoryError:
                continue
        else:
            raise MemoryError("Impossible d'allouer RAM Forth (minimum 64KB requis)")
        
        self.here = 256
        self.latest = 0
        self.state = 0
        self.ip = 0
        
        # Calculer adresses piles en fonction de la taille allouée
        taille = len(self.ram)
        self.sp = taille - 16    # Top pile données
        self.SP0 = self.sp
        self.rp = taille - 272   # Top pile retour (256 bytes plus bas)
        self.RP0 = self.rp
        
        print(f"  Zones: Dict=0x100-0x{self.here:x}, Piles=0x{self.rp:x}-0x{self.sp:x}")
    
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

# fin du "memoire" version "17"