# début du "words_level1" version "1"
"""
NIVEAU 1 : Mots Forth créés à partir des primitives NIVEAU 0.
Ces mots seront compilés automatiquement au démarrage.
"""

import uasyncio as asyncio
from memoire import mem
from piles import piles

# Liste des définitions Forth à compiler au démarrage
FORTH_WORDS_L1 = [
    # Stack manipulation (2 items)
    ": 2DUP OVER OVER ;",
    ": 2DROP DROP DROP ;",
    ": NIP SWAP DROP ;",
    ": TUCK DUP ROT ROT ;",
    
    # Comparison
    ": = - 0= ;",
    ": 0= DUP 0 - NEGATE 1 + ;",
    ": <> 0= NEGATE ;",
    ": < 2DUP - 0< ;",
    ": > SWAP < ;",
    ": <= 2DUP > 0= ;",
    ": >= SWAP <= ;",
    
    # Logic
    ": NOT 0= ;",
    ": AND * 0<> ;",
    ": OR + 0<> ;",
    
    # Arithmetic
    ": MIN 2DUP > IF DROP ELSE NIP THEN ;",
    ": MAX 2DUP < IF DROP ELSE NIP THEN ;",
    ": SQUARE DUP * ;",
    ": CUBE DUP DUP * * ;",
    
    # Memory helpers
    ": +! DUP @ ROT + SWAP ! ;",
    
    # Control flow (IF THEN ELSE)
    # Note: IF/THEN/ELSE seront implémentées spécialement
]

async def compile_forth_word(word_def):
    """Compiler une définition Forth simple"""
    tokens = word_def.split()
    # Ignoré pour l'instant - sera géré par main.py
    pass

async def init_level1():
    """Initialiser les mots de niveau 1"""
    print("\n--- Chargement des mots NIVEAU 1 ---")
    # Pour l'instant, l'initialisation se fait via le REPL
    # Les utilisateurs tapent les définitions
    print("Mots NIVEAU 1 disponibles dans le REPL")

version = ('words_level1.py', 1)
print(f"words_level1.py v{version[1]} – définitions NIVEAU 1 (Forth pur)")
# fin du "words_level1" version "1"