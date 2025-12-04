<!-- Objectifs.md Version 1.0 -->

# Micro Forth
Version 1.0
## Objectif final

J'ai pour objectif de réaliser en bare-metal un programme n'utilisant d'autres ressources que l'assembleur.

- Avoir un programme informatique fonctionnant sur différentes machines modernes : microcontrôleurs 32 bits, FPGA, etc.
- Ce type de programme existe, mais mon objectif n'est pas d'utiliser un programme existant, mais d'en développer un, de le réaliser et de comprendre son fonctionnement dans le détail.
- La partie pédagogique est importante : présentation du fonctionnement en Python et implémentation en assembleur.

## Développement du projet

### Consignes générales

- Le programme sera écrit en MicroPython sans utiliser d'instructions spécifiques à Python, afin qu'il puisse être directement converti en assembleur. Une procédure MicroPython doit correspondre à une procédure assembleur avec les mêmes variables et les mêmes résultats (**Règle n°1**). Par exemple, ne pas utiliser de regex car celles-ci sont difficilement transcodées.

- Les microcontrôleurs actuels sont 32 bits, à la différence des microcontrôleurs des années 70 (origine du Forth) qui étaient 8 bits. Le programme visera ce type de machine 32 bits (**Règle n°2**). Cette différence va changer : l'organisation des piles, peut-être plus de découpage en champs d'un mot, l'arithmétique, l'arithmétique flottante est plus accessible, etc.

- Chaque fichier constituant le programme possède un numéro de version immuable. Au moindre changement, le numéro de version doit être incrémenté afin, pour la traçabilité, d'être sûr en voyant le numéro du contenu du fichier. Ce numéro figurera en première et dernière ligne des fichiers en commentaire avec le nom du fichier. Une variable `version` sera incluse dans les fichiers programme afin qu'un programme puisse afficher sur la console les numéros de versions réellement utilisés (**Règle n°3**). Cela facilitera les échanges d'information.

- Les programmes seront écrits sous Windows sur Notepad++ et seront en UTF-8 mode Unix (fin de ligne `\n` et non `\r\n`). ESP-IDF permettra de faire la compilation, l'édition de lien et le chargement lorsque Thonny ne sera plus utilisé.

## Étapes du programme

Le programme va se dérouler en plusieurs étapes successives :

**1. Simulation en MicroPython sur microcontrôleur ESP32-S3N16R8**
   - Utilisation de la version gratuite en ligne Wokwi
   - Au terme de cette étape, tout le code doit être généré et testé
   - Version actuelle de MicroPython : `micropython-20231227-v1.22.0`

**2. Portage sur kit physique**
   - Le code précédent est copié sans modification (**Règle n°3**) dans le logiciel Thonny pour qu'il soit chargé sur un kit ESP32-S3N16R8 Wroom
   - Les fonctionnalités seront à nouveau testées entièrement
   - Binaire MicroPython : `ESP32_GENERIC_S3-SPIRAM_OCT-20250911-v1.26.1.bin`

**3. Compilation des vocabulaires**
   - Les fichiers de code en MicroPython réalisant le vocabulaire primaire (Forth primaire) liront et compileront les macros des autres vocabulaires
   - La plage mémoire correspondante sera stockée dans un fichier binaire `forth.S` qui sera incorporé (si `forth.S` existe) au programme Forth primaire, évitant ainsi une recompilation inutile

**4. Transcodage en assembleur**
   - Les fichiers (Forth primaire) seront transcodés en assembleur, mis à part la partie `boot.py` qui restera pour faciliter les tests à partir de Thonny

**5. Boot assembleur**
   - Un boot sera écrit en assembleur pour être lié au Forth primaire assembleur précédent
   
<!-- Objectifs.md Version 1.0 -->
   