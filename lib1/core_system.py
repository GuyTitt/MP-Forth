# début du "core_system" version "51"
version = ('core_system.py', 51)

"""
VOCABULAIRE SYSTÈME - Primitives Python (à transcoder en assembleur)

Ces ~20 primitives forment le noyau minimal qui sera réécrit en assembleur.
Tout le reste (stdlib.v) sera défini EN FORTH et compilé au démarrage.
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
        MARK_THEN, MARK_BEGIN, MARK_DO, MARK_LOOP,
        OP_MIN, OP_MAX, OP_1MINUS
    )

    # Opcodes système
    OP_RECURSE   = 200
    OP_DOVAR     = 202
    OP_WORDS     = 204
    OP_SEE       = 205
    OP_VARIABLES = 206

    # ==========================================
    # PRIMITIVES SYSTÈME
    # ==========================================

    async def prim_recurse():
        """RECURSE - Compile appel récursif"""
        if mem.state == 0:
            print("? RECURSE hors définition")
            return
        code_addr = mem.wpeek(mem.latest + 4)
        mem.wpoke(mem.here, code_addr)
        mem.here += 4

    async def prim_dovar():
        """DOVAR - Comportement VARIABLE
        
        Empile l'adresse de stockage.
        mem.ip pointe déjà sur la zone de données.
        """
        await piles.push(mem.ip)

    async def prim_words():
        """WORDS - Affiche tous les mots par catégorie"""
        categories = {
            "PRIMITIVES": list(range(1, 200)),
            "SYSTEM": list(range(200, 300)),
            "ADVANCED": list(range(300, 400)),
            "HARDWARE": list(range(400, 500)),
        }
        
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
        
        for cat_name, opcodes in categories.items():
            words_in_cat = []
            for name, info in all_words.items():
                if info['code'] in opcodes:
                    marker = "!" if info['imm'] else ""
                    words_in_cat.append(name + marker)
            if words_in_cat:
                print(f"\n{cat_name}: ", end="")
                print(" ".join(sorted(words_in_cat)))
        
        # Mots utilisateur (définis en Forth)
        user_words = []
        for name, info in all_words.items():
            if info['code'] >= 1000:
                marker = "!" if info['imm'] else ""
                user_words.append(name + marker)
        
        if user_words:
            print(f"\nFORTH (stdlib.v): ", end="")
            print(" ".join(sorted(user_words)))
        print()

    async def prim_see():
        """SEE - Usage interne (pas pour utilisateur)"""
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
        """VARIABLES - Liste VARIABLE et CONSTANT"""
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
            
            if code == 202:  # VARIABLE
                val_addr = code_addr + 4
                val = mem.wpeek(val_addr)
                variables.append((name, val, val_addr))
            elif code == 21:  # CONSTANT
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
        """.S - Affiche pile sans la modifier"""
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
        OP_RECURSE:   prim_recurse,
        OP_DOVAR:     prim_dovar,
        OP_WORDS:     prim_words,
        OP_SEE:       prim_see,
        OP_VARIABLES: prim_variables,
        30:           prim_dot_s,
    })

    # ==========================================
    # CRÉATION DICTIONNAIRE (primitives seulement)
    # ==========================================

    def c(name, opcode, immediate=False):
        """Helper pour créer un mot primitif"""
        create(name, opcode, immediate=immediate)
        print(name, end=" ")

    print("\n=== VOCABULAIRE PRIMITIF (Python → Assembleur) ===")
    
    # Pile de données
    c("DUP", 1); c("DROP", 2); c("SWAP", 3); c("OVER", 4); c("ROT", 5)
    c("2DUP", 34); c("2DROP", 35)
    
    # Arithmétique
    c("+", 6); c("-", 7); c("*", 8); c("/", 9); c("MOD", 10)
    c("1+", 120); c("1-", 201)
    
    # Comparaisons
    c("<", 111); c(">", 112); c("=", 113); c("0=", 115)
    
    # Mémoire
    c("@", 13); c("!", 14); c("C@", 15); c("C!", 16)
    
    # I/O
    c(".", 17); c("CR", 18); c("EMIT", 19)
    
    # Logique
    c("AND", 42); c("OR", 43); c("XOR", 44); c("NOT", 45)
    
    # Structures contrôle (marqueurs pour compilation)
    c("IF", OP_ZBRANCH, immediate=True)
    c("THEN", MARK_THEN, immediate=True)
    c("ELSE", OP_BRANCH, immediate=True)
    c("BEGIN", MARK_BEGIN, immediate=True)
    c("UNTIL", OP_ZBRANCH, immediate=True)
    c("AGAIN", OP_BRANCH, immediate=True)
    c("DO", MARK_DO, immediate=True)
    c("LOOP", MARK_LOOP, immediate=True)
    c("I", 109)
    
    # Système
    c("EXIT", OP_EXIT, immediate=True)
    c("WORDS", OP_WORDS)
    c(".S", 30)
    c("SEE", OP_SEE)
    c("VARIABLES", OP_VARIABLES)
    c("HERE", 129); c(",", 131)
    
    print(f"\n\n{len([k for k in dispatch.keys() if k < 200])} primitives créées")
    print("Le reste sera défini en FORTH dans stdlib.v\n")

    # Charger mots avancés (CREATE/DOES>)
    try:
        import core_system1
    except ImportError:
        print("core_system1.py absent – CREATE/DOES> non disponibles")

    print(f"core_system.py v{version[1]} chargé\n")
    __core_sys_done = True

# fin du "core_system" version "51"
