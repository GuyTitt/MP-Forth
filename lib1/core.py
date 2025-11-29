# début du "core" version "34"
version = ('core.py', 34)

print("Chargement core en deux parties...")
import core_primitives
import core_system

# Export explicite du dispatch global pour main.py
from core_primitives import dispatch

# Export des marqueurs pour main.py
from core_primitives import (
    MARK_THEN, MARK_BEGIN, MARK_DO, MARK_LOOP,
    OP_DO, OP_LOOP, OP_PLOOP, OP_ZBRANCH, OP_BRANCH
)

print(f"fin de {version[0]} v{version[1]} – dispatch et marqueurs exportés")
# fin du "core" version "34"