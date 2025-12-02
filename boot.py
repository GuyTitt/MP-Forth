# début du "boot" version "24"
version = ('boot.py', 24)
import os

MON_DOSSIER = "lib1/" if "lib1" in os.listdir() else ""

print("\n" + "="*72)
print(" FORTH ESP32-S3 – INITIALISATION (boot.py v24)")
print(f" Dossier modules → '{MON_DOSSIER or 'racine'}'")
print("="*72)

# Modules requis par le système
modules = [
    'boot.py',
    'main.py', 
    'memoire.py',
    'piles.py',
    'dictionnaire.py',
    'core_primitives.py',
    'core_system.py',
    'core_system1.py',
    'core_level2.py',
    'core_hardware.py',
]

# Modules optionnels
modules_optionnels = [
    'tests.py',
    'stdlib.f4',
]

for nom in modules:
    chemin = MON_DOSSIER + nom if MON_DOSSIER else nom
    try:
        with open(chemin, 'r') as f:
            for ligne in f:
                if 'version' in ligne and '=' in ligne:
                    partie = ligne.split('=', 1)[1].strip()
                    if partie.startswith('('):
                        fichier, num = eval(partie)
                        src = "lib1" if MON_DOSSIER else "racine"
                        print(f"  {fichier:25} → v{num:<6} [{src}]")
                    break
    except OSError:
        print(f"  {nom:25} → [ERREUR: introuvable]")

print("="*72)
print("boot.py v24 terminé – MON_DOSSIER dans globals()\n")

# fin du "boot" version "24"