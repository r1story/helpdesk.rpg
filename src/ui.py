"""src/ui.py : Interface terminal enrichie et alignée."""
import os
from src.models import Choice, GameEvent, Player

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

ROUGE = "\033[91m"
VERT = "\033[92m"
JAUNE = "\033[93m"
BLEU = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BLANC = "\033[97m"

COULEURS_JAUGES = {
    "energie": JAUNE,
    "moral": CYAN,
    "technique": VERT,
    "relationnel": MAGENTA,
    "promotion": BLEU,
}


def effacer_ecran() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def barre_simple(valeur: int, max_val: int = 100, longueur: int = 10, couleur: str = BLANC) -> str:
    """Génère la jauge brute colorée avec un padding texte strict."""
    valeur_clamped = max(0, min(max_val, valeur))
    rempli = int((valeur_clamped / max_val) * longueur)
    vide = longueur - rempli
    return f"{couleur}[{'█' * rempli}{'░' * vide}]{RESET} {valeur_clamped:3d}/{max_val:<3d}"


def afficher_tableau_de_bord(joueur: Player) -> None:
    """Tableau de bord avec calcul d'alignement au caractère près."""
    w = 72
    print(f"{DIM}┌{'─' * (w - 2)}┐{RESET}")
    
    # En-tête brut pour calcul exact de l'espace restant
    titre_gauche = " Informations : "
    centre = f"Semaine : {joueur.semaine_actuelle:02d}/52"
    droite = f"Tech : {joueur.nom.upper()} ({joueur.archetype})"
    
    # Ligne 1 avec couleurs injectées
    ligne1_texte = f"{titre_gauche}  |  {centre}  |  {droite}"
    espaces_fin = (w - 2) - len(ligne1_texte)
    if espaces_fin < 0:
        # Si le nom est trop long, on tronque
        droite = droite[:droite.find("(")-1]
        ligne1_texte = f"{titre_gauche}  |  {centre}  |  {droite}"
        espaces_fin = max(0, (w - 2) - len(ligne1_texte))

    print(f"{DIM}│{RESET}{BOLD}{BLANC}{titre_gauche}{RESET}  {DIM}|{RESET}  Semaine : {JAUNE}{joueur.semaine_actuelle:02d}/52{RESET}  {DIM}|{RESET}  Tech : {CYAN}{joueur.nom.upper()}{RESET} ({joueur.archetype}){' ' * espaces_fin}{DIM}│{RESET}")
    print(f"{DIM}├{'─' * (w - 2)}┤{RESET}")

    # Barres calibrées
    # Format fixe : " [████░░░░░░]  50/100" = 20 caractères d'affichage réel
    b_nrg = barre_simple(joueur.energie, joueur.energie_max, 10, COULEURS_JAUGES["energie"])
    b_mor = barre_simple(joueur.moral, 100, 10, COULEURS_JAUGES["moral"])
    b_tec = barre_simple(joueur.technique, 100, 10, COULEURS_JAUGES["technique"])
    b_rel = barre_simple(joueur.relationnel, 100, 10, COULEURS_JAUGES["relationnel"])
    b_pro = barre_simple(joueur.promotion, 100, 10, COULEURS_JAUGES["promotion"])

    # Ligne Énergie (pleine largeur)
    # "  Énergie   : " = 14 chars + 20 chars jauge = 34 chars. Reste : 70 - 34 = 36 espaces.
    pad_nrg = " " * ((w - 2) - 34)
    print(f"{DIM}│{RESET}  Énergie   : {b_nrg}{pad_nrg}{DIM}│{RESET}")

    # Lignes à 2 colonnes (35 chars par colonne = 70 chars total)
    # Col 1: "  Moral        : " (17) + 20 = 37 -> on ajuste les labels à 13 chars
    # "  Moral     : " (14) + 20 = 34 chars
    # "  Tech      : " (14) + 20 = 34 chars -> total 68 chars + 2 espaces = 70
    pad_col = "  "
    print(f"{DIM}│{RESET}  Moral     : {b_mor}{pad_col}Tech      : {b_tec}  {DIM}│{RESET}")
    print(f"{DIM}│{RESET}  Relation  : {b_rel}{pad_col}Promotion : {b_pro}  {DIM}│{RESET}")

    print(f"{DIM}└{'─' * (w - 2)}┘{RESET}\n")


def afficher_evenement(event: GameEvent) -> None:
    """Fiche ticket cadrée proprement."""
    type_tag = f"{ROUGE}[CRISE]{RESET}" if event.type == "crise" else f"{CYAN}[TICKET]{RESET}"
    print(f"▶ {type_tag} {BOLD}#{event.id.upper()}{RESET} — {event.titre}")
    print(f"{DIM}{'─' * 72}{RESET}")
    print(f"  {event.description}\n")

    print(f"{BOLD}Options disponibles :{RESET}")
    for idx, c in enumerate(event.choix, start=1):
        cout = f"{JAUNE}-{c.cout_energie}⚡{RESET}" if c.cout_energie > 0 else f"{DIM}gratuit{RESET}"
        print(f"  {BOLD}[{idx}]{RESET} {c.texte} ({cout})")
    print(f"  {DIM}[0] Quitter le bureau pour cette semaine{RESET}\n")


def afficher_bilan_action(choix: Choice) -> None:
    """Récapitulatif immédiat après validation."""
    print(f"\n{BOLD}═══ RÉSULTAT DU TICKET ═══{RESET}")
    if choix.cout_energie > 0:
        print(f"  Énergie consommée : {JAUNE}-{choix.cout_energie}⚡{RESET}")

    if choix.impacts:
        changements = []
        for jauge, delta in choix.impacts.items():
            c = COULEURS_JAUGES.get(jauge, BLANC)
            signe = f"{VERT}+{delta}" if delta > 0 else f"{ROUGE}{delta}"
            changements.append(f"{c}{jauge.capitalize()}{RESET} {signe}{RESET}")
        print("  Impacts : " + " | ".join(changements))

    if choix.flags_ajoutes:
        print(f"  {DIM}Flags débloqués : {', '.join(choix.flags_ajoutes)}{RESET}")
    print(f"{BOLD}══════════════════════════{RESET}\n")


def demander_choix(nb_options: int, peut_quitter: bool = False, username: str = "sysadmin") -> int:
    """Boucle de saisie avec prompt bash dynamique au nom du joueur."""
    borne_min = 0 if peut_quitter else 1
    # Nettoyage pour un rendu type login Linux (minuscules, sans espaces)
    user_clean = username.lower().replace(" ", "-")
    prompt_invite = f"{BOLD}{VERT}{user_clean}@support:~$ {RESET}Action ({borne_min}-{nb_options}) > "

    while True:
        saisie = input(prompt_invite).strip()
        if saisie.isdigit():
            valeur = int(saisie)
            if valeur == 0 and peut_quitter:
                return -1
            if 1 <= valeur <= nb_options:
                return valeur - 1
        msg = f"0 et {nb_options}" if peut_quitter else f"1 et {nb_options}"
        print(f"{ROUGE}Entrée invalide. Choisis entre {msg}.{RESET}")


def afficher_pop_up_succes(titre: str, description: str) -> None:
    """Affiche une bannière dorée lors d'un déverrouillage."""
    print(f"\n{JAUNE}{BOLD}┌{'─' * 60}┐{RESET}")
    print(f"{JAUNE}{BOLD}│ 🏆 SUCCÈS DÉVERROUILLÉ !                                   │{RESET}")
    print(f"{JAUNE}{BOLD}├{'─' * 60}┤{RESET}")
    print(f"{JAUNE}{BOLD}│ {BLANC}{titre:<58}{JAUNE}{BOLD} │{RESET}")
    print(f"{JAUNE}{BOLD}│ {DIM}{description:<58}{RESET}{JAUNE}{BOLD} │{RESET}")
    print(f"{JAUNE}{BOLD}└{'─' * 60}┘{RESET}\n")