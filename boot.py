# début du "boot" version "27"
version = ('boot.py', 27)
import os
import sys
import time

MON_DOSSIER = "lib1/" if "lib1" in os.listdir() else ""

print("\n" + "="*72)
print(" FORTH ESP32-S3 – INITIALISATION (boot.py v27)")
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

# Modules Python (noyau Forth - seront transcodés en assembleur)
modules = [
    'boot.py',           # Initialisation système
    'main.py',           # REPL et interpréteur
    'memoire.py',        # Gestion RAM 512KB
    'piles.py',          # Piles données/retour
    'dictionnaire.py',   # Gestion mots
    'core_primitives.py',# 21 primitives de base
    'core_system.py',    # WORDS, SEE, VARIABLES
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

# Bibliothèques Forth (.v = vocabulaire)
bibliotheques = [
    ('stdlib_minimal.v', 1.0),   # Vocabulaire général (2DUP, MOD, IF, etc.)
    ('esp32.v', 1.0),             # Matériel ESP32 (GPIO, Time, NeoPixel)
    ('applicatif.v', 1.0),        # Utilitaires généraux (LED, BUTTON, etc.)
    ('apps/3leds.v', 1.0),        # Application: 3 LED clignotantes
    ('apps/arcenciel.v', 1.0),    # Application: Arc-en-ciel NeoPixel
]

print("\nBibliothèques Forth (.v):")
for nom, version_attendue in bibliotheques:
    chemin = MON_DOSSIER + nom if MON_DOSSIER else nom
    try:
        with open(chemin, 'r') as f:
            # Chercher version dans les 10 premières lignes
            version_trouvee = None
            for i, ligne in enumerate(f):
                if i > 10:
                    break
                if 'Version' in ligne or 'version' in ligne:
                    # Extraire numéro (format: Version 1.0 ou version = 1.0)
                    import re
                    match = re.search(r'(\d+\.\d+)', ligne)
                    if match:
                        version_trouvee = match.group(1)
                        break
            
            src = "lib1" if MON_DOSSIER else "racine"
            if version_trouvee:
                status = "✓" if float(version_trouvee) == version_attendue else "⚠"
                print(f"  {status} {nom:25} → v{version_trouvee:<6} [{src}]")
            else:
                print(f"  ? {nom:25} → v?       [{src}]")
    except OSError:
        print(f"  ✗ {nom:25} → [absent]")

print("="*72)
print("boot.py v27 terminé – MON_DOSSIER dans globals()\n")

# fin du "boot" version "27"