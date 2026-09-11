# Helpdesk RPG 🖥️⚡

Un RPG textuel satirique et réaliste dans le terminal, inspiré de l'univers du support informatique et des livres dont vous êtes le héros.

Incarnez un technicien informatique fraîchement recruté et tentez de survivre à une année complète (**52 semaines**) au sein d'une entreprise. Entre les pannes de switchs non sauvegardés, les caprices de la direction, les bourrages papier et les audits de sécurité inopinés, chaque choix impacte directement vos jauges : **Moral**, **Compétences Techniques**, **Relationnel**, **Promotion** et votre réserve hebdomadaire d'**Énergie**.

Saurez-vous gravir les échelons jusqu'au poste de RSSI, ou finirez-vous par tout plaquer pour élever des chèvres dans la Creuse ?

---

## 🚀 Installation & Lancement

Le jeu est compatible **Linux**, **macOS** et **Windows** (PowerShell ou Windows Terminal recommandé). Il nécessite **Python 3.10+**.

### Sur Linux / macOS

1. **Cloner le dépôt et entrer dans le dossier :**
```bash
git clone [https://github.com/votre-compte/helpdesk-rpg.git](https://github.com/votre-compte/helpdesk-rpg.git)
cd helpdesk-rpg

```


2. **Créer l'environnement virtuel et installer les dépendances :**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```


3. **Lancer le jeu :**
```bash
chmod +x run.sh
./run.sh
# Ou directement : python3 main.py

```



---

### Sur Windows

1. **Ouvrir PowerShell ou le Terminal Windows** dans le dossier du projet.
2. **Créer et activer l'environnement virtuel :**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

```


*(Si une restriction de script PowerShell apparaît, exécutez d'abord : `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*
3. **Installer les dépendances et lancer :**
```powershell
pip install -r requirements.txt
python main.py

```



---

## 👤 Les Profils de Départ

Au début de votre aventure, vous devez choisir votre parcours professionnel. Chaque profil dispose d'une répartition initiale de statistiques unique et d'avantages passifs cachés influençant le déroulement de la partie :

* **L'Autodidacte** : Forgé à coups de homelabs nocturnes et de lignes de commande. Plus à l'aise face à un terminal de serveurs qu'en réunion de cadrage.
* **Le Reconverti** : Venu du monde administratif et de la gestion. Maîtrise le vocabulaire corporate, la diplomatie interne et l'art de contourner les frictions.
* **Le Diplômé** : Fraîchement issu d'un cursus spécialisé en réseaux et cybersécurité. Plein d'énergie, équilibré et rigoureux face aux standards théoriques.
* **Le Planqué** : Un profil mystérieux qui semble avoir trouvé la faille dans les rouages du management. Maîtrise le service minimum et l'art de l'esquive.
* **Le Passionné** : Ne compte pas ses heures dès qu'un problème devient stimulant ou complexe, mais s'étiole face à la routine abrutissante du support N1.

---

## 💾 Sauvegarde Automatique

* **Persistance de session** : Une sauvegarde locale (`savegame.json`) est automatiquement générée et mise à jour **à chaque passage de semaine**.
* **Reprise fluide** : Vous pouvez fermer votre terminal ou quitter le bureau en cours d'année (action `[0]`) ; à la relance du jeu, votre progression, vos statistiques et vos choix passés seront automatiquement détectés.
* En cas de fin de partie (victoire ou défaite prématurée), la session en cours est réinitialisée pour vous permettre de retenter l'aventure.

---

## 🏆 Succès & Trophées

Le jeu intègre un système persistant de récompenses indépendant des réinitialisations de parties :

* **7 succès uniques** sont à déverrouiller au total.
* Ils récompensent la découverte des différentes conclusions de carrière (officielles ou officieuses), ainsi que des choix spécifiques liés à certains profils ou crises critiques.
* La progression globale est conservée d'une tentative à l'autre dans le registre local du jeu.

---

## 🛠️ Architecture du Projet

* `data/events/` : Fichiers YAML contenant les tickets quotidiens, les crises majeures et les événements de profils.
* `data/archetypes.yaml` : Définition des statistiques de départ et passifs.
* `src/` : Moteur de jeu (`engine.py`), modèles de données (`models.py`), interface terminal ANSI (`ui.py`) et gestionnaire de succès (`achievements.py`).
* `main.py` : Point d'entrée de l'application.

---

Le développement logiciel est 100% généré par IA.