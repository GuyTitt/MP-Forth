# Guide Pédagogique - Interpréteur Forth ESP32-S3

**Version 1.1** - Documentation complète du système

---

## 📋 Table des matières

1. [Architecture générale](#architecture)
2. [Structure de la mémoire](#memoire)
3. [Le dictionnaire](#dictionnaire)
4. [Les vocabulaires](#vocabulaires)
5. [Flux d'exécution](#execution)
6. [Détail des modules](#modules)
7. [Multitâche et Concurrence](#multitasking)

---

## 🏗️ Architecture générale {#architecture}

### Hiérarchie des modules

```
boot.py (lancé au reset)
  └── main.py
       ├── memoire.py         (RAM 512KB)
       ├── piles.py           (gestion piles)
       ├── dictionnaire.py    (mots/lookup)
       ├── core_primitives.py (opcodes 1-200)
       ├── core_system.py     (mots système)
       ├── core_system1.py    (CREATE/DOES>)
       ├── core_level2.py     (mots Forth niveau 2)
       ├── core_hardware.py   (GPIO, Time, NeoPixel)
       └── stdlib.f4          (bibliothèque Forth pure - optionnel)
```

### Versions actuelles

| Module | Version | Rôle |
|--------|---------|------|
| boot.py | v25 | Initialisation système |
| main.py | v74 | REPL principal |
| memoire.py | v17 | Gestion mémoire (adaptative) |
| piles.py | v15 | Piles données/retour |
| dictionnaire.py | v30 | Recherche/création mots |
| core_primitives.py | v36 | Primitives bas niveau |
| core_system.py | v46 | Vocabulaire système |
| core_system1.py | v2 | Mots avancés |
| core_level2.py | v1 | Mots Forth compilés |
| core_hardware.py | v2 | GPIO, Time, NeoPixel |
| stdlib.v | v1.0 | Bibliothèque Forth pure |

---

## 💾 Gestion de la mémoire - Important !

### Tailles RAM selon les cartes

| Carte | RAM interne | PSRAM | Total disponible |
|-------|-------------|-------|------------------|
| ESP32-S3 basique | ~320KB | 0 | ~320KB |
| ESP32-S3N8 | ~320KB | 8MB | ~8.3MB |
| ESP32-S3N16R8 | ~320KB | 8MB | ~8.3MB (si PSRAM activée) |
| Wokwi (simulation) | Illimité | - | Illimité |

### Allocation mémoire adaptative (v17)

`memoire.py v17` détecte automatiquement la RAM disponible et alloue :
- **512KB** si possible (Wokwi, cartes avec PSRAM)
- **256KB** si échec (ESP32-S3 sans PSRAM)
- **128KB** en dernier recours
- **64KB** minimum requis

**Sortie typique** :
```
RAM Forth allouée: 256KB (libre: 180KB)
  Zones: Dict=0x100-0x100, Piles=0x3ff00-0x3fff0
```

### Problème PSRAM non détectée

Si vous voyez :
```
E (301) quad_psram: PSRAM ID read error
```

**Solutions** :
1. Utiliser la version adaptative (memoire.py v17) ✅
2. Activer PSRAM dans sdkconfig de MicroPython (complexe)
3. Accepter 256KB au lieu de 512KB (largement suffisant)

---

## 💾 Structure de la mémoire {#memoire}

### Cartographie mémoire (512KB = 0x80000 octets)

```
0x00000 ┌─────────────────────────┐
        │  Zone réservée          │
0x00100 ├─────────────────────────┤
        │  DICTIONNAIRE           │
        │  (headers + code)       │
        │  ↓ croît vers le haut   │
mem.here├─────────────────────────┤
        │                         │
        │  Zone libre             │
        │                         │
0x7FF00 ├─────────────────────────┤
        │  ↓ PILE RETOUR (RP)     │
mem.rp  │  (DO/LOOP, appels)      │
0x7FFF0 ├─────────────────────────┤
        │  ↓ PILE DONNÉES (SP)    │
mem.sp  │  (calculs Forth)        │
0x80000 └─────────────────────────┘
```

### Pointeurs clés

- **mem.here** : prochaine adresse libre pour compilation (croît ↑)
- **mem.sp** : sommet pile données (décroît ↓)
- **mem.rp** : sommet pile retour (décroît ↓)
- **mem.latest** : dernier mot défini (tête de liste chaînée)
- **mem.state** : 0=interprétation, 1=compilation

---

## 📖 Le dictionnaire {#dictionnaire}

### Structure d'un mot

Chaque mot est un enregistrement chaîné :

```
       ┌─────────────────────┐
       │  LINK (4 octets)    │ ← pointe vers mot précédent
       ├─────────────────────┤
       │  FLAGS+LENGTH (1)   │ ← bit 7=immediate, bits 0-6=longueur
       ├─────────────────────┤
       │  NAME (n octets)    │ ← nom en ASCII
       ├─────────────────────┤
       │  [padding]          │ ← alignement 4 octets
       ├─────────────────────┤
       │  CODE FIELD (4)     │ ← opcode ou adresse code
       └─────────────────────┘
```

### Exemple : mot `DUP`

```
Adresse   Contenu       Signification
0x0194    0x00000000    LINK (premier mot, pas de précédent)
0x0198    0x03          LENGTH=3, immediate=0
0x0199    'D'           
0x019A    'U'           Nom "DUP"
0x019B    'P'           
0x019C    [padding]     Alignement
0x019D    0x00000001    CODE=1 (opcode primitive DUP)
```

### Recherche dans le dictionnaire

La fonction `find(name)` parcourt la liste chaînée :

1. Commence à `mem.latest`
2. Compare le nom
3. Si trouvé → retourne (code, immediate)
4. Sinon → suit le LINK vers mot précédent
5. Si LINK=0 → mot introuvable

---

## 🎯 Les vocabulaires {#vocabulaires}

### 1. Vocabulaire PRIMITIF (niveau 0)

**Rôle** : Opérations atomiques directement en Python

**Exemples** :
```python
OP_DUP = 1      # Duplique sommet pile
OP_ADD = 6      # Addition
OP_FETCH = 13   # Lecture mémoire @
OP_DOT = 17     # Affichage .
```

**Caractéristiques** :
- Opcodes 1-199
- Implémentés en `async def prim_xxx()`
- Table `dispatch = {opcode: fonction}`
- Exécution directe sans interprétation

### 2. Vocabulaire SYSTÈME (niveau 1)

**Rôle** : Mots compilés à partir des primitives

**Exemples** :
```forth
: ABS ( n -- |n| )
  DUP 0< IF NEGATE THEN ;

: MIN ( a b -- min )
  2DUP > IF SWAP THEN DROP ;
```

**Caractéristiques** :
- Opcodes >= 1000 (adresses mémoire)
- Compilés dans la zone dictionnaire
- Corps = séquence d'opcodes + EXIT

### 3. Vocabulaire NIVEAU 2 (core_level2.py)

**Rôle** : Mots Forth standards compilés en Python

**Exemples** :
- `?DUP` - Duplique si non-zéro
- `*/` - Multiplication puis division
- `/MOD` - Division avec modulo
- `2SWAP` `2OVER` - Manipulation doubles

### 4. Vocabulaire SPÉCIALISÉ (matériel)

**Rôle** : Interaction avec le microcontrôleur ESP32-S3

**Domaines** :
- **GPIO** : PIN-OUT, PIN-IN, PIN-HIGH, PIN-LOW, PIN-READ, PIN-TOGGLE
- **TIME** : MS, US, TICKS-MS, TICKS-US, TICKS-DIFF
- **NEOPIXEL** : NEO-INIT, NEO-SET, NEO-WRITE, NEO-FILL, NEO-CLEAR
- **À venir** : UART, WiFi, ADC, PWM, Timers, Interruptions, RTC

**Exemple** :
```forth
: LED-ON  ( pin -- )
  DUP PIN-OUT PIN-HIGH ;

: READ-TEMP ( -- temp )
  ADC-CHANNEL-0 ADC-READ
  3300 * 4095 / ; \ Conversion en mV
```

### 5. Vocabulaire APPLICATIF (utilisateur)

**Rôle** : Logique métier de l'application

**Exemples** :
```forth
VARIABLE compteur
: INCREMENTER  compteur @ 1+ compteur ! ;

: FIBONACCI ( n -- fib[n] )
  0 1 ROT 0 DO OVER + SWAP LOOP DROP ;

: CLIGNOTER ( pin times delay -- )
  >R >R DUP PIN-OUT 
  R> 0 DO DUP PIN-TOGGLE R@ MS LOOP 
  DROP R> DROP ;
```

### 6. Bibliothèque stdlib.f4

**Rôle** : Implémentations Forth pures (pour migration vers Forth pur)

Le fichier `stdlib.f4` contient toutes les définitions en Forth pur, organisées par niveau. Ces définitions peuvent remplacer progressivement les implémentations Python.

---

## ⚙️ Flux d'exécution {#execution}

### Mode INTERPRÉTATION (mem.state=0)

```
Saisie utilisateur
   ↓
Tokenisation (split par espaces)
   ↓
Pour chaque token :
   ├─ Nombre ? → empiler sur pile données
   ├─ Mot trouvé ?
   │  ├─ Primitive (opcode < 1000) → execute_primitive()
   │  └─ Colon (opcode >= 1000) → execute_colon()
   └─ Sinon → "? token"
```

### Mode COMPILATION (mem.state=1)

```
Saisie utilisateur (après :)
   ↓
Pour chaque token :
   ├─ Nombre ? → compiler LIT + valeur
   ├─ Mot immédiat ? → exécuter immédiatement
   └─ Mot normal ? → compiler opcode
   
Fin avec ; → compiler EXIT, mem.state=0
```

### Exécution d'un mot COLON

```python
async def execute_colon(addr):
    mem.ip = addr
    while True:
        opcode = mem.wpeek(mem.ip)
        mem.ip += 4
        
        if opcode == 0:        # EXIT
            break
        elif opcode == 21:     # LIT
            val = mem.wpeek(mem.ip)
            mem.ip += 4
            await piles.push(val)
        elif opcode < 1000:    # Primitive
            await execute_primitive(opcode)
        else:                  # Autre mot colon
            await execute_colon(opcode)  # Récursion
```

---

## 🔧 Détail des modules {#modules}

### boot.py (v23)

**Rôle** : Point d'entrée au reset

**Actions** :
1. Détecte si dossier `lib1/` existe
2. Affiche versions de tous les modules
3. Définit `MON_DOSSIER` dans globals()
4. Lance `main.py`

**Modules testés** :
- boot.py, main.py, memoire.py, piles.py
- dictionnaire.py, core_primitives.py, core_system.py, core_system1.py
- core_level2.py, core_hardware.py
- words_level1.py (optionnel), tests.py (optionnel), stdlib.f4 (optionnel)

---

### main.py (v72)

**Rôle** : REPL (Read-Eval-Print Loop)

**Fonctions clés** :
- `charger(nom)` : charge modules Python
- `handle_control_flow()` : gère IF/THEN/DO/LOOP
- `execute_primitive()` : appelle dispatch[opcode]
- `execute_colon()` : interprète mots compilés
- `repl()` : boucle principale

**Variable de configuration** :
```python
USE_FORTH_STDLIB = False  # True = utilise stdlib.f4
```

**Flux** :
```python
charger tous les modules
  ↓
boucle infinie :
  ├─ input(prompt)
  ├─ parser ligne
  ├─ pour chaque token :
  │  └─ interpréter ou compiler
  └─ gérer erreurs
```

---

### memoire.py (v15)

**Rôle** : Abstraction mémoire RAM

**Classe Memoire** :
```python
ram = bytearray(512*1024)  # 512KB
here = 256                  # Zone dict commence à 0x100
latest = 0                  # Dernier mot défini
state = 0                   # Mode interprétation
sp = 0x7FFF0               # Top pile données
rp = 0x7FF00               # Top pile retour
```

**Méthodes** :
- `wpoke(addr, val)` : écrit 32 bits little-endian
- `wpeek(addr)` : lit 32 bits
- `cpoke(addr, val)` : écrit 8 bits
- `cpeek(addr)` : lit 8 bits

---

### piles.py (v14)

**Rôle** : Gestion des 2 piles

**Pile DONNÉES (SP)** :
- Calculs Forth standard
- Opérations : `push()`, `pop()`
- Croît vers le bas (0x7FFF0 → 0x7FF00)

**Pile RETOUR (RP)** :
- Adresses de retour (appels)
- Compteurs DO/LOOP
- Opérations : `rpush()`, `rpop()`
- Croît vers le bas (0x7FF00 → ...)

---

### dictionnaire.py (v30)

**Rôle** : Création et recherche de mots

**Fonctions** :
- `align_here()` : aligne sur 4 octets
- `create(name, code, immediate)` : crée header
- `create_colon_word(name, body_addr)` : crée mot colon
- `find(name)` : recherche mot → (code, imm)
- `see_word(name)` : décompilation

**Format header** : voir section [Dictionnaire](#dictionnaire)

---

### core_primitives.py (v35)

**Rôle** : Primitives bas niveau

**Catégories** :
- **Pile** : DUP DROP SWAP OVER ROT 2DUP 2DROP NIP TUCK
- **Arithmétique** : + - * / MOD ABS 1+ 1- 2* 2/ NEGATE
- **Comparaison** : < > = <> 0< 0= 0> U<
- **Mémoire** : @ ! C@ C! +@ +!
- **I/O** : . CR EMIT SPACE SPACES
- **Logique** : AND OR XOR NOT INVERT LSHIFT RSHIFT
- **Contrôle** : IF ELSE THEN BEGIN UNTIL WHILE REPEAT AGAIN DO LOOP +LOOP I J UNLOOP

**Table dispatch** :
```python
dispatch = {
    1: prim_dup,
    6: prim_add,
    13: prim_fetch,
    ...
}
```

---

### core_system.py (v46)

**Rôle** : Vocabulaire système niveau 1

**Actions** :
1. Importe primitives
2. Définit mots système (WORDS, SEE, .S, VARIABLES...)
3. Crée tous les mots dans le dictionnaire
4. Charge core_system1.py

**Mots créés** : EXIT, DUP, +, -, IF, THEN, DO, LOOP, WORDS, MIN, MAX, VARIABLE, CONSTANT, HERE, ALLOT, , , C,

---

### core_system1.py (v2)

**Rôle** : Mots avancés

**Mots** :
- CREATE / DOES> (création mots personnalisés)
- VARIABLE / CONSTANT
- VOCABULARY (espaces de noms)
- IMMEDIATE (mots immédiats)
- EXECUTE (exécution dynamique)
- FIND, COMPILE, [, ], [COMPILE], '
- Formatage numérique : #, <#, #>, #S

---

### core_level2.py (v1)

**Rôle** : Mots Forth niveau 2 compilés en Python

**15 mots définis** :
- ?DUP, */, /MOD, WITHIN
- PICK, ROLL, 2SWAP, 2OVER
- ABS (version colon), S>D
- M*, UM*, FM/MOD, SM/REM, UM/MOD

---

### core_hardware.py (v2)

**Rôle** : Vocabulaire matériel ESP32-S3

**GPIO (8 mots)** :
- PIN-OUT, PIN-IN - Configuration
- PIN-HIGH, PIN-LOW - Écriture
- PIN-READ - Lecture
- PIN-TOGGLE - Inversion
- PIN-PULLUP, PIN-PULLDOWN - Résistances

**TIME (5 mots)** :
- MS, US - Pauses
- TICKS-MS, TICKS-US - Timestamps
- TICKS-DIFF - Calcul durée

**NEOPIXEL (5 mots)** :
- NEO-INIT - Initialise strip WS2812
- NEO-SET - Définit couleur RGB d'une LED
- NEO-WRITE - Affiche changements
- NEO-FILL - Remplit toutes les LEDs
- NEO-CLEAR - Éteint tout

**Exemple NeoPixel** :
```forth
\ LED interne LilyGO T-Display-S3 (GPIO48)
48 1 NEO-INIT           ( 1 LED sur GPIO48 )
48 0 255 0 0 NEO-SET    ( Rouge )
48 NEO-WRITE            ( Affiche )
1000 MS
48 0 0 255 0 NEO-SET    ( Vert )
48 NEO-WRITE
1000 MS
48 NEO-CLEAR            ( Éteint )
```

---

### stdlib.f4 (v1.0)

**Rôle** : Bibliothèque Forth pure (préparation migration)

**Contenu organisé par niveau** :
1. **Niveau 1** - Mots de base (pile, arithmétique, comparaisons)
2. **Niveau 2** - Structures de contrôle (?DO, CASE/ENDCASE)
3. **Niveau 3** - I/O formaté (.", S", .R, HEX, DECIMAL)
4. **Niveau 4** - Hardware (LED-INIT, BLINK, NEO-RAINBOW)
5. **Niveau 5** - Algorithmes (SQRT, GCD, FIB, BUBBLE-SORT)
6. **Niveau 6** - Multitâche (TASK, PAUSE, SLEEP)

**Utilisation** :
```forth
\ Charger dans Forth
LOAD stdlib.f4

\ Ou inclure au démarrage dans main.py
USE_FORTH_STDLIB = True
```

---

## 🔄 Multitâche et Concurrence {#multitasking}

### Problématique

Comment faire clignoter plusieurs LEDs à des fréquences différentes sans qu'elles s'influencent ?

```forth
\ On veut ceci simultanément:
LED1 clignote à 500ms
LED2 clignote à 300ms
LED3 clignote à 1000ms
```

### Solution 1 : Multitâche COOPÉRATIF

**Principe** : Chaque tâche s'exécute un peu puis passe la main volontairement avec `PAUSE`.

```
Tâche 1: LED1 ON → PAUSE → LED1 OFF → PAUSE → recommence
Tâche 2: LED2 ON → PAUSE → LED2 OFF → PAUSE → recommence
Tâche 3: LED3 ON → PAUSE → LED3 OFF → PAUSE → recommence
```

**Architecture** :

```
Task Control Block (TCB) - 32 octets par tâche:
┌────────────┬─────┬────────────────────────┐
│ Offset     │ Size│ Description            │
├────────────┼─────┼────────────────────────┤
│ +0         │  4  │ LINK → prochaine tâche │
│ +4         │  4  │ SP (pile données)      │
│ +8         │  4  │ RP (pile retour)       │
│ +12        │  4  │ STATUS (0=prête,1=sus) │
│ +16        │  4  │ IP (instruction ptr)   │
│ +20        │  4  │ WAKE-TIME (réveil)     │
│ +24        │  8  │ NAME (nom tâche)       │
└────────────┴─────┴────────────────────────┘
```

**Implémentation** : Voir stdlib.f4 niveau 6

**Exemple complet** :
```forth
\ Définir les tâches
TASK led1-task
TASK led2-task  
TASK led3-task

: led1-loop ( -- )
  BEGIN 2 PIN-HIGH 500 SLEEP 2 PIN-LOW 500 SLEEP AGAIN ;

: led2-loop ( -- )
  BEGIN 3 PIN-HIGH 300 SLEEP 3 PIN-LOW 300 SLEEP AGAIN ;

: led3-loop ( -- )
  BEGIN 4 PIN-HIGH 1000 SLEEP 4 PIN-LOW 1000 SLEEP AGAIN ;

\ Initialiser
: INIT-TASKS
  2 PIN-OUT 3 PIN-OUT 4 PIN-OUT
  ' led1-loop led1-task ACTIVATE
  ' led2-loop led2-task ACTIVATE
  ' led3-loop led3-task ACTIVATE
  led1-task CURRENT-TASK ! ;

\ Scheduler principal
: RUN-TASKS INIT-TASKS BEGIN WAKE-TASKS PAUSE KEY? UNTIL ;
```

### Solution 2 : Asyncio MicroPython (actuel)

Notre implémentation utilise `uasyncio` de MicroPython :

```python
async def task1():
    while True:
        pin2.value(1)
        await asyncio.sleep_ms(500)
        pin2.value(0)
        await asyncio.sleep_ms(500)

async def task2():
    while True:
        pin3.value(1)
        await asyncio.sleep_ms(300)
        pin3.value(0)
        await asyncio.sleep_ms(300)

# Lance tout
asyncio.gather(task1(), task2())
```

### Solution 3 : Timer Hardware ESP32

Utiliser les timers matériels pour déclencher des interruptions.

### Comparaison des approches

| Approche | Avantages | Inconvénients |
|----------|-----------|---------------|
| **Coopératif Forth** | Contrôle total, léger | Nécessite PAUSE régulier |
| **Asyncio Python** | Simple, robuste | Dépend de MicroPython |
| **Timer hardware** | Précis, sans surcharge | Limité par nb de timers |

---

## 📚 Références

- **ANS Forth Standard** : https://forth-standard.org/
- **ESP32-S3 Datasheet** : Documentation Espressif
- **MicroPython** : https://docs.micropython.org/

---

*Guide rédigé pour le projet Forth ESP32-S3 - Version 1.1*