# début du "main" version "75"
version = ('main.py', 75)

import uasyncio as asyncio
import sys

MON_DOSSIER = globals().get('MON_DOSSIER', '')

USE_FORTH_STDLIB = True
DEBUG_CONTROL_FLOW = False  # Désactivé par défaut

def charger(nom):
    chemin = MON_DOSSIER + nom if MON_DOSSIER else nom
    try:
        module_name = chemin.rstrip('.py').replace('/', '.')
        __import__(module_name)
        print(f"  ✓ {nom}")
    except Exception as e:
        print(f"  ✗ {nom}: {e}")
        sys.print_exception(e)
        raise

print("\n" + "="*72)
print(" CHARGEMENT MODULES FORTH (main.py v75)")
print("="*72)

charger('memoire.py')
charger('piles.py')
charger('dictionnaire.py')
charger('core_primitives.py')
charger('core_system.py')
charger('core_system1.py')
charger('core_level2.py')
charger('core_hardware.py')

print("="*72)

from memoire import mem
from piles import piles
from dictionnaire import create_colon_word, align_here, find, see_word, create
from core_primitives import (
    OP_EXIT, OP_LIT, OP_ZBRANCH, OP_BRANCH,
    MARK_THEN, MARK_BEGIN, MARK_DO, MARK_LOOP,
    dispatch
)

compile_stack = []

async def handle_control_flow(opcode, token):
    if DEBUG_CONTROL_FLOW:
        print(f"[CTRL] handle_control_flow(opcode={opcode}, token='{token}') @ here={mem.here:#x}")
        tmp = [f'{a:#x}' for a in compile_stack]
        print(f"[CTRL] compile_stack = {tmp}")
    
    if opcode == MARK_THEN:
        if not compile_stack:
            print("? THEN sans IF")
            mem.state = 0
            return
        addr = compile_stack.pop()
        if DEBUG_CONTROL_FLOW:
            print(f"[CTRL] THEN: patching {addr:#x} → {mem.here:#x}")
        mem.wpoke(addr, mem.here)
        
    elif opcode == MARK_BEGIN:
        if DEBUG_CONTROL_FLOW:
            print(f"[CTRL] BEGIN: push {mem.here:#x}")
        compile_stack.append(mem.here)
        
    elif opcode == MARK_DO:
        if DEBUG_CONTROL_FLOW:
            print(f"[CTRL] DO: compiling OP_DO(90) @ {mem.here:#x}")
        mem.wpoke(mem.here, 90)
        mem.here += 4
        if DEBUG_CONTROL_FLOW:
            print(f"[CTRL] DO: push {mem.here - 4:#x}")
        compile_stack.append(mem.here - 4)
        
    elif opcode == MARK_LOOP:
        if not compile_stack:
            print("? LOOP sans DO")
            mem.state = 0
            return
        do_addr = compile_stack.pop()
        
        if DEBUG_CONTROL_FLOW:
            print(f"[CTRL] {token}: pop do_addr={do_addr:#x}")
        
        if token == "LOOP":
            opcode_loop = 91
        elif token == "+LOOP":
            opcode_loop = 92
        else:
            opcode_loop = 91
        
        if DEBUG_CONTROL_FLOW:
            print(f"[CTRL] {token}: compiling OP({opcode_loop}) @ {mem.here:#x}")
        mem.wpoke(mem.here, opcode_loop)
        mem.here += 4
        
        offset = do_addr - mem.here
        if DEBUG_CONTROL_FLOW:
            print(f"[CTRL] {token}: offset={offset:#x} @ {mem.here:#x}")
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
        if opc == 21:
            val = mem.wpeek(mem.ip)
            mem.ip += 4
            await piles.push(val)
        elif opc < 1000:
            await execute_primitive(opc)
        else:
            await execute_colon(opc)

async def repl():
    print("\n" + "="*72)
    print(" FORTH ESP32-S3 v75 – SYSTÈME COMPLET")
    print("="*72)
    print(" Commandes:")
    print("   WORDS .S SEE <mot>")
    print("   VARIABLE <nom> - Crée variable")
    print("   CONSTANT <nom> - Crée constante")
    print("   LOAD <fichier> - Charge fichier Forth")
    print(" GPIO: <pin> PIN-OUT PIN-HIGH")
    print(" NeoPixel: 48 1 NEO-INIT  48 0 255 0 0 NEO-SET  48 NEO-WRITE")
    print("="*72 + "\n")
    # Dans main.py, après le démarrage du REPL
    if USE_FORTH_STDLIB:
        try:
            with open('stdlib.v', 'r') as f:
                # Parser et exécuter chaque ligne
                pass
        except:
            print("stdlib.v non trouvé")
    while True:
        try:
            prompt = "ok> " if mem.state == 0 else ": "
            line = input(prompt)
            if not line.strip():
                continue

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
                    if DEBUG_CONTROL_FLOW:
                        print(f"[COLON] Début '{name}' @ here={mem.here:#x}")
                    align_here()
                    create_colon_word(name, 0)
                    mem.state = 1
                    i += 2
                    continue

                # SEMI
                if t == ";":
                    if mem.state == 1:
                        if DEBUG_CONTROL_FLOW:
                            print(f"[COLON] EXIT @ {mem.here:#x}")
                        mem.wpoke(mem.here, 0)
                        mem.here += 4
                        mem.state = 0
                    else:
                        print("? ; hors définition")
                    i += 1
                    continue

                # VARIABLE - CORRECTION: parser nom du token suivant
                if t == "VARIABLE":
                    if i + 1 >= len(tokens):
                        print("? VARIABLE : nom manquant")
                        i += 1
                        continue
                    name = tokens[i+1].upper()
                    align_here()
                    create(name, 202)  # OP_VARIABLE
                    mem.wpoke(mem.here, 0)  # Valeur initiale
                    mem.here += 4
                    print(f"VARIABLE {name}")
                    i += 2
                    continue

                # CONSTANT - CORRECTION: parser nom du token suivant
                if t == "CONSTANT":
                    if i + 1 >= len(tokens):
                        print("? CONSTANT : nom manquant")
                        i += 1
                        continue
                    if piles.depth() == 0:
                        print("? CONSTANT : valeur manquante sur pile")
                        i += 2
                        continue
                    value = await piles.pop()
                    name = tokens[i+1].upper()
                    align_here()
                    create(name, 21)  # OP_LIT
                    mem.wpoke(mem.here, value)
                    mem.here += 4
                    print(f"CONSTANT {name} = {value}")
                    i += 2
                    continue

                # SEE
                if t == "SEE":
                    if i + 1 >= len(tokens):
                        print("? SEE : nom manquant")
                    else:
                        await see_word(tokens[i+1].upper())
                    i += 2
                    continue

                # LOAD - Charge fichier Forth
                if t == "LOAD":
                    if i + 1 >= len(tokens):
                        print("? LOAD : nom fichier manquant")
                        i += 1
                        continue
                    filename = tokens[i+1]
                    try:
                        chemin = MON_DOSSIER + filename if MON_DOSSIER else filename
                        with open(chemin, 'r') as f:
                            print(f"Chargement {filename}...")
                            for ligne in f:
                                ligne = ligne.strip()
                                if ligne and not ligne.startswith('\\'):
                                    # Exécuter chaque ligne
                                    # (simplifié - à améliorer)
                                    pass
                            print(f"{filename} chargé")
                    except Exception as e:
                        print(f"? LOAD : {e}")
                    i += 2
                    continue

                # Nombre
                if t.lstrip('-').isdigit():
                    n = int(t)
                    if mem.state == 0:
                        await piles.push(n)
                    else:
                        if DEBUG_CONTROL_FLOW:
                            print(f"[COMPILE] LIT {n} @ {mem.here:#x}")
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
                    if DEBUG_CONTROL_FLOW and t in ("DO", "LOOP", "+LOOP", "IF", "THEN"):
                        print(f"[COMPILE] {t} opcode={opcode} imm={immediate}")
                    
                    if opcode in (MARK_THEN, MARK_BEGIN, MARK_DO, MARK_LOOP):
                        await handle_control_flow(opcode, t)
                    elif immediate:
                        await execute_primitive(opcode)
                    elif opcode in (OP_ZBRANCH, OP_BRANCH):
                        mem.wpoke(mem.here, opcode)
                        mem.here += 4
                        compile_stack.append(mem.here)
                        mem.here += 4
                    else:
                        if DEBUG_CONTROL_FLOW and mem.state == 1:
                            print(f"[COMPILE] {t} opcode={opcode} @ {mem.here:#x}")
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

# fin du "main" version "75"