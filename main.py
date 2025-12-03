# début du "main" version "78"
version = ('main.py', 78)

import uasyncio as asyncio
import sys

MON_DOSSIER = globals().get('MON_DOSSIER', '')

USE_FORTH_STDLIB = True
DEBUG_CONTROL_FLOW = False
DEBUG_VARIABLE = False  # Debug VARIABLE/CONSTANT

# ==========================================
# CHARGEMENT MODULES
# ==========================================

def charger(nom):
    """Charge un module Python"""
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
print(" CHARGEMENT MODULES FORTH (main.py v78)")
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

# ==========================================
# GESTION STRUCTURES DE CONTRÔLE
# ==========================================

async def handle_control_flow(opcode, token):
    """Gère IF/THEN/BEGIN/DO/LOOP pendant la compilation"""
    if DEBUG_CONTROL_FLOW:
        print(f"[CTRL] {token} opcode={opcode} @ here={mem.here:#x}")
        print(f"[CTRL] compile_stack = {[f'{a:#x}' for a in compile_stack]}")
    
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
        mem.wpoke(mem.here, 90)  # OP_DO
        mem.here += 4
        compile_stack.append(mem.here - 4)
        
    elif opcode == MARK_LOOP:
        if not compile_stack:
            print("? LOOP sans DO")
            mem.state = 0
            return
        do_addr = compile_stack.pop()
        
        opcode_loop = 91 if token == "LOOP" else 92  # LOOP ou +LOOP
        mem.wpoke(mem.here, opcode_loop)
        mem.here += 4
        
        offset = do_addr - mem.here
        mem.wpoke(mem.here, offset & 0xFFFFFFFF)
        mem.here += 4

# ==========================================
# EXÉCUTION
# ==========================================

async def execute_primitive(opcode):
    """Exécute une primitive"""
    func = dispatch.get(opcode)
    if func:
        await func()
    else:
        print(f"? primitive {opcode} inconnue")

async def execute_colon(addr):
    """Exécute un mot COLON ou VARIABLE/CONSTANT
    
    3 cas possibles:
    1. VARIABLE (opcode 202 = OP_DOVAR) : empile adresse puis EXIT
    2. CONSTANT (opcode 21 = OP_LIT) : empile valeur puis EXIT  
    3. Mot COLON : séquence opcodes terminée par EXIT
    """
    saved_ip = mem.ip  # Sauvegarder IP appelant
    mem.ip = addr
    
    # Lire premier opcode
    opc = mem.wpeek(mem.ip)
    mem.ip += 4
    
    if DEBUG_VARIABLE:
        print(f"[EXEC] execute_colon(0x{addr:x}) opc={opc}")
    
    # Cas VARIABLE (OP_DOVAR)
    if opc == 202:
        addr_data = mem.ip  # Adresse de la valeur
        await piles.push(addr_data)
        if DEBUG_VARIABLE:
            val = mem.wpeek(addr_data)
            print(f"[VAR] Push addr=0x{addr_data:x} (val={val})")
        mem.ip = saved_ip  # Restaurer IP
        return
    
    # Cas CONSTANT (OP_LIT sans boucle)
    if opc == 21:
        val = mem.wpeek(mem.ip)
        mem.ip += 4
        # Vérifier si c'est bien une CONSTANT (pas de code après)
        next_opc = mem.wpeek(mem.ip) if mem.ip < len(mem.ram) - 4 else 0
        if next_opc == 0 or mem.ip >= mem.here:  # EXIT ou fin dictionnaire
            await piles.push(val)
            if DEBUG_VARIABLE:
                print(f"[CONST] Push val={val}")
            mem.ip = saved_ip
            return
        # Sinon c'est un LIT dans un mot COLON, reculer IP
        mem.ip -= 8
    
    # Cas COLON : reculer IP et exécuter séquence
    mem.ip = addr
    
    while True:
        opc = mem.wpeek(mem.ip)
        mem.ip += 4
        
        if opc == 0:  # EXIT
            break
        elif opc == 21:  # LIT
            val = mem.wpeek(mem.ip)
            mem.ip += 4
            await piles.push(val)
        elif opc < 1000:  # Primitive
            await execute_primitive(opc)
        else:  # Autre mot COLON
            await execute_colon(opc)
    
    mem.ip = saved_ip  # Restaurer IP

# ==========================================
# GESTION STDLIB.V
# ==========================================

async def load_stdlib():
    """Charge stdlib.v au démarrage"""
    if not USE_FORTH_STDLIB:
        return
    
    try:
        chemin = MON_DOSSIER + 'stdlib.v' if MON_DOSSIER else 'stdlib.v'
        with open(chemin, 'r', encoding='utf-8') as f:
            print("Chargement stdlib.v...")
            definitions = 0
            
            for num_ligne, ligne in enumerate(f, 1):
                ligne = ligne.strip()
                if not ligne or ligne.startswith('\\') or ligne.startswith('( '):
                    continue
                
                tokens = ligne.split()
                if tokens and tokens[0] == ':' and len(tokens) > 1:
                    print(f"  Définition: {tokens[1]}")
                    definitions += 1
            
            print(f"stdlib.v scanné ({definitions} définitions détectées)")
            print("Note: Exécution complète stdlib.v à implémenter\n")
    except OSError:
        print("stdlib.v non trouvé - primitives uniquement\n")
    except Exception as e:
        print(f"Erreur stdlib.v: {e}\n")

# ==========================================
# REPL - INTERPRÉTATION
# ==========================================

async def process_token_interpret(t):
    """Traite un token en mode interprétation"""
    # Nombre ?
    if t.lstrip('-').isdigit():
        await piles.push(int(t))
        return True
    
    # Mot du dictionnaire ?
    opcode, immediate = find(t)
    if opcode is None:
        print(f"? {t}")
        return False
    
    # Exécuter
    if opcode < 1000:
        await execute_primitive(opcode)
    else:
        await execute_colon(opcode)
    
    return True

# ==========================================
# REPL - COMPILATION
# ==========================================

async def process_token_compile(t):
    """Traite un token en mode compilation"""
    # Nombre ?
    if t.lstrip('-').isdigit():
        n = int(t)
        mem.wpoke(mem.here, OP_LIT)
        mem.here += 4
        mem.wpoke(mem.here, n)
        mem.here += 4
        return True
    
    # Mot du dictionnaire ?
    opcode, immediate = find(t)
    if opcode is None:
        print(f"? {t}")
        mem.state = 0
        return False
    
    # Structures de contrôle ?
    if opcode in (MARK_THEN, MARK_BEGIN, MARK_DO, MARK_LOOP):
        await handle_control_flow(opcode, t)
    # Mot immédiat ?
    elif immediate:
        await execute_primitive(opcode)
    # IF/ELSE (branchements) ?
    elif opcode in (OP_ZBRANCH, OP_BRANCH):
        mem.wpoke(mem.here, opcode)
        mem.here += 4
        compile_stack.append(mem.here)
        mem.here += 4
    # Mot normal : compiler opcode
    else:
        mem.wpoke(mem.here, opcode)
        mem.here += 4
    
    return True

# ==========================================
# REPL PRINCIPAL
# ==========================================

async def repl():
    print("\n" + "="*72)
    print(" FORTH ESP32-S3 v78 – SYSTÈME COMPLET")
    print("="*72)
    print(" Commandes:")
    print("   WORDS .S SEE <mot> VARIABLES")
    print("   VARIABLE <nom> - Crée variable")
    print("   CONSTANT <nom> - Crée constante")
    print(" GPIO: <pin> PIN-OUT PIN-HIGH")
    print(" NeoPixel: 48 1 NEO-INIT  48 0 255 0 0 NEO-SET  48 NEO-WRITE")
    print("="*72 + "\n")
    
    await load_stdlib()
    
    while True:
        try:
            prompt = "ok> " if mem.state == 0 else ": "
            line = input(prompt)
            if not line.strip():
                continue

            # Retirer commentaires ()
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

                # ===== COLON =====
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

                # ===== SEMI =====
                if t == ";":
                    if mem.state == 1:
                        mem.wpoke(mem.here, 0)  # EXIT
                        mem.here += 4
                        mem.state = 0
                    else:
                        print("? ; hors définition")
                    i += 1
                    continue

                # ===== VARIABLE =====
                if t == "VARIABLE":
                    if i + 1 >= len(tokens):
                        print("? VARIABLE : nom manquant")
                        i += 1
                        continue
                    
                    name = tokens[i+1].upper()
                    
                    if mem.state == 0:
                        align_here()
                        create(name, 202)  # OP_DOVAR
                        mem.wpoke(mem.here, 0)  # Valeur initiale
                        mem.here += 4
                        if DEBUG_VARIABLE:
                            print(f"VARIABLE {name} @ 0x{mem.here-4:x}")
                        else:
                            print(f"VARIABLE {name}")
                    else:
                        print("? VARIABLE en mode compilation non supporté")
                    
                    i += 2
                    continue

                # ===== CONSTANT =====
                if t == "CONSTANT":
                    if i + 1 >= len(tokens):
                        print("? CONSTANT : nom manquant")
                        i += 1
                        continue
                    if piles.depth() == 0:
                        print("? CONSTANT : valeur manquante")
                        i += 2
                        continue
                    
                    value = await piles.pop()
                    name = tokens[i+1].upper()
                    
                    if mem.state == 0:
                        align_here()
                        create(name, 21)  # OP_LIT
                        mem.wpoke(mem.here, value)
                        mem.here += 4
                        if DEBUG_VARIABLE:
                            print(f"CONSTANT {name} = {value} @ 0x{mem.here-4:x}")
                        else:
                            print(f"CONSTANT {name} = {value}")
                    else:
                        print("? CONSTANT en mode compilation non supporté")
                    
                    i += 2
                    continue

                # ===== SEE =====
                if t == "SEE":
                    if i + 1 < len(tokens):
                        await see_word(tokens[i+1].upper())
                    else:
                        print("? SEE : nom manquant")
                    i += 2
                    continue

                # ===== LOAD =====
                if t == "LOAD":
                    if i + 1 >= len(tokens):
                        print("? LOAD : nom fichier manquant")
                        i += 1
                        continue
                    # TODO: implémenter LOAD complet
                    print(f"LOAD {tokens[i+1]} - à implémenter")
                    i += 2
                    continue

                # ===== TRAITEMENT GÉNÉRAL =====
                if mem.state == 0:
                    if not await process_token_interpret(t):
                        break
                else:
                    if not await process_token_compile(t):
                        break
                
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

# fin du "main" version "78"