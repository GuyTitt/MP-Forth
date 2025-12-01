# début du "main" version "66"
version = ('main.py', 66)

import uasyncio as asyncio
import sys

# MON_DOSSIER est défini par boot.py et dans globals()
MON_DOSSIER = globals().get('MON_DOSSIER', '')

def charger(nom):
    """Charger un module Python"""
    chemin = MON_DOSSIER + nom if MON_DOSSIER else nom
    try:
        module_name = chemin.rstrip('.py').replace('/', '.')
        __import__(module_name)
        src = "lib1" if MON_DOSSIER else "racine"
        print(f"  {nom:20} → chargé [{src}]")
    except Exception as e:
        print(f"ERREUR chargement {nom} : {e}")

print("\n" + "="*72)
print(" CHARGEMENT DES MODULES FORTH (main.py v66)")
print("="*72)

# Chargement des modules
for module in [
    'memoire.py', 'piles.py', 'dictionnaire.py', 
    'core_primitives.py', 'core_system.py', 'core_system1.py']:
    charger(module)

print("="*72)

# Imports après chargement
from memoire import mem
from piles import piles
from dictionnaire import create_colon_word, align_here, find
from core_primitives import (
    OP_EXIT, OP_LIT, OP_ZBRANCH, OP_BRANCH,
    MARK_THEN, MARK_BEGIN, MARK_DO, MARK_LOOP,
    dispatch
)

compile_stack = []

# ================================================
# Gestion des structures de contrôle
# ================================================
async def handle_control_flow(opcode, token):
    if opcode == MARK_THEN:
        if not compile_stack:
            print("? THEN sans IF")
            mem.state = 0
            return
        addr = compile_stack.pop()
        mem.wpoke(addr, mem.here)
    elif opcode == MARK_BEGIN:
        compile_stack.append(mem.here)
    elif opcode == MARK_DO:
        mem.wpoke(mem.here, 90)
        mem.here += 4
        compile_stack.append(mem.here)
        mem.here += 8
    elif opcode == MARK_LOOP:
        if not compile_stack:
            print("? LOOP sans DO")
            mem.state = 0
            return
        start = compile_stack.pop()
        op = 91 if token == "LOOP" else 92
        mem.wpoke(mem.here, op)
        mem.here += 4
        mem.wpoke(mem.here, start - mem.here - 4)
        mem.here += 4
        mem.wpoke(start, mem.here)

# ================================================
# Exécution
# ================================================
async def execute_primitive(opcode):
    func = dispatch.get(opcode)
    if func:
        await func()

async def execute_colon(addr):
    mem.ip = addr
    while True:
        opc = mem.wpeek(mem.ip)
        mem.ip += 4
        if opc == 0:
            break
        if opc == 21:  # OP_LIT
            val = mem.wpeek(mem.ip)
            mem.ip += 4
            await piles.push(val)
        elif opc < 1000:
            await execute_primitive(opc)
        else:
            await execute_colon(opc)

# ================================================
# REPL
# ================================================
async def repl():
    print("\n" + "="*72)
    print(" FORTH ESP32-S3 v66 – SYSTÈME FONCTIONNEL")
    print(" Tape : WORDS  ou  5 DUP * .")
    print("="*72 + "\n")

    while True:
        try:
            prompt = "ok> " if mem.state == 0 else ": "
            line = input(prompt).strip()
            if not line:
                continue

            # Supprimer commentaires ( ... )
            cleaned = ""
            in_paren = False
            for c in line:
                if c == '(':
                    in_paren = True
                elif c == ')' and in_paren:
                    in_paren = False
                elif not in_paren:
                    cleaned += c

            tokens = cleaned.split()
            if not tokens:
                continue

            i = 0
            while i < len(tokens):
                t = tokens[i].upper()

                # Cas 1 : COLON
                if t == ":":
                    if i + 1 >= len(tokens):
                        print("? nom manquant après :")
                        mem.state = 0
                        break
                    name = tokens[i+1]
                    align_here()
                    create_colon_word(name, mem.here)
                    mem.state = 1
                    i += 2
                    continue

                # Cas 2 : SEMI
                if t == ";":
                    if mem.state == 1:
                        mem.wpoke(mem.here, 0)  # OP_EXIT
                        mem.here += 4
                        mem.state = 0
                    else:
                        print("? ; hors définition")
                    i += 1
                    continue

                # Cas 3 : Nombre
                if t.lstrip('-').isdigit():
                    n = int(t)
                    if mem.state == 0:
                        await piles.push(n)
                    else:
                        mem.wpoke(mem.here, OP_LIT)
                        mem.here += 4
                        mem.wpoke(mem.here, n)
                        mem.here += 4
                    i += 1
                    continue

                # Cas 4 : Mot du dictionnaire
                opcode, immediate = find(t)
                if opcode is None:
                    print(f"? {t}")
                    mem.state = 0
                    i += 1
                    continue

                # Interprétation
                if mem.state == 0:
                    if opcode < 1000:
                        await execute_primitive(opcode)
                    else:
                        await execute_colon(opcode)
                else:
                    if immediate:
                        await execute_primitive(opcode)
                    elif opcode in (OP_ZBRANCH, OP_BRANCH):
                        mem.wpoke(mem.here, opcode)
                        mem.here += 4
                        compile_stack.append(mem.here)
                        mem.here += 4
                    elif opcode in (MARK_THEN, MARK_BEGIN, MARK_DO, MARK_LOOP):
                        await handle_control_flow(opcode, t)
                    else:
                        mem.wpoke(mem.here, opcode)
                        mem.here += 4
                i += 1

        except Exception as e:
            print(f"\n[ERREUR] {e}")
            mem.state = 0
            compile_stack.clear()

print("main.py v66 chargé – démarrage REPL\n")
asyncio.run(repl())

# fin du "main" version "66"