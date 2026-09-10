# helpdesk.rpg
Tiny Helpdesk game


## Comment jouer :
1. Créer l'environnement virtuel nommé .venv<br>
python3 -m venv .venv <br>

 2. L'activer (selon ton shell)
Si tu es sur Bash/Zsh :<br>
source .venv/bin/activate<br><br>
Si tu es sur Fish :<br>
source .venv/bin/activate.fish<br><br>

3. Installer la seule dépendance actuelle (PyYAML)<br>
pip install -r requirements.txt


## Descriptions des archetypes :

[1] L'Autodidacte
    A monté son homelab à 14 ans. Préfère parler à un terminal Bash qu'à un être humain.
    Stats : Tech 55 | Rel 25 | Moral 70 | NRJ 10

[2] Le Reconverti
    Ancien gestionnaire administratif. Maîtrise le jargon corporate, les process et la diplomatie.
    Stats : Tech 20 | Rel 65 | Moral 70 | NRJ 10

[3] Le Diplômé
    Sort frais et dispos d'un BTS réseau/cyber. Équilibré, confiant et plein d'énergie.
    Stats : Tech 40 | Rel 45 | Moral 80 | NRJ 15

[4] Le Planqué
    Inamovible grâce à un vieux CDI blindé. En fait le strict minimum syndical.
    Stats : Tech 15 | Rel 40 | Moral 85 | NRJ 7

[5] Le Passionné
    Ne compte pas ses heures quand ça devient complexe. S'ennuie vite sur la routine bureautique.
    Stats : Tech 50 | Rel 30 | Moral 65 | NRJ 10