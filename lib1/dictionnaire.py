# début du "dictionnaire" version "30"
version = ('dictionnaire.py', 30)
from memoire import mem

def align_here():
    mem.here = (mem.here + 3) & ~3

def create(name, code, immediate=False):
    align_here()
    header_start = mem.here
    mem.wpoke(mem.here, mem.latest)
    mem.here += 4
    length = len(name)
    flags = 0x80 if immediate else 0
    mem.cpoke(mem.here, length | flags)
    mem.here += 1
    for c in name:
        mem.cpoke(mem.here, ord(c))
        mem.here += 1
    align_here()
    mem.wpoke(mem.here, code)
    mem.here += 4
    mem.latest = header_start

def create_colon_word(name, body_addr):
    align_here()
    header_size = 4 + 1 + len(name)
    header_size = (header_size + 3) & ~3
    header_size += 4
    code_addr = mem.here + header_size
    create(name, code_addr)

def find(name):
    name = name.upper()
    addr = mem.latest
    count = 0
    
    while addr:
        count += 1
        if count > 200:
            print(f"[ERROR] find(): >200 itérations")
            return None, False
        
        if addr < 0 or addr >= len(mem.ram) - 8:
            print(f"[ERROR] find(): adresse invalide {addr:#x}")
            return None, False
        
        try:
            link = mem.wpeek(addr)
        except Exception as e:
            print(f"[ERROR] find(): lecture link @ {addr:#x} : {e}")
            return None, False
        
        addr += 4
        fl = mem.cpeek(addr)
        length = fl & 0x7F
        immediate = bool(fl & 0x80)
        addr += 1
        wname = "".join(chr(mem.cpeek(addr + i)) for i in range(length))
        code_addr = addr + length + (4 - (length + 1) % 4) % 4
        
        if code_addr >= len(mem.ram) - 4:
            print(f"[ERROR] code_addr {code_addr:#x} hors limites")
            return None, False
        
        try:
            code = mem.wpeek(code_addr)
        except Exception as e:
            print(f"[ERROR] lecture code @ {code_addr:#x} : {e}")
            return None, False
        
        if wname.upper() == name:
            return code, immediate
        
        addr = link
        if addr == 0:
            break
    
    return None, False

async def see_word(name):
    code, immediate = find(name.upper())
    if code is None:
        print(f"? {name} introuvable")
        return
    if code < 1000:
        print(f"{name} est une primitive (opcode {code})")
        return
    print(f"{name}{'*' if immediate else ''}: ", end="")
    ip = code
    while True:
        opc = mem.wpeek(ip)
        ip += 4
        if opc == 0:
            print("EXIT")
            break
        if opc == 21:
            val = mem.wpeek(ip)
            ip += 4
            print(val, end=" ")
            continue
        found = False
        a = mem.latest
        while a:
            link = mem.wpeek(a)
            a += 4
            fl = mem.cpeek(a)
            length = fl & 0x7F
            a += 1
            wname = "".join(chr(mem.cpeek(a + i)) for i in range(length))
            code_addr = a + length + (4 - (length + 1) % 4) % 4
            wcode = mem.wpeek(code_addr)
            if wcode == opc:
                print(wname, end=" ")
                found = True
                break
            a = link
        if not found:
            print(f"[{opc}]", end=" ")
    print()

# fin du "dictionnaire" version "30"