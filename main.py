# début du "main" version "72"
version = ('main.py', 72)

import uasyncio as asyncio
import sys

MON_DOSSIER = globals().get('MON_DOSSIER', '')

def charger(nom):
    chemin = MON_DOSSIER + nom if MON_DOSSIER else nom
    try:
        module_name = chemin.rstrip('.py').replace('/', '.')
        __import__(module_name)
    except Exception as e:
        print(f"ERREUR chargement {nom} : {e}")
        sys.print_exception(e)
        raise

print("\n" + "="*72)
print(" CHARGEMENT MODULES FORTH (main.py v72)")
print("="*72)

charger('memoire.py')
charger('piles.py')
charger('dictionnaire.py')
charger('core_primitives.py')
charger('core_system.py')
charger('core_system1.py')
charger('core_level2.py')      # AJOUTÉ
charger('core_hardware.py')    # AJOUTÉ

print("="*72)

from memoire import mem
from piles import piles
from dictionnaire import create_colon_word, align_here, find, see_word
from core_primitives import (
    OP_EXIT, OP_LIT, OP_ZBRANCH, OP_BRANCH,
    MARK_THEN, MARK_BEGIN, MARK_DO, MARK_LOOP,
    dispatch
)

compile_stack = []

async def handle_control_flow(opcode, token):
    """Gestion des structures de contrôle IF/THEN/DO/LOOP/BEGIN"""
    
    if opcode == MARK_THEN:  # 999
        if not compile_stack:
            print("? THEN sans IF")
            mem.state = 0
            return
        addr = compile_stack.pop()
        mem.wpoke(addr, mem.here)
        
    elif opcode == MARK_BEGIN:  # 998
        compile_stack.append(mem.here)
        
    elif opcode == MARK_DO:  # 997
        # Sauvegarder position actuelle pour LOOP
        compile_stack.append(mem.here)
        # Compiler OP_DO
        mem.wpoke(mem.here, 90)
        mem.here += 4
        
    elif opcode == MARK_LOOP:  # 996
        if not compile_stack:
            print("? LOOP sans DO")
            mem.state = 0
            return
        do_addr = compile_stack.pop()
        
        # Compiler OP_LOOP ou OP_PLOOP
        if token == "LOOP":
            mem.wpoke(mem.here, 91)
        elif token == "+LOOP":
            mem.wpoke(mem.here, 92)
        else:
            mem.wpoke(mem.here, 91)
        mem.here += 4
        
        # Compiler offset de saut vers DO (saut arrière)
        offset = do_addr - mem.here
        mem.wpoke(mem.here, offset & 0xFFFFFFFF)
        mem.here += 4

async def execute_primitive(opcode):
    func = dispatch.get(opcode)
    if func:
        await func()
    else:
        print(f"? primitive {opcode} inconnue")

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

async def repl():
    print("\n" + "="*72)
    print(" FORTH ESP32-S3 v72 – SYSTÈME COMPLET")
    print("="*72)
    print(" Commandes:")
    print("   WORDS       - Liste tous les mots")
    print("   .S          - Affiche la pile")
    print("   SEE <mot>   - Décompile un mot")
    print(" GPIO:")
    print("   <pin> PIN-OUT PIN-HIGH - Configure et active")
    print("   <pin> PIN-IN PIN-READ  - Configure et lit")
    print(" Time:")
    print("   <ms> MS     - Pause en millisecondes")
    print("   TICKS-MS    - Timestamp actuel")
    print("="*72 + "\n")

    while True:
        try:
            prompt = "ok> " if mem.state == 0 else ": "
            line = input(prompt)
            if not line.strip():
                continue

            # Supprimer commentaires
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

                # COLON
                if t == ":":
                    if i + 1 >= len(tokens):
                        print("? nom manquant après :")
                        mem.state = 0
                        break
                    name = tokens[i+1].upper()
                    align_here()
                    create_colon_word(name, 0)
                    mem.state = 1
                    i += 2
                    continue

                # SEMI
                if t == ";":
                    if mem.state == 1:
                        mem.wpoke(mem.here, 0)  # EXIT
                        mem.here += 4
                        mem.state = 0
                    else:
                        print("? ; hors définition")
                    i += 1
                    continue

                # SEE
                if t == "SEE":
                    if i + 1 >= len(tokens):
                        print("? SEE : nom manquant")
                    else:
                        await see_word(tokens[i+1].upper())
                    i += 2
                    continue

                # Nombre
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

                # Mot du dictionnaire
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
                    # Compilation
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

        except KeyboardInterrupt:
            print("\n[Ctrl+C] Interruption")
            mem.state = 0
            compile_stack.clear()
        except Exception as e:
            print(f"\n[ERREUR] {e}")
            sys.print_exception(e)
            mem.state = 0
            compile_stack.clear()

print("Système prêt\n")
asyncio.run(repl())

# fin du "main" version "72"