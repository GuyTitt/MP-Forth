# début du "boot" version "23"
version = ('boot.py', 23)
import os

# ================================================
# UNIQUE SOURCE DE VÉRITÉ : Détection du dossier
# ================================================
MON_DOSSIER = "lib1/" if "lib1" in os.listdir() else ""

print("\n" + "="*72)
print(" FORTH ESP32-S3 – INITIALISATION (boot.py v23)")
print(f" Dossier modules → '{MON_DOSSIER or 'racine'}'")
print("="*72)

# Affichage des versions
modules = [
    'memoire.py', 'piles.py', 'dictionnaire.py',
    'core_primitives.py', 'core_system.py', 'core_system1.py',
    'words_level1.py', 'tests.py', 'main.py'
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
        print(f"  {nom:25} → [introuvable]")

print("="*72)
print("boot.py v23 terminé – MON_DOSSIER dans globals()\n")

# fin du "boot" version "23"