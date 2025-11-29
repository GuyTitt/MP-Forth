# début du "dictionnaire" version "25"
version = ('dictionnaire.py', 25)

from memoire import mem

def align_here():
    """Alignement de here sur 4 octets"""
    mem.here = (mem.here + 3) & ~3

def create(name, code, immediate=False):
    """Création d’un mot dans le dictionnaire"""
    align_here()
    mem.wpoke(mem.here, mem.latest)        # link
    mem.here += 4
    length = len(name)
    flags = 0x80 if immediate else 0
    mem.cpoke(mem.here, length | flags)     # flags+len
    mem.here += 1
    for c in name:
        mem.cpoke(mem.here, ord(c))
        mem.here += 1
    align_here()
    mem.wpoke(mem.here, code)               # code field
    mem.here += 4
    mem.latest = mem.here - 4

def create_colon_word(name, body_addr):
    """Création d’un mot colon (: … ;)"""
    create(name, body_addr)

def find(name):
    """Recherche d’un mot → (code, immediate)"""
    addr = mem.latest
    name = name.upper()
    while addr:
        link = mem.wpeek(addr)
        addr += 4
        fl = mem.cpeek(addr)
        length = fl & 0x7F
        immediate = bool(fl & 0x80)
        addr += 1
        wname = ""
        for i in range(length):
            wname += chr(mem.cpeek(addr + i))
        if wname.upper() == name:
            code_addr = addr + length + (4 - (length + 1) % 4) % 4
            code = mem.wpeek(code_addr)
            return code, immediate
        addr = link
    return None, False

async def see_word(name):
    """Décompilation complète d’un mot"""
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
            wname = "".join(chr(mem.cpeek(a + i)) for i in range(length))  # ← CORRIGÉ ICI
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

print("dictionnaire.py v25 chargé – syntaxe corrigée (parenthèse manquante)")

# fin du "dictionnaire" version "25"