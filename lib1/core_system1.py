# début du "core_system1" version "1"
version = ('core_system1.py', 1)

try:
    __core_sys1_done
except NameError:
    __core_sys1_done = False

if not __core_sys1_done:
    from memoire import mem
    from dictionnaire import create
    from piles import piles
    import uasyncio as asyncio

    from core_primitives import dispatch, OP_EXIT, OP_LIT

    # Opcodes réservés pour core_system1
    OP_CREATE   = 300
    OP_DOES      = 301
    OP_BUILD     = 302
    OP_VOCABULARY = 303
    OP_FORGET    = 304
    OP_FIND      = 305
    OP_COMPILE   = 306
    OP_EXECUTE   = 307
    OP_IMMEDIATE = 308
    OP_BRACKET   = 309   # [
    OP_RBRACKET  = 310   # ]
    OP_COMPBRACK = 311   # [COMPILE]
    OP_TICK      = 312   # '
    OP_NUMBER    = 313   # # <# #> #S

    async def prim_create():
        name = await piles.pop_string()
        from dictionnaire import align_here
        align_here()
        create(name, OP_CREATE)
        mem.wpoke(mem.here, 0)  # placeholder DOES>
        mem.here += 4
        print(f"CREATE {name}")

    async def prim_does():
        if mem.state == 0:
            print("? DOES> hors définition")
            return
        addr = mem.wpeek(mem.latest + 4)
        mem.wpoke(addr, mem.here)

    async def prim_build():
        await prim_create()
        mem.state = 1

    async def prim_vocabulary():
        name = await piles.pop_string()
        create(name, OP_VOCABULARY)
        print(f"VOCABULARY {name}")

    async def prim_forget():
        name = await piles.pop_string()
        from dictionnaire import find
        addr, _ = find(name.upper())
        if addr is None:
            print(f"? {name} introuvable")
            return
        mem.latest = mem.wpeek(addr - 4)  # relink
        print(f"FORGET {name}")

    async def prim_find():
        name = await piles.pop_string()
        from dictionnaire import find
        code, imm = find(name.upper())
        await piles.push(code if code is not None else 0)
        await piles.push(-1 if code is not None else 0)

    async def prim_compile():
        word = await piles.pop_string()
        from dictionnaire import find
        code, _ = find(word.upper())
        if code is None:
            print(f"? {word} inconnu")
            return
        mem.wpoke(mem.here, code)
        mem.here += 4

    async def prim_execute():
        addr = await piles.pop()
        if addr < 1000:
            await dispatch[addr]()
        else:
            mem.ip = addr
            await execute_colon(addr)

    async def prim_immediate():
        if mem.latest:
            addr = mem.latest - 3  # flags byte
            fl = mem.cpeek(addr)
            mem.cpoke(addr, fl | 0x80)

    async def prim_bracket():
        mem.state = 0

    async def prim_rbracket():
        mem.state = 1

    async def prim_compbrack():
        word = await piles.pop_string()
        from dictionnaire import find
        code, _ = find(word.upper())
        if code is None:
            print(f"? {word} inconnu")
            return
        mem.wpoke(mem.here, code)
        mem.here += 4

    async def prim_tick():
        import utime
        line = utime.ticks_ms()  # placeholder
        # à implémenter proprement plus tard
        await piles.push(0)

    # Formatage numérique
    async def prim_number():
        await piles.push(35)  # #
    async def prim_hold():
        await piles.push(60)   # <
    async def prim_sign():
        await piles.push(62)  # >
    async def prim_numbers():
        await piles.push(83)  # S

    dispatch.update({
        OP_CREATE: prim_create,
        OP_DOES: prim_does,
        350: prim_vocabulary,
        351: prim_forget,
        352: prim_find,
        353: prim_compile,
        354: prim_execute,
        355: prim_immediate,
        356: prim_bracket,
        357: prim_rbracket,
        358: prim_compbrack,
        359: prim_tick,
        360: prim_number,
        361: prim_hold,
        362: prim_sign,
        363: prim_numbers,
    })

    def c(name, opcode, immediate=False):
        create(name, opcode, immediate=immediate)
        print(name, end=" ")

    print("\nCréation mots avancés (core_system1):", end=" ")
    c("CREATE", OP_CREATE)
    c("DOES>", OP_DOES, immediate=True)
    c("<BUILD>", OP_BUILD, immediate=True)
    c("VOCABULARY", 350)
    c("FORGET", 351)
    c("FIND", 352)
    c("COMPILE", 353)
    c("EXECUTE", 354)
    c("IMMEDIATE", 355, immediate=True)
    c("[", 356, immediate=True)
    c("]", 357)
    c("[COMPILE]", 358, immediate=True)
    c("'", 359, immediate=True)
    c("#", 360)
    c("<#", 361, immediate=True)
    c("#>", 362)
    c("#S", 363)
    print("\ncore_system1.py v1 chargé – vocabulaire complet ajouté")
    __core_sys1_done = True

# fin du "core_system1.py" version "1"