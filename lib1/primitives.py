# début du "primitives" version "3"
from memoire import mem
from dictionnaire import create
import uasyncio as asyncio

async def _dup():
    x = await piles.pop()
    await piles.push(x)
    await piles.push(x)
_dup.immediate = False

async def _dot():
    print(await piles.pop(), end=' ')
_dot.immediate = False

async def _cr(): print()
_cr.immediate = False

async def _words():
    addr = mem.latest
    while addr:
        link = mem.wpeek(addr)
        addr += 4
        flags = mem.ram[addr]; length = flags & 0x7F
        addr += 1
        name = ''.join(chr(mem.ram[addr+i]) for i in range(length))
        print(name, end='  ')
        addr = link
    print()
_words.immediate = False

# Création des premiers mots
create("DUP", _dup)
create(".", _dot)
create("CR", _cr)
create("WORDS", _words)

version = ('primitives.py', 3)
print(f"Chargement module: {version} – mots créés")
# --- TESTS (uniquement en phase développement) ---
async def _tests():
    from tests import run_all_tests
    await run_all_tests()

_tests.immediate = False
create("TESTS", _tests)
# --- TESTS (uniquement en phase développement) ---
# fin du "primitives" version "3"