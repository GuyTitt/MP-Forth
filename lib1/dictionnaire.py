# début du "dictionnaire" version "31"
version = ('dictionnaire.py', 31)
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
            print(f"[ERREUR] find(): >200 itérations")
            return None, False
        
        if addr < 0 or addr >= len(mem.ram) - 8:
            print(f"[ERREUR] find(): adresse invalide {addr:#x}")
            return None, False
        
        try:
            link = mem.wpeek(addr)
        except Exception as e:
            print(f"[ERREUR] find(): lecture link @ {addr:#x} : {e}")
            return None, False
        
        addr += 4
        fl = mem.cpeek(addr)
        length = fl & 0x7F
        immediate = bool(fl & 0x80)
        addr += 1
        wname = "".join(chr(mem.cpeek(addr + i)) for i in range(length))
        code_addr = addr + length + (4 - (length + 1) % 4) % 4
        
        if code_addr >= len(mem.ram) - 4:
            print(f"[ERREUR] code_addr {code_addr:#x} hors limites")
            return None, False
        
        try:
            code = mem.wpeek(code_addr)
        except Exception as e:
            print(f"[ERREUR] lecture code @ {code_addr:#x} : {e}")
            return None, False
        
        if wname.upper() == name:
            return code, immediate
        
        addr = link
        if addr == 0:
            break
    
    return None, False

def find_word_by_code(code):
    """Trouve le nom d'un mot à partir de son opcode"""
    addr = mem.latest
    
    while addr:
        link = mem.wpeek(addr)
        addr += 4
        fl = mem.cpeek(addr)
        length = fl & 0x7F
        addr += 1
        name = "".join(chr(mem.cpeek(addr + i)) for i in range(length))
        code_addr = addr + length + (4 - (length + 1) % 4) % 4
        word_code = mem.wpeek(code_addr)
        
        if word_code == code:
            return name
        
        addr = link
        if addr == 0:
            break
    
    return None

async def see_word(name):
    """Décompile un mot avec noms lisibles"""
    code, immediate = find(name.upper())
    if code is None:
        print(f"? {name} introuvable")
        return
    
    if code < 1000:
        print(f"{name} est une primitive (opcode {code})")
        return
    
    # Mot COLON
    print(f"\n{name}{'*' if immediate else ''}: ", end="")
    ip = code
    tokens = []
    
    while ip < mem.here and len(tokens) < 50:  # Limite sécurité
        try:
            opc = mem.wpeek(ip)
            ip += 4
            
            if opc == 0:  # EXIT
                tokens.append("EXIT")
                break
            elif opc == 21:  # LIT
                val = mem.wpeek(ip)
                ip += 4
                tokens.append(str(val))
            else:
                # Chercher le nom du mot
                word_name = find_word_by_code(opc)
                if word_name:
                    tokens.append(word_name)
                else:
                    tokens.append(f"[{opc}]")
        except:
            tokens.append("[ERR]")
            break
    
    # Afficher avec retours à la ligne tous les 10 mots
    for i, tok in enumerate(tokens):
        print(tok, end=" ")
        if (i + 1) % 10 == 0 and i < len(tokens) - 1:
            print("\n  ", end="")
    print()

# fin du "dictionnaire" version "31"