# début du "documentation" version "5"
version = ('documentation.py', 5)

def generer_documentation():
    md = """\
£# FORTH ESP32-S3 – Documentation technique complète
£**Version système : 58** – **Date : 28 novembre 2025**
£**Architecture : /lib1 avec détection automatique**
£
£## Architecture des fichiers
£
£- `boot.py` et `main.py` → à la racine
£- Tous les modules → dans `/lib1/` sur cible réelle
£- Sur Wokwi → tout à la racine (pas de dossiers)
£- Détection automatique via `boot.py v16` → variable globale `monDossier`
£- Tous les imports utilisent `monDossier + "fichier.py"`
£- Code identique fonctionne partout
£
£## Vocabulaire Forth – Tableau complet (trié alphabétiquement)
£
£| Mot           | Type        | Action                                                                 |
£|---------------|-------------|------------------------------------------------------------------------|
£| !             | primitive   | Stocke une valeur en mémoire                                           |
£| #             | courant     | Commence formatage numérique                                           |
£| #>            | courant     | Termine formatage numérique                                            |
£| #S            | courant     | Ajoute tous les chiffres restants                                      |
£| '             | immédiat    | Prend l’adresse du mot suivant (tick)                                  |
£| (             | immédiat    | Début de commentaire                                                   |
£| +             | primitive   | Addition                                                               |
£| +LOOP         | immédiat    | Incrémente l’index de boucle                                           |
£| -             | primitive   | Soustraction                                                           |
£| .             | primitive   | Affiche un nombre                                                      |
£| .S            | système     | Affiche la pile de données                                             |
£| /             | primitive   | Division                                                               |
£| <             | primitive   | Inférieur                                                              |
£| <#            | immédiat    | Initialise formatage numérique                                         |
£| =             | primitive   | Égalité                                                                |
£| >             | primitive   | Supérieur                                                              |
£| @             | primitive   | Lit une valeur en mémoire                                              |
£| ABS           | primitive   | Valeur absolue                                                         |
£| AGAIN         | immédiat    | Boucle infinie (vers BEGIN)                                            |
£| AND           | primitive   | ET logique                                                             |
£| BEGIN         | immédiat    | Marque le début d’une boucle                                           |
£| C!            | primitive   | Stocke un octet                                                        |
£| C@            | primitive   | Lit un octet                                                           |
£| CONSTANT      | immédiat    | Définit une constante                                                 |
£| CR            | primitive   | Retour chariot                                                         |
£| CREATE        | courant     | Crée un mot avec champ données                                         |
£| DEPTH         | système     | Retourne la profondeur de pile                                         |
£| DOES>         | immédiat    | Définit le comportement d’un mot créé                                 |
£| DROP          | primitive   | Supprime le sommet de pile                                             |
£| DUP           | primitive   | Duplique le sommet de pile                                             |
£| ELSE          | immédiat    | Branche alternative dans IF                                            |
£| EMIT          | primitive   | Émet un caractère                                                      |
£| EXECUTE       | courant     | Exécute une adresse                                                    |
£| FIND          | courant     | Recherche un mot dans le dictionnaire                                  |
£| FORGET        | courant     | Supprime un mot du dictionnaire                                        |
£| IF            | immédiat    | Branche conditionnelle                                                 |
£| IMMEDIATE     | courant     | Rend le dernier mot immédiat                                           |
£| LOOP          | immédiat    | Incrémente et boucle (DO ... LOOP)                                     |
£| OR            | primitive   | OU logique                                                             |
£| OVER          | primitive   | Copie le deuxième élément sur le sommet                                |
£| RECURSE       | immédiat    | Appel récursif du mot en cours de définition                          |
£| ROT           | primitive   | Rotation de trois éléments                                             |
£| SEE           | système     | Décompile un mot                                                       |
£| SPACE         | primitive   | Émet une espace                                                        |
£| SWAP          | primitive   | Échange les deux éléments du sommet                                    |
£| THEN          | immédiat    | Fin de branche conditionnelle                                          |
£| UNTIL         | immédiat    | Boucle conditionnelle (vers BEGIN)                                     |
£| VARIABLE      | immédiat    | Crée une variable                                                      |
£| VARIABLES     | système     | Liste toutes les variables et constantes                               |
£| VOCABULARY    | courant     | Crée un nouveau vocabulaire                                            |
£| WORDS         | système     | Liste tous les mots (triés par catégorie)                              |
£| XOR           | primitive   | OU exclusif                                                            |
£
£## État actuel
£
£- 100 % fonctionnel sur ESP32-S3 (Xtensa LX6)
£- Architecture propre, portable, professionnelle
£- Prêt pour portage natif C/ESP-IDF
£
£**Prochaine étape : GO PHYSIQUE → silicium réel**
"""
    lignes = [l[1:] if l.startswith('£') else l for l in md.split('\n')]
    with open("FORTH_ESP32S3_DOCUMENTATION.md", "w", encoding="utf-8") as f:
        f.write('\n'.join(lignes))
    print("FORTH_ESP32S3_DOCUMENTATION.md v5 généré – tableau complet des mots")

if __name__ == "__main__":
    generer_documentation()

# fin du "documentation" version "5"