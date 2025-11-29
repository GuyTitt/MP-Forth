# début du "core_primitives" version "33"
version = ('core_primitives.py', 33)

try:
    __core_prim_done
except NameError:
    __core_prim_done = False

if not __core_prim_done:
    from memoire import mem
    from dictionnaire import create
    from piles import piles
    import uasyncio as asyncio

    # === OPCODES – TOUS définis ici (exportés pour core_system) ===
    OP_EXIT     = 0
    OP_DUP      = 1
    OP_DROP     = 2
    OP_SWAP     = 3
    OP_OVER     = 4
    OP_ROT      = 5
    OP_2DUP_P   = 34
    OP_2DROP_P  = 35
    OP_NIP      = 36
    OP_TUCK     = 37

    OP_ADD      = 6
    OP_SUB      = 7
    OP_MUL      = 8
    OP_DIV      = 9
    OP_MOD      = 10
    OP_NEGATE   = 11
    OP_ABS      = 12

    OP_LT       = 111
    OP_GT       = 112
    OP_EQ       = 113
    OP_ZLESS    = 114
    OP_ZEQUAL   = 115
    OP_U_LESS   = 119

    OP_FETCH    = 13
    OP_STORE    = 14
    OP_CFETCH   = 15
    OP_CSTORE   = 16
    OP_FETCHP   = 38
    OP_STOREP   = 39

    OP_DOT      = 17
    OP_CR       = 18
    OP_EMIT     = 19
    OP_KEY      = 20
    OP_SPACE    = 40
    OP_SPACES   = 41

    OP_LIT      = 21
    OP_BRANCH   = 22
    OP_ZBRANCH  = 23

    OP_AND      = 42
    OP_OR       = 43
    OP_XOR      = 44
    OP_NOT      = 45

    OP_DO       = 90
    OP_LOOP     = 91
    OP_PLOOP    = 92
    OP_I        = 109
    OP_J        = 110

    # === MARQUEURS DE CONTRÔLE (utilisés par main.py) ===
    MARK_THEN   = 999
    MARK_BEGIN  = 998
    MARK_DO     = 997
    MARK_LOOP   = 996

    # === OPCODES SYSTÈME (définis ici pour export) ===
    OP_WORDS    = 29
    OP_DOTSS    = 30
    OP_DEPTH    = 116
    OP_TESTS    = 31
    OP_FORGET   = 46
    OP_SEE      = 47
    OP_DEBUG    = 101
    OP_HEX      = 106
    OP_DECIMAL  = 107
    OP_MIN      = 117
    OP_MAX      = 118

    # === PRIMITIVES ===
    async def prim_exit(): pass
    async def prim_dup():
        x = await piles.pop()
        await piles.push(x)
        await piles.push(x)
    async def prim_drop(): await piles.pop()
    async def prim_swap():
        a = await piles.pop(); b = await piles.pop()
        await piles.push(a); await piles.push(b)
    async def prim_over():
        a = await piles.pop(); b = await piles.pop()
        await piles.push(b); await piles.push(a); await piles.push(b)
    async def prim_rot():
        a = await piles.pop(); b = await piles.pop(); c = await piles.pop()
        await piles.push(a); await piles.push(c); await piles.push(b)
    async def prim_2dup():
        a = await piles.pop(); b = await piles.pop()
        await piles.push(b); await piles.push(a); await piles.push(b); await piles.push(a)
    async def prim_2drop(): await piles.pop(); await piles.pop()
    async def prim_nip():
        a = await piles.pop(); await piles.pop()
        await piles.push(a)
    async def prim_tuck():
        a = await piles.pop(); b = await piles.pop()
        await piles.push(a); await piles.push(b); await piles.push(a)

    async def prim_add(): await piles.push(await piles.pop() + await piles.pop())
    async def prim_sub():
        b = await piles.pop(); a = await piles.pop()
        await piles.push(a - b)
    async def prim_mul(): await piles.push(await piles.pop() * await piles.pop())
    async def prim_div():
        b = await piles.pop(); a = await piles.pop()
        if b == 0: raise ValueError("div/0")
        await piles.push(a // b)
    async def prim_mod():
        b = await piles.pop(); a = await piles.pop()
        if b == 0: raise ValueError("mod/0")
        await piles.push(a % b)
    async def prim_negate(): await piles.push(-await piles.pop())
    async def prim_abs(): await piles.push(abs(await piles.pop()))

    async def prim_lt():
        b = await piles.pop(); a = await piles.pop()
        await piles.push(1 if a < b else 0)
    async def prim_gt():
        b = await piles.pop(); a = await piles.pop()
        await piles.push(1 if a > b else 0)
    async def prim_eq():
        b = await piles.pop(); a = await piles.pop()
        await piles.push(1 if a == b else 0)
    async def prim_zless():
        a = await piles.pop()
        await piles.push(1 if a < 0 else 0)
    async def prim_zequal():
        a = await piles.pop()
        await piles.push(1 if a == 0 else 0)
    async def prim_u_less():
        b = await piles.pop(); a = await piles.pop()
        await piles.push(1 if (a & 0xFFFFFFFF) < (b & 0xFFFFFFFF) else 0)

    async def prim_fetch(): await piles.push(mem.wpeek(await piles.pop()))
    async def prim_store():
        addr = await piles.pop(); val = await piles.pop()
        mem.wpoke(addr, val)
    async def prim_cfetch(): await piles.push(mem.cpeek(await piles.pop()))
    async def prim_cstore():
        addr = await piles.pop(); val = await piles.pop()
        mem.cpoke(addr, val & 0xFF)
    async def prim_fetchp():
        addr = await piles.pop()
        await piles.push(mem.wpeek(addr) + await piles.pop())
    async def prim_storep():
        addr = await piles.pop(); val = await piles.pop()
        mem.wpoke(addr, mem.wpeek(addr) + val)

    async def prim_dot(): print(await piles.pop(), end=' ')
    async def prim_cr(): print()
    async def prim_emit():
        code = await piles.pop()
        print(chr(code & 0xFF), end='')
    async def prim_key():
        try:
            ch = input()
            await piles.push(ord(ch[0]) if ch else 0)
        except:
            await piles.push(0)
    async def prim_space(): print(" ", end='')
    async def prim_spaces():
        n = await piles.pop()
        for _ in range(n): print(" ", end='')

    async def prim_lit():
        val = mem.wpeek(mem.ip)
        mem.ip += 4
        await piles.push(val)
    async def prim_branch(): mem.ip = mem.wpeek(mem.ip)
    async def prim_zbranch():
        target = mem.wpeek(mem.ip)
        mem.ip += 4
        if await piles.pop() == 0:
            mem.ip = target

    async def prim_and():
        b = await piles.pop(); a = await piles.pop()
        await piles.push(a & b)
    async def prim_or():
        b = await piles.pop(); a = await piles.pop()
        await piles.push(a | b)
    async def prim_xor():
        b = await piles.pop(); a = await piles.pop()
        await piles.push(a ^ b)
    async def prim_not():
        a = await piles.pop()
        await piles.push(~a & 0xFFFFFFFF)

    async def prim_do():
        limit = await piles.pop(); index = await piles.pop()
        mem.rp -= 8
        mem.wpoke(mem.rp, index)
        mem.wpoke(mem.rp + 4, limit)
    async def prim_loop():
        mem.wpoke(mem.rp, mem.wpeek(mem.rp) + 1)
        if mem.wpeek(mem.rp) < mem.wpeek(mem.rp + 4):
            mem.ip += mem.wpeek(mem.ip - 4)
        else:
            mem.ip += 4; mem.rp += 8
    async def prim_ploop():
        incr = await piles.pop()
        mem.wpoke(mem.rp, mem.wpeek(mem.rp) + incr)
        if mem.wpeek(mem.rp) < mem.wpeek(mem.rp + 4):
            mem.ip += mem.wpeek(mem.ip - 4)
        else:
            mem.ip += 4; mem.rp += 8
    async def prim_i(): await piles.push(mem.wpeek(mem.rp))
    async def prim_j(): await piles.push(mem.wpeek(mem.rp + 16))

    # Dispatch global
    dispatch = {
        OP_EXIT: prim_exit, OP_DUP: prim_dup, OP_DROP: prim_drop,
        OP_SWAP: prim_swap, OP_OVER: prim_over, OP_ROT: prim_rot,
        OP_2DUP_P: prim_2dup, OP_2DROP_P: prim_2drop, OP_NIP: prim_nip, OP_TUCK: prim_tuck,
        OP_ADD: prim_add, OP_SUB: prim_sub, OP_MUL: prim_mul,
        OP_DIV: prim_div, OP_MOD: prim_mod, OP_NEGATE: prim_negate, OP_ABS: prim_abs,
        OP_LT: prim_lt, OP_GT: prim_gt, OP_EQ: prim_eq,
        OP_ZLESS: prim_zless, OP_ZEQUAL: prim_zequal, OP_U_LESS: prim_u_less,
        OP_FETCH: prim_fetch, OP_STORE: prim_store,
        OP_CFETCH: prim_cfetch, OP_CSTORE: prim_cstore,
        OP_FETCHP: prim_fetchp, OP_STOREP: prim_storep,
        OP_DOT: prim_dot, OP_CR: prim_cr, OP_EMIT: prim_emit, OP_KEY: prim_key,
        OP_SPACE: prim_space, OP_SPACES: prim_spaces,
        OP_LIT: prim_lit, OP_BRANCH: prim_branch, OP_ZBRANCH: prim_zbranch,
        OP_AND: prim_and, OP_OR: prim_or, OP_XOR: prim_xor, OP_NOT: prim_not,
        OP_DO: prim_do, OP_LOOP: prim_loop, OP_PLOOP: prim_ploop,
        OP_I: prim_i, OP_J: prim_j,
    }

    print("core_primitives.py v33 chargé – tous les opcodes exportés")
    __core_prim_done = True

# Export explicite pour core_system.py
__all__ = [
    "dispatch", "OP_EXIT", "OP_LIT", "OP_ZBRANCH", "OP_BRANCH",
    "MARK_THEN", "MARK_BEGIN", "MARK_DO", "MARK_LOOP",
    "OP_WORDS", "OP_DOTSS", "OP_DEPTH", "OP_TESTS", "OP_FORGET", "OP_SEE",
    "OP_DEBUG", "OP_HEX", "OP_DECIMAL", "OP_MIN", "OP_MAX"
]

# fin du "core_primitives" version "33"