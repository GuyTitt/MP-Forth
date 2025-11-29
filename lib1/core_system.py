# début du "core_system" version "41"
version = ('core_system.py', 41)

try:
    from boot import MON_DOSSIER
except ImportError:
    MON_DOSSIER = ""

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

    # Opcodes propres à core_system
    OP_RECURSE   = 200
    OP_VARIABLE  = 202
    OP_CONSTANT  = 203
    OP_WORDS     = 204
    OP_SEE       = 205
    OP_VARIABLES = 206

    async def prim_recurse():
        """Compilation d’un appel récursif au mot en cours de définition"""
        if mem.state == 0:                     # ← CORRIGÉ (double == supprimé)
            print("? RECURSE hors définition")
            return
        code_addr = mem.wpeek(mem.latest + 4)  # adresse du corps du mot courant
        mem.wpoke(mem.here, code_addr)
        mem.here += 4

    async def prim_variable():
        """Crée une variable (immédiat)"""
        name = await piles.pop_string()
        from dictionnaire import align_here
        align_here()
        create(name, OP_VARIABLE)
        mem.wpoke(mem.here, 0)                 # valeur initiale = 0
        mem.here += 4
        print(f"VARIABLE {name}")

    async def prim_constant():
        """Crée une constante (immédiat)"""
        value = await piles.pop()
        name  = await piles.pop_string()
        from dictionnaire import align_here
        align_here()
        create(name, OP_LIT)
        mem.wpoke(mem.here, value)
        mem.here += 4
        print(f"CONSTANT {name} = {value}")

    async def prim_words():
        """Affiche tous les mots triés par catégorie"""
        prim, cour, app = [], [], []
        addr = mem.latest
        while addr:
            link = mem.wpeek(addr)
            addr += 4
            fl = mem.cpeek(addr)
            length = fl & 0x7F
            immediate = bool(fl & 0x80)
            addr += 1
            name = "".join(chr(mem.cpeek(addr + i)) for i in range(length))  # ← CORRIGÉ
            code_addr = addr + length + (4 - (length + 1) % 4) % 4
            code = mem.wpeek(code_addr)
            cat = prim if code < 1000 else (cour if code == OP_LIT else app)
            cat.append(name + ("!" if immediate else ""))
            addr = link

        for titre, liste in [("PRIMITIVES", prim), ("MOTS COURANTS", cour), ("APPLICATION", app)]:
            if liste:
                print(f"\n--- {titre} ---")
                for w in sorted(liste):
                    print(f"{w:15}", end="")
                print()

    async def prim_see():
        """Décompile le mot dont le nom (terminé par 0) est sur la pile"""
        if piles.depth() == 0:
            print("? SEE : pile vide")
            return
        word = ""
        sp = mem.sp
        while sp < mem.SP0:
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
        """Liste toutes les variables et constantes définies"""
        print("\n--- VARIABLES & CONSTANTES ---")
        addr = mem.latest
        while addr:
            link = mem.wpeek(addr)
            addr += 4
            fl = mem.cpeek(addr)
            length = fl & 0x7F
            addr += 1
            name = "".join(chr(mem.cpeek(addr + i)) for i in range(length))
            code_addr = addr + length + (4 - (length + 1) % 4) % 4
            code = mem.wpeek(code_addr)
            if code == OP_VARIABLE:
                val = mem.wpeek(code_addr + 4)
                print(f"VARIABLE {name:12} = {val}  @ 0x{code_addr + 4:08X}")
            elif code == OP_LIT:
                val = mem.wpeek(code_addr + 4)
                print(f"CONSTANT {name:12} = {val}")
            addr = link

    async def prim_dot_s():
        """Affiche la pile de données"""
        depth = piles.depth()
        print(f"<{depth}>:", end=" ")
        i = mem.sp
        while i < mem.SP0:
            print(mem.wpeek(i), end=" ")
            i += 4
        print(">")

    # Enregistrement dans la table de dispatch
    dispatch.update({
        OP_RECURSE:   prim_recurse,
        OP_VARIABLE:  prim_variable,
        OP_CONSTANT:  prim_constant,
        OP_WORDS:     prim_words,
        OP_SEE:       prim_see,
        OP_VARIABLES: prim_variables,
        30:           prim_dot_s,          # .S
    })

    # Création effective des mots système
    def c(name, opcode, immediate=False):
        create(name, opcode, immediate=immediate)
        print(name, end=" ")

    print("\nCréation dictionnaire système:")
    c("EXIT", OP_EXIT, immediate=True)
    c("DUP", 1); c("DROP", 2); c("SWAP", 3); c("OVER", 4); c("ROT", 5)
    c("2DUP", 34); c("2DROP", 35); c("NIP", 36); c("TUCK", 37)
    c("+", 6); c("-", 7); c("*", 8); c("/", 9); c("MOD", 10)
    c("NEGATE", 11); c("ABS", 12)
    c("<", 111); c(">", 112); c("=", 113); c("0<", 114); c("0=", 115); c("U<", 119)
    c("@", 13); c("!", 14); c("C@", 15); c("C!", 16); c("+@", 38); c("+!", 39)
    c(".", 17); c("CR", 18); c("EMIT", 19); c("SPACE", 40); c("SPACES", 41)
    c("AND", 42); c("OR", 43); c("XOR", 44); c("NOT", 45)
    c("IF", OP_ZBRANCH, immediate=True)
    c("ELSE", OP_BRANCH, immediate=True)
    c("THEN", MARK_THEN, immediate=True)
    c("BEGIN", MARK_BEGIN, immediate=True)
    c("UNTIL", OP_ZBRANCH, immediate=True)
    c("AGAIN", OP_BRANCH, immediate=True)
    c("DO", MARK_DO, immediate=True)
    c("LOOP", MARK_LOOP, immediate=True)
    c("+LOOP", MARK_LOOP, immediate=True)
    c("I", 109); c("J", 110)
    c("WORDS", OP_WORDS)
    c(".S", 30)
    c("DEPTH", 116)
    c("SEE", OP_SEE)
    c("VARIABLES", OP_VARIABLES)
    c("RECURSE", OP_RECURSE, immediate=True)
    c("1-", 201)
    c("VARIABLE", OP_VARIABLE, immediate=True)
    c("CONSTANT", OP_CONSTANT, immediate=True)
    c("MIN", 150); c("MAX", 151)
    print()

    # Chargement du vocabulaire étendu (CREATE/DOES> etc.)
    try:
        import core_system1
    except ImportError:
        print("core_system1.py absent – mots CREATE/DOES> non chargés")

    print("core_system.py v41 chargé – RECURSE corrigé + parenthèse fermante")
    __core_sys_done = True

# fin du "core_system" version "41"