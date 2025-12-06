# début du "boot" version "2.0"
version = ('boot.py', 2.0)
import os
import sys
import time

# Détection dossier lib1 (pour migration future)
MON_DOSSIER = "lib1/" if "lib1" in os.listdir() else ""

print("\n" + "="*72)
print(" FORTH ESP32-S3 — INITIALISATION (boot.py v2.0)")
print(f" Dossier modules → '{MON_DOSSIER or 'racine'}'")
print("="*72)

# ==========================================
# PAUSE INTERRUPTIBLE AU DÉMARRAGE
# ==========================================
print("\nDémarrage dans 3 secondes...")
print("Appuyez sur Ctrl+C pour annuler et rester en REPL Python\n")

try:
    for i in range(3, 0, -1):
        print(f"  {i}...", end='')
        time.sleep(1)
    print(" GO!\n")
except KeyboardInterrupt:
    print("\n\n[ANNULÉ] Démarrage Forth interrompu")
    print("Vous êtes en REPL Python - tapez 'import main' pour lancer Forth\n")
    sys.exit()

# ==========================================
# AFFICHAGE VERSIONS MODULES PYTHON
# ==========================================

modules = [
    'boot.py',
    'main.py',
    'memoire.py',
    'piles.py',
    'dictionnaire.py',
    'core_primitives.py',
    'core_system.py',
]

print("Modules Python (→ Assembleur):")
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

# ==========================================
# AFFICHAGE VERSIONS BIBLIOTHÈQUES FORTH
# ==========================================

bibliotheques = [
    ('base.txt', 2.0),
    ('esp32.txt', 2.0),
    ('utils.txt', 2.0),
]

print("\nBibliothèques Forth (.txt):")
for nom, version_attendue in bibliotheques:
    chemin = MON_DOSSIER + nom if MON_DOSSIER else nom
    try:
        with open(chemin, 'r') as f:
            version_trouvee = None
            for i, ligne in enumerate(f):
                if i > 10:
                    break
                if 'Version' in ligne or 'version' in ligne:
                    import re
                    match = re.search(r'(\d+\.\d+)', ligne)
                    if match:
                        version_trouvee = match.group(1)
                        break
            
            src = "lib1" if MON_DOSSIER else "racine"
            if version_trouvee:
                print(f"  ✓ {nom:25} → v{version_trouvee:<6} [{src}]")
            else:
                print(f"  ? {nom:25} → v?       [{src}]")
    except OSError:
        print(f"  ✗ {nom:25} → [absent]")

print("="*72)
print("boot.py v2.0 terminé — MON_DOSSIER dans globals()\n")

# fin du "boot" version "2.0"