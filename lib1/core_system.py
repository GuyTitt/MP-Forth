# début du "core_system" version "47"
version = ('core_system.py', 47)

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

    OP_RECURSE   = 200
    OP_WORDS     = 204
    OP_SEE       = 205
    OP_VARIABLES = 206

    async def prim_recurse():
        if mem.state == 0:
            print("? RECURSE hors définition")
            return
        code_addr = mem.wpeek(mem.latest + 4)
        mem.wpoke(mem.here, code_addr)
        mem.here += 4

    async def prim_words():
        categories = {
            "PRIMITIVES": list(range(1, 200)),
            "SYSTEM": list(range(200, 300)),
            "ADVANCED": list(range(300, 400)),
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
        
        user_words = [n + ("!" if all_words[n]['imm'] else "") 
                      for n, i in all_words.items() if i['code'] >= 1000]
        if user_words:
            print(f"\nUSER: ", end="")
            print(" ".join(sorted(user_words)))
        print()

    async def prim_see():
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
            # OP_VARIABLE=202, OP_CONSTANT=21 (OP_LIT)
            if code == 202:
                val = mem.wpeek(code_addr + 4)
                print(f"VARIABLE {name:12} = {val}  @ 0x{code_addr + 4:08X}")
            elif code == 21:
                val = mem.wpeek(code_addr + 4)
                print(f"CONSTANT {name:12} = {val}")
            addr = link

    async def prim_dot_s():
        depth = piles.depth()
        print(f"<{depth}>:", end=" ")
        i = mem.sp
        while i < piles.SP0:
            print(mem.wpeek(i), end=" ")
            i += 4
        print(">")

    dispatch.update({
        OP_RECURSE:   prim_recurse,
        OP_WORDS:     prim_words,
        OP_SEE:       prim_see,
        OP_VARIABLES: prim_variables,
        30:           prim_dot_s,
    })

    def c(name, opcode, immediate=False):
        create(name, opcode, immediate=immediate)
        print(name, end=" ")

    print("\nCréation dictionnaire système:")
    c("EXIT", OP_EXIT, immediate=True)
    c("DUP", 1); c("DROP", 2); c("SWAP", 3); c("OVER", 4); c("ROT", 5)
    c("2DUP", 34); c("2DROP", 35); c("NIP", 36); c("TUCK", 37)
    c("+", 6); c("-", 7); c("*", 8); c("/", 9); c("MOD", 10)
    c("NEGATE", 11); c("ABS", 12); c("1+", 120); c("1-", 201); c("2*", 121); c("2/", 122)
    c("<", 111); c(">", 112); c("=", 113); c("<>", 123); c("0<", 114); c("0=", 115)
    c("0>", 124); c("U<", 119)
    c("@", 13); c("!", 14); c("C@", 15); c("C!", 16); c("+@", 38); c("+!", 39)
    c(".", 17); c("CR", 18); c("EMIT", 19); c("SPACE", 40); c("SPACES", 41)
    c("AND", 42); c("OR", 43); c("XOR", 44); c("NOT", 45); c("INVERT", 125)
    c("LSHIFT", 126); c("RSHIFT", 127)
    c("IF", OP_ZBRANCH, immediate=True)
    c("ELSE", OP_BRANCH, immediate=True)
    c("THEN", MARK_THEN, immediate=True)
    c("BEGIN", MARK_BEGIN, immediate=True)
    c("UNTIL", OP_ZBRANCH, immediate=True)
    c("WHILE", OP_ZBRANCH, immediate=True)
    c("REPEAT", OP_BRANCH, immediate=True)
    c("AGAIN", OP_BRANCH, immediate=True)
    c("DO", MARK_DO, immediate=True)
    c("LOOP", MARK_LOOP, immediate=True)
    c("+LOOP", MARK_LOOP, immediate=True)
    c("I", 109); c("J", 110); c("UNLOOP", 128)
    c("WORDS", OP_WORDS)
    c(".S", 30); c("DEPTH", 116)
    c("SEE", OP_SEE); c("VARIABLES", OP_VARIABLES)
    c("RECURSE", OP_RECURSE, immediate=True)
    c("MIN", 150); c("MAX", 151)
    # VARIABLE et CONSTANT retirés - gérés dans main.py
    c("HERE", 129); c("ALLOT", 130); c(",", 131); c("C,", 132)
    print()

    try:
        import core_system1
    except ImportError:
        print("core_system1.py absent – mots CREATE/DOES> non chargés")

    print(f"core_system.py v{version[1]} chargé")
    __core_sys_done = True

# fin du "core_system" version "47"