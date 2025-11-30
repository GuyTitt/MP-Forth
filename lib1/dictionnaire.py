# début du "dictionnaire" version "27"
version = ('dictionnaire.py', 27)
from memoire import mem

DEBUG = True  # Activer temporairement

def trace(msg):
    if DEBUG:
        print(f"[DICT] {msg}")

def align_here():
    """Alignement de here sur 4 octets"""
    mem.here = (mem.here + 3) & ~3

def create(name, code, immediate=False):
    """Création d'un mot dans le dictionnaire"""
    trace(f"create('{name}', code={code}, imm={immediate}) @ here={mem.here:#x}")
    align_here()
    
    # Sauvegarder l'adresse du début du header
    header_start = mem.here
    
    # Link vers previous
    mem.wpoke(mem.here, mem.latest)
    trace(f"  link={mem.latest:#x} written @ {mem.here:#x}")
    mem.here += 4
    
    # Flags + length
    length = len(name)
    flags = 0x80 if immediate else 0
    mem.cpoke(mem.here, length | flags)
    mem.here += 1
    
    # Name
    for c in name:
        mem.cpoke(mem.here, ord(c))
        mem.here += 1
    
    # Align
    align_here()
    
    # Code field
    mem.wpoke(mem.here, code)
    trace(f"  code={code} written @ {mem.here:#x}")
    mem.here += 4
    
    # Update latest → POINTE SUR LE HEADER, PAS LE CODE !
    mem.latest = header_start
    trace(f"  latest={mem.latest:#x} (header_start), here now={mem.here:#x}\n")

def create_colon_word(name, body_addr):
    """Création d'un mot colon (: … ;)"""
    create(name, body_addr)

def find(name):
    """Recherche d'un mot → (code, immediate)"""
    name = name.upper()
    trace(f"find('{name}') starting @ latest={mem.latest:#x}")
    
    addr = mem.latest
    count = 0
    
    while addr:
        count += 1
        if count > 200:  # Protection contre boucle infinie
            print(f"[ERROR] find(): trop d'itérations (>200), corruption dictionnaire")
            return None, False
        
        trace(f"  iter {count}: checking header @ {addr:#x}")
        
        # Vérifier que addr est valide
        if addr < 0 or addr >= len(mem.ram) - 8:
            print(f"[ERROR] find(): adresse invalide {addr:#x}")
            return None, False
        
        # Link
        try:
            link = mem.wpeek(addr)
            trace(f"    link={link:#x}")
        except Exception as e:
            print(f"[ERROR] find(): lecture link @ {addr:#x} : {e}")
            return None, False
        
        addr += 4
        
        # Flags
        fl = mem.cpeek(addr)
        length = fl & 0x7F
        immediate = bool(fl & 0x80)
        trace(f"    flags={fl:#x}, len={length}, imm={immediate}")
        addr += 1
        
        # Name
        wname = ""
        for i in range(length):
            wname += chr(mem.cpeek(addr + i))
        trace(f"    name='{wname}'")
        
        # Code field
        code_addr = addr + length + (4 - (length + 1) % 4) % 4
        
        if code_addr >= len(mem.ram) - 4:
            print(f"[ERROR] code_addr {code_addr:#x} hors limites")
            return None, False
        
        try:
            code = mem.wpeek(code_addr)
            trace(f"    code={code} @ {code_addr:#x}")
        except Exception as e:
            print(f"[ERROR] lecture code @ {code_addr:#x} : {e}")
            return None, False
        
        if wname.upper() == name:
            trace(f"  FOUND: returning ({code}, {immediate})\n")
            return code, immediate
        
        addr = link
        if addr == 0:
            break
    
    trace(f"  NOT FOUND\n")
    return None, False

async def see_word(name):
    """Décompilation complète d'un mot"""
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
        if opc == 21:  # LIT
            val = mem.wpeek(ip)
            ip += 4
            print(val, end=" ")
            continue
        # Recherche du nom
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

print("dictionnaire.py v27 chargé – latest pointe sur HEADER corrigé")
# fin du "dictionnaire" version "27"