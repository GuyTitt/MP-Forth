# début du "versions" version "7"
import os

modules = [
    'memoire',
    'dictionnaire',
    'piles',
    'core',
    'boot',
    'interpreteur',
    'tests',
    'options',
    'primitives',
    'words_level1',
    'control_flow',
]

def lire_version(nom):
    try:
        chemin = '/lib1/' + nom + '.py'
        with open(chemin, 'r') as f:
            for ligne in f:
                ligne = ligne.strip()
                if ligne.startswith('version'):
                    if "=('" in ligne or '= ("' in ligne:
                        debut = ligne.find("'") + 1
                        fin = ligne.find("'", debut)
                        if debut > 0 and fin > debut:
                            fichier = ligne[debut:fin]
                        else:
                            fichier = nom + '.py'
                        num = ligne.split(',', 1)[1].strip(" )")
                        if num.isdigit():
                            return (fichier, int(num))
    except:
        pass
    return None

def show_versions():
    print("\n" + "="*64)
    print(" VERSIONS DES MODULES DANS /lib1 (lecture statique)")
    print("="*64)
    for nom in modules:
        info = lire_version(nom)
        if info:
            print(f"  {info[0]:25} → v{info[1]:<4} [présent]")
        else:
            print(f"  {nom}.py{' ':21} → [absent ou sans version]")
    print("="*64)

version = ('versions.py', 7)
# fin du "versions" version "7"