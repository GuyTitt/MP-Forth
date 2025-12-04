# début du "core_system" version "55"
version = ('core_system.py', 55)

"""
VOCABULAIRE PRIMITIF MINIMAL - 21 primitives Python → Assembleur
"""

MON_DOSSIER = globals().get('MON_DOSSIER', '')

try:
    __core_sys_done
except NameError:
    __core_sys_done = False

if not __core_sys_done:
    import uasyncio as asyncio
    from memoire import mem
    from dictionnaire import create, find, see_word
    from piles import piles

    from core_primitives import (
        dispatch, OP_EXIT, OP_LIT, OP_ZBRANCH, OP_BRANCH,
        MARK_THEN, MARK_BEGIN, MARK_DO, MARK_LOOP
    )

    # Opcodes système
    OP_TOR       = 203  # >R
    OP_FROMR     = 207  # R>
    OP_DOVAR     = 202  # VARIABLE
    OP_WORDS     = 204
    OP_SEE       = 205
    OP_VARIABLES = 206

    # ==========================================
    # PRIMITIVES SYSTÈME
    # ==========================================

    async def prim_tor():
        """>R"""
        val = await piles.pop()
        await piles.rpush(val)

    async def prim_fromr():
        """R>"""
        val = await piles.rpop()
        await piles.push(val)

    async def prim_dovar():
        """DOVAR - Comportement VARIABLE"""
        await piles.push(mem.ip)

    async def prim_words():
        """WORDS - Affiche vocabulaire organisé"""
        all_words = {}
        addr = mem.latest
        
        while addr:
            link = mem.wpeek(addr)
            addr += 4
            fl = mem.cpeek(addr)
            length = fl & 0x7F
            immediate = bool(fl & 0x80)
            addr += 1
            name = "".join(chr(mem.cpeek(addr + i)) for i in range(length))
            code_addr = addr + length + (4 - (length + 1) % 4) % 4
            code = mem.wpeek(code_addr)
            all_words[name] = {'code': code, 'imm': immediate}
            addr = link
        
        # Catégoriser intelligemment
        primitives = []
        forth_base = []
        forth_hardware = []
        forth_app = []
        
        # Mots hardware connus
        hardware_keywords = ['PIN', 'GPIO', 'NEO', 'TICKS', 'MS', 'US']
        
        # Mots applicatifs connus
        app_keywords = ['LED', 'BUTTON', 'BLINK', 'TASK', 'PAUSE', 'SLEEP',
                        'FIB', 'SQRT', 'GCD', 'RANDOM', 'SORT']
        
        for name, info in all_words.items():
            marker = "!" if info['imm'] else ""
            word = name + marker
            
            # Primitives : opcode < 210
            if info['code'] < 210:
                primitives.append(word)
            # Hardware : contient mot-clé hardware
            elif any(kw in name for kw in hardware_keywords):
                forth_hardware.append(word)
            # Applicatif : contient mot-clé app
            elif any(kw in name for kw in app_keywords):
                forth_app.append(word)
            # Base : tout le reste (2DUP, MOD, IF, etc.)
            else:
                forth_base.append(word)
        
        print(f"\nPRIMITIVES (21 → ASM): ", end="")
        print(" ".join(sorted(primitives)))
        
        if forth_base:
            print(f"\nFORTH BASE: ", end="")
            print(" ".join(sorted(forth_base)))
        
        if forth_hardware:
            print(f"\nFORTH HARDWARE: ", end="")
            print(" ".join(sorted(forth_hardware)))
        
        if forth_app:
            print(f"\nFORTH APPLICATIF: ", end="")
            print(" ".join(sorted(forth_app)))
        
        print()

    async def prim_see():
        """SEE interne"""
        if piles.depth() == 0:
            print("? SEE : pile vide")
            return
        word = ""
        sp = mem.sp
        while sp < piles.SP0:
            c = mem.wpeek(sp) & 0xFF
            if c == 0:
                break
            word += chr(c)
            sp += 4
        await piles.pop()
        if not word.strip():
            print("? SEE : mot vide")
            return
        await see_word(word.strip())

    async def prim_variables():
        """VARIABLES"""
        print("\n--- VARIABLES & CONSTANTES ---")
        
        addr = mem.latest
        variables = []
        constants = []
        
        while addr:
            link = mem.wpeek(addr)
            addr += 4
            fl = mem.cpeek(addr)
            length = fl & 0x7F
            addr += 1
            name = "".join(chr(mem.cpeek(addr + i)) for i in range(length))
            code_addr = addr + length + (4 - (length + 1) % 4) % 4
            code = mem.wpeek(code_addr)
            
            if code == 202:
                val_addr = code_addr + 4
                val = mem.wpeek(val_addr)
                variables.append((name, val, val_addr))
            elif code == 21:
                val = mem.wpeek(code_addr + 4)
                constants.append((name, val))
            
            addr = link
        
        for name, val, addr in sorted(variables):
            print(f"VARIABLE {name:12} = {val:6}  @ 0x{addr:08X}")
        
        for name, val in sorted(constants):
            print(f"CONSTANT {name:12} = {val:6}")
        
        if not variables and not constants:
            print("Aucune variable ou constante définie.")
        print()

    async def prim_dot_s():
        """.S"""
        depth = piles.depth()
        print(f"<{depth}>:", end=" ")
        i = mem.sp
        while i < piles.SP0:
            print(mem.wpeek(i), end=" ")
            i += 4
        print()

    # ==========================================
    # ENREGISTREMENT DISPATCH
    # ==========================================

    dispatch.update({
        OP_TOR:       prim_tor,
        OP_FROMR:     prim_fromr,
        OP_DOVAR:     prim_dovar,
        OP_WORDS:     prim_words,
        OP_SEE:       prim_see,
        OP_VARIABLES: prim_variables,
        30:           prim_dot_s,
    })

    # ==========================================
    # CRÉATION DICTIONNAIRE MINIMAL (21 primitives)
    # ==========================================

    def c(name, opcode, immediate=False):
        create(name, opcode, immediate=immediate)
        print(name, end=" ")

    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║ VOCABULAIRE PRIMITIF - 21 mots Python → Assembleur            ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    # Pile (5)
    c("DUP", 1); c("DROP", 2); c("SWAP", 3); c("OVER", 4); c("ROT", 5)
    
    # Arithmétique (4)
    c("+", 6); c("-", 7); c("*", 8); c("/", 9)
    
    # Comparaisons (2)
    c("<", 111); c("=", 113)
    
    # Mémoire (4)
    c("@", 13); c("!", 14); c("C@", 15); c("C!", 16)
    
    # Pile retour (2)
    c(">R", OP_TOR); c("R>", OP_FROMR)
    
    # I/O (2)
    c("EMIT", 19); c(".", 17)
    
    # Structures (marqueurs compilation)
    print("\n\nMarqueurs:", end=" ")
    c("IF", OP_ZBRANCH, immediate=True)
    c("THEN", MARK_THEN, immediate=True)
    c("ELSE", OP_BRANCH, immediate=True)
    c("BEGIN", MARK_BEGIN, immediate=True)
    c("UNTIL", OP_ZBRANCH, immediate=True)
    c("AGAIN", OP_BRANCH, immediate=True)
    c("DO", MARK_DO, immediate=True)
    c("LOOP", MARK_LOOP, immediate=True)
    
    # Système
    print("\n\nSystème:", end=" ")
    c("EXIT", OP_EXIT, immediate=True)
    c("WORDS", OP_WORDS)
    c(".S", 30)
    c("SEE", OP_SEE)
    c("VARIABLES", OP_VARIABLES)
    
    print(f"\n\n✓ 21 primitives + marqueurs + système")
    print(f"✓ stdlib_minimal.v v1.1 : mots manquants corrigés\n")
    
    print(f"core_system.py v{version[1]} chargé\n")
    __core_sys_done = True

# fin du "core_system" version "55"