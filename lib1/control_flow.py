# début du "control_flow" version "1"
"""
Gestion du contrôle de flux Forth :
- IF THEN ELSE
- BEGIN UNTIL WHILE REPEAT
- DO LOOP +LOOP
Ces structures seront traduites en bytecode lors de la compilation.
"""

from memoire import mem
from dictionnaire import create, create_colon_word
import uasyncio as asyncio

# Opcodes pour le contrôle de flux
OP_IF       = 50
OP_THEN     = 51
OP_ELSE     = 52
OP_BEGIN    = 53
OP_UNTIL    = 54
OP_WHILE    = 55
OP_REPEAT   = 56
OP_DO       = 57
OP_LOOP     = 58
OP_PLOOP    = 59

class ControlFlowCompiler:
    """Gère la compilation des structures de contrôle"""
    
    def __init__(self):
        self.if_stack = []      # Stack pour les IF imbriqués
        self.loop_stack = []    # Stack pour les boucles imbriquées
    
    def compile_if(self):
        """Compiler IF : émettre 0BRANCH avec placeholder"""
        # OP_ZBRANCH sera utilisé, mais l'adresse cible sera remplie plus tard
        mem.wpoke(mem.here, 50)  # OP_IF placeholder
        mem.here += 4
        # Sauvegarder l'adresse où l'offset sera écrit
        self.if_stack.append(mem.here - 4)
    
    def compile_else(self):
        """Compiler ELSE"""
        if not self.if_stack:
            raise Exception("ELSE sans IF")
        # Émettre BRANCH vers THEN
        mem.wpoke(mem.here, 22)  # OP_BRANCH
        mem.here += 4
        # Remplir le 0BRANCH du IF
        if_addr = self.if_stack.pop()
        mem.wpoke(if_addr, mem.here)  # Adresse après ELSE
        self.if_stack.append(mem.here - 4)
    
    def compile_then(self):
        """Compiler THEN"""
        if not self.if_stack:
            raise Exception("THEN sans IF")
        then_addr = self.if_stack.pop()
        mem.wpoke(then_addr, mem.here)

# Instance globale
cf_compiler = ControlFlowCompiler()

# Primitives pour IF/THEN/ELSE
async def prim_if():
    """Marqueur IF en mode compilation"""
    cf_compiler.compile_if()

async def prim_then():
    """Marqueur THEN en mode compilation"""
    cf_compiler.compile_then()

async def prim_else():
    """Marqueur ELSE en mode compilation"""
    cf_compiler.compile_else()

# Ces fonctions seront appelées avec immediate=True
# pour être disponibles en mode compilation

version = ('control_flow.py', 1)
print(f"control_flow.py v{version[1]} – structures de contrôle")
# fin du "control_flow" version "1"