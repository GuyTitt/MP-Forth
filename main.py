# début du "main" version "81"
version = ('main.py', 81)

import uasyncio as asyncio
import sys

MON_DOSSIER = globals().get('MON_DOSSIER', '')

USE_FORTH_STDLIB = True
DEBUG_LOAD = False  # Désactiver messages DEBUG

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
print(" CHARGEMENT MODULES FORTH (main.py v81)")
print("="*72)

charger('memoire.py')
charger('piles.py')
charger('dictionnaire.py')
charger('core_primitives.py')
charger('core_system.py')

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
    """Gère IF/THEN/BEGIN/DO/LOOP/WHILE/REPEAT"""
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
        compile_stack.append(mem.here - 4)
        
    elif opcode == MARK_LOOP:
        if not compile_stack:
            print("? LOOP sans DO")
            mem.state = 0
            return
        do_addr = compile_stack.pop()
        opcode_loop = 91 if token == "LOOP" else 92
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
        print(f"? Primitive {opcode} inconnue")

async def execute_colon(addr):
    """Exécute mot COLON/VARIABLE/CONSTANT"""
    saved_ip = mem.ip
    mem.ip = addr
    
    opc = mem.wpeek(mem.ip)
    mem.ip += 4
    
    # VARIABLE (202)
    if opc == 202:
        await piles.push(mem.ip)
        mem.ip = saved_ip
        return
    
    # CONSTANT (21)
    if opc == 21:
        val = mem.wpeek(mem.ip)
        mem.ip += 4
        next_opc = mem.wpeek(mem.ip) if mem.ip < len(mem.ram) - 4 else 0
        if next_opc == 0 or mem.ip >= mem.here:
            await piles.push(val)
            mem.ip = saved_ip
            return
        mem.ip -= 8
    
    # Mot COLON
    mem.ip = addr
    
    while True:
        opc = mem.wpeek(mem.ip)
        mem.ip += 4
        
        if opc == 0:
            break
        elif opc == 21:
            val = mem.wpeek(mem.ip)
            mem.ip += 4
            await piles.push(val)
        elif opc < 1000:
            await execute_primitive(opc)
        else:
            await execute_colon(opc)
    
    mem.ip = saved_ip

# ==========================================
# TRAITEMENT LIGNE FORTH
# ==========================================

async def execute_line(line, show_errors=True):
    """Exécute une ligne Forth"""
    # Retirer commentaires () et \
    cleaned = ""
    in_paren = False
    for c in line:
        if c == '\\':  # Commentaire jusqu'à fin de ligne
            break
        if c == '(':
            in_paren = True
        elif c == ')' and in_paren:
            in_paren = False
        elif not in_paren:
            cleaned += c

    tokens = cleaned.split()
    if not tokens:
        return True

    i = 0
    while i < len(tokens):
        t = tokens[i].upper()

        # COLON
        if t == ":":
            if i + 1 >= len(tokens):
                if show_errors:
                    print("? : nom manquant")
                mem.state = 0
                return False
            name = tokens[i+1].upper()
            align_here()
            create_colon_word(name, 0)
            mem.state = 1
            i += 2
            continue

        # SEMI
        if t == ";":
            if mem.state == 1:
                mem.wpoke(mem.here, 0)
                mem.here += 4
                mem.state = 0
            else:
                if show_errors:
                    print("? ; hors définition")
                return False
            i += 1
            continue

        # VARIABLE
        if t == "VARIABLE":
            if i + 1 >= len(tokens):
                if show_errors:
                    print("? VARIABLE : nom manquant")
                i += 1
                continue
            name = tokens[i+1].upper()
            if mem.state == 0:
                align_here()
                create(name, 202)
                mem.wpoke(mem.here, 0)
                mem.here += 4
            i += 2
            continue

        # CONSTANT
        if t == "CONSTANT":
            if i + 1 >= len(tokens):
                if show_errors:
                    print("? CONSTANT : nom manquant")
                i += 1
                continue
            if piles.depth() == 0:
                if show_errors:
                    print("? CONSTANT : valeur manquante")
                i += 2
                continue
            value = await piles.pop()
            name = tokens[i+1].upper()
            if mem.state == 0:
                align_here()
                create(name, 21)
                mem.wpoke(mem.here, value)
                mem.here += 4
            i += 2
            continue

        # ASSIMILE <fichier.v>
        if t == "ASSIMILE":
            if i + 1 >= len(tokens):
                print("? ASSIMILE : fichier manquant")
                i += 1
                continue
            
            fichier = tokens[i+1].strip('<>')
            await load_forth_file(fichier, verbose=True)
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
            if show_errors:
                print(f"? {t}")
            mem.state = 0
            return False

        # Interprétation
        if mem.state == 0:
            if opcode < 1000:
                await execute_primitive(opcode)
            else:
                await execute_colon(opcode)
        # Compilation
        else:
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
                mem.wpoke(mem.here, opcode)
                mem.here += 4
        
        i += 1
    
    return True

# ==========================================
# CHARGEMENT FICHIERS FORTH
# ==========================================

async def load_forth_file(filename, verbose=False):
    """Charge et exécute un fichier .v (vocabulaire Forth)"""
    chemin = MON_DOSSIER + filename if MON_DOSSIER else filename
    
    if verbose:
        print(f"\n[ASSIMILE] Chargement {filename}...")
    
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            definitions = 0
            erreurs = 0
            ligne_num = 0
            
            for ligne in f:
                ligne_num += 1
                ligne = ligne.strip()
                
                # Ignorer commentaires et séparateurs
                if not ligne or ligne.startswith('\\'):
                    continue
                if all(c in '-=│║╔╗╚╝' for c in ligne):
                    continue
                
                try:
                    success = await execute_line(ligne, show_errors=False)
                    
                    if not success:
                        erreurs += 1
                        if DEBUG_LOAD:
                            print(f"  ✗ Ligne {ligne_num}: {ligne[:50]}")
                    else:
                        # Compter définitions
                        if ligne.strip().startswith(':'):
                            parts = ligne.split()
                            if len(parts) > 1:
                                definitions += 1
                                if verbose:
                                    print(f"  ✓ {parts[1]}")
                    
                    mem.state = 0
                    compile_stack.clear()
                    
                except Exception as e:
                    erreurs += 1
                    if DEBUG_LOAD:
                        print(f"  ✗ Ligne {ligne_num}: {e}")
                    mem.state = 0
                    compile_stack.clear()
            
            if verbose:
                print(f"[ASSIMILE] {filename}: {definitions} définitions")
                if erreurs > 0:
                    print(f"[ASSIMILE] {erreurs} erreurs ignorées")
            
            return True
    
    except OSError:
        print(f"✗ Fichier {filename} introuvable")
        return False
    except Exception as e:
        print(f"✗ Erreur {filename}: {e}")
        if DEBUG_LOAD:
            sys.print_exception(e)
        return False

# ==========================================
# CHARGEMENT BIBLIOTHÈQUES AU DÉMARRAGE
# ==========================================

async def load_stdlib():
    """Charge bibliothèques Forth au démarrage"""
    if not USE_FORTH_STDLIB:
        return
    
    print("\n" + "="*72)
    print(" CHARGEMENT BIBLIOTHÈQUES FORTH")
    print("="*72)
    
    # Ordre de chargement important
    bibliotheques = [
        ('stdlib_minimal.v', True),   # Vocabulaire de base
        ('esp32.v', True),             # Matériel ESP32
        ('applicatif.v', False),       # Utilitaires (optionnel)
    ]
    
    for nom, obligatoire in bibliotheques:
        result = await load_forth_file(nom, verbose=True)
        if not result and obligatoire:
            print(f"✗ ERREUR: {nom} est obligatoire!")
            return False
    
    print("="*72 + "\n")
    return True

# ==========================================
# REPL PRINCIPAL
# ==========================================

async def repl():
    print("\n" + "="*72)
    print(" FORTH ESP32-S3 v81 – SYSTÈME MINIMAL")
    print("="*72)
    print(" 21 primitives + bibliothèques Forth = système complet")
    print("="*72 + "\n")
    
    if not await load_stdlib():
        print("✗ Échec chargement bibliothèques")
        return
    
    # Afficher vocabulaire
    print("Vocabulaire chargé:")
    await execute_primitive(204)  # OP_WORDS
    
    print("\nCommandes:")
    print("  WORDS  .S  SEE <mot>  VARIABLES")
    print("  <apps/fichier.v> ASSIMILE  - Charge application")
    print("\nApplications disponibles:")
    print("  <apps/3leds.v> ASSIMILE     - 3 LEDs clignotantes")
    print("  <apps/arcenciel.v> ASSIMILE - Arc-en-ciel NeoPixel")
    print("\nok> ", end='')
    
    while True:
        try:
            line = input()
            if not line.strip():
                continue

            # SEE spécial
            tokens = line.strip().upper().split()
            if len(tokens) == 2 and tokens[0] == "SEE":
                await see_word(tokens[1])
                print("ok> ", end='')
                continue

            # Exécuter ligne
            await execute_line(line)
            
            # Prompt
            if mem.state == 0:
                print("ok> ", end='')
            else:
                print(": ", end='')

        except KeyboardInterrupt:
            print("\n[Ctrl+C]")
            mem.state = 0
            compile_stack.clear()
            print("ok> ", end='')
        except Exception as e:
            print(f"\n✗ {e}")
            # Pas de trace détaillée, juste le message
            mem.state = 0
            compile_stack.clear()
            print("ok> ", end='')

print("Système prêt\n")
asyncio.run(repl())

# fin du "main" version "81"