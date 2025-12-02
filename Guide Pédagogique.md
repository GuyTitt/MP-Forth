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
       └── core_system1.py    (CREATE/DOES>)
```

### Versions actuelles

| Module | Version | Rôle |
|--------|---------|------|
| boot.py | v23 | Initialisation système |
| main.py | v66 | REPL principal |
| memoire.py | v14 | Gestion mémoire |
| piles.py | v13 | Piles données/retour |
| dictionnaire.py | v28 | Recherche/création mots |
| core_primitives.py | v35 | Primitives bas niveau |
| core_system.py | v44 | Vocabulaire système |
| core_system1.py | v2 | Mots avancés |

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

### 3. Vocabulaire SPÉCIALISÉ (matériel)

**Rôle** : Interaction avec le microcontrôleur ESP32-S3

**Domaines** :
- **UART** : communication série
- **WiFi** : réseau sans fil
- **GPIO** : entrées/sorties digitales
- **ADC** : conversion analogique-numérique
- **PWM** : modulation largeur d'impulsion
- **Timers** : gestion du temps
- **Interruptions** : événements asynchrones
- **RTC** : horloge temps réel

**Exemple** :
```forth
: LED-ON  ( pin -- )
  OUTPUT-MODE     \ Configure en sortie
  1 SWAP GPIO! ;  \ Écrit HIGH

: READ-TEMP ( -- temp )
  ADC-CHANNEL-0 ADC-READ
  3300 * 4095 / ; \ Conversion en mV
```

### 4. Vocabulaire APPLICATIF (utilisateur)

**Rôle** : Logique métier de l'application

**Exemples** :
```forth
VARIABLE compteur
: INCREMENTER  compteur @ 1+ compteur ! ;

: FIBONACCI ( n -- fib[n] )
  0 1 ROT 0 DO OVER + SWAP LOOP DROP ;

: CLIGNOTER ( n -- )
  0 DO
    LED-ON 500 MS
    LED-OFF 500 MS
  LOOP ;
```

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

**Note** : N'est PAS appelé par un autre module, c'est le système qui l'exécute.

---

### main.py (v66)

**Rôle** : REPL (Read-Eval-Print Loop)

**Fonctions clés** :
- `charger(nom)` : charge modules Python
- `handle_control_flow()` : gère IF/THEN/DO/LOOP
- `execute_primitive()` : appelle dispatch[opcode]
- `execute_colon()` : interprète mots compilés
- `repl()` : boucle principale

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

### memoire.py (v14)

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

### piles.py (v13)

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

### dictionnaire.py (v28)

**Rôle** : Création et recherche de mots

**Fonctions** :
- `align_here()` : aligne sur 4 octets
- `create(name, code, immediate)` : crée header
- `find(name)` : recherche mot → (code, imm)
- `see_word(name)` : décompilation

**Format header** : voir section [Dictionnaire](#dictionnaire)

---

### core_primitives.py (v35)

**Rôle** : Primitives bas niveau

**Catégories** :
- **Pile** : DUP DROP SWAP OVER ROT 2DUP...
- **Arithmétique** : + - * / MOD ABS 1+ 1-...
- **Comparaison** : < > = 0< 0=...
- **Mémoire** : @ ! C@ C!...
- **I/O** : . CR EMIT SPACE...
- **Logique** : AND OR XOR NOT INVERT...
- **Contrôle** : IF THEN DO LOOP...

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

### core_system.py (v44)

**Rôle** : Vocabulaire système niveau 1

**Actions** :
1. Importe primitives
2. Définit mots système (WORDS, SEE, .S...)
3. Crée tous les mots dans le dictionnaire
4. Charge core_system1.py

**Mots créés** : EXIT, DUP, +, -, IF, THEN, DO, LOOP, WORDS...

---

### core_system1.py (v2)

**Rôle** : Mots avancés

**Mots** :
- CREATE / DOES> (création mots personnalisés)
- VARIABLE / CONSTANT
- VOCABULARY (espaces de noms)
- IMMEDIATE (mots immédiats)
- EXECUTE (exécution dynamique)

---

## 🐛 Problèmes connus

### Erreur "wpeek overflow" lors appel mot colon

**Cause** : L'adresse du code n'est pas correctement sauvegardée

**Solution** : Voir correction dans main.py v67

---

## 📚 Références

- **ANS Forth Standard** : https://forth-standard.org/
- **ESP32-S3 Datasheet** : Documentation Espressif
- **MicroPython** : https://docs.micropython.org/

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

**Implémentation Forth** :

```forth
VARIABLE TASK-LIST     \ Liste chaînée des tâches
VARIABLE CURRENT-TASK  \ Tâche en cours

: TASK ( size "name" -- addr )
  \ Crée TCB + espace piles
  CREATE 
    HERE TASK-LIST @ , TASK-LIST !  \ Chaîne
    HERE 32 + ,  \ SP
    HERE 32 + ,  \ RP
    0 ,          \ STATUS
    0 ,          \ IP
    0 ,          \ WAKE-TIME
    0 , 0 ,      \ NAME
  32 ALLOT       \ Espace piles locales
  DOES> ;

: ACTIVATE ( xt task -- )
  \ Lance une tâche
  SWAP OVER 16 + !    \ Sauve IP
  0 OVER 12 + ! ;     \ STATUS = prête

: PAUSE ( -- )
  \ Sauvegarde contexte et change de tâche
  \ 1. Sauver SP, RP, IP de la tâche courante
  \ 2. Trouver prochaine tâche prête
  \ 3. Restaurer SP, RP, IP de la nouvelle tâche
  CURRENT-TASK @ DUP
  SP@ SWAP 4 + !       \ Sauve SP
  RP@ SWAP 8 + !       \ Sauve RP
  @ DUP CURRENT-TASK ! \ Tâche suivante
  DUP 4 + @ SP!        \ Restaure SP
  8 + @ RP! ;          \ Restaure RP

: SLEEP ( ms -- )
  \ Suspend tâche pendant ms
  TICKS-MS + CURRENT-TASK @ 20 + ! 
  1 CURRENT-TASK @ 12 + !  \ STATUS = suspendue
  PAUSE ;

: WAKE-TASKS ( -- )
  \ Réveille tâches dont le délai a expiré
  TASK-LIST @ 
  BEGIN ?DUP WHILE
    DUP 12 + @ 1 = IF  \ Si suspendue
      DUP 20 + @ TICKS-MS < IF  \ Si délai expiré
        0 OVER 12 + !  \ STATUS = prête
      THEN
    THEN
    @ 
  REPEAT ;
```

**Exemple complet - 3 LEDs indépendantes** :

```forth
\ Définir les tâches
TASK led1-task
TASK led2-task  
TASK led3-task

: led1-loop ( -- )
  BEGIN
    2 PIN-HIGH 500 SLEEP
    2 PIN-LOW 500 SLEEP
  AGAIN ;

: led2-loop ( -- )
  BEGIN
    3 PIN-HIGH 300 SLEEP
    3 PIN-LOW 300 SLEEP
  AGAIN ;

: led3-loop ( -- )
  BEGIN
    4 PIN-HIGH 1000 SLEEP
    4 PIN-LOW 1000 SLEEP
  AGAIN ;

\ Initialiser
: INIT-TASKS
  2 PIN-OUT 3 PIN-OUT 4 PIN-OUT
  ' led1-loop led1-task ACTIVATE
  ' led2-loop led2-task ACTIVATE
  ' led3-loop led3-task ACTIVATE
  led1-task CURRENT-TASK ! ;

\ Scheduler principal
: RUN-TASKS
  INIT-TASKS
  BEGIN
    WAKE-TASKS
    PAUSE
  KEY? UNTIL ;
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

Utiliser les timers matériels pour déclencher des interruptions :

```forth
\ À implémenter avec primitives timer
VARIABLE LED1-STATE
VARIABLE LED2-STATE

: LED1-ISR ( -- )
  \ Handler interruption timer1
  LED1-STATE @ 0= IF
    2 PIN-HIGH 1 LED1-STATE !
  ELSE
    2 PIN-LOW 0 LED1-STATE !
  THEN ;

: INIT-TIMER1 ( us -- )
  \ Configure timer1 pour us microsecondes
  \ Appelle LED1-ISR à chaque expiration
  \ [Code spécifique ESP32 à implémenter]
  ;

: DEMO-TIMER
  500000 INIT-TIMER1  \ 500ms
  BEGIN KEY? UNTIL ;
```

### Comparaison des approches

| Approche | Avantages | Inconvénients |
|----------|-----------|---------------|
| **Coopératif Forth** | Contrôle total, léger | Nécessite PAUSE régulier |
| **Asyncio Python** | Simple, robuste | Dépend de MicroPython |
| **Timer hardware** | Précis, sans surcharge | Limité par nb de timers |

### État/Événements entre tâches

Communication via **variables partagées** :

```forth
VARIABLE SENSOR-VALUE
VARIABLE ALARM-FLAG

: sensor-task ( -- )
  BEGIN
    read-sensor SENSOR-VALUE !
    SENSOR-VALUE @ 100 > IF
      1 ALARM-FLAG !
    THEN
    100 SLEEP
  AGAIN ;

: alarm-task ( -- )
  BEGIN
    ALARM-FLAG @ IF
      led-blink
      0 ALARM-FLAG !
    THEN
    50 SLEEP
  AGAIN ;
```

---

*Guide rédigé pour le projet Forth ESP32-S3 - Version 1.1*