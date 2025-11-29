# début du "interpreteur" version "1"
import uasyncio as asyncio
from primitives import prims
from piles import piles

class Interpreteur:
    def __init__(self):
        self.dict = prims.copy()

    async def executer(self, mot):
        mot = mot.upper()
        if mot in self.dict:
            await self.dict[mot]()
        elif mot.isdigit() or (mot.startswith('-') and mot[1:].isdigit()):
            await piles.push(int(mot))
        else:
            print(f"? {mot}")

interp = Interpreteur()
version = ('interpreteur.py', 1)
print(f"Chargement module: {version}")
# fin du "interpreteur" version "1"