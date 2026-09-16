"""src/ui.py : Interface terminal calibrée à 72 colonnes."""
import os
import re
import textwrap

from src.models import Choice, GameEvent, Player
from src.engine import charger_pnj


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
    valeur_clamped = max(0, min(max_val, valeur))
    rempli = int((valeur_clamped / max_val) * longueur)
    vide = longueur - rempli
    return f"{couleur}[{'█' * rempli}{'░' * vide}]{RESET} {valeur_clamped:3d}/{max_val:<3d}"


# Regex pour supprimer les codes ANSI et mesurer la largeur visible réelle
ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def longueur_visible(texte: str) -> int:
    """Retourne la longueur réelle du texte sans les séquences d'échappement ANSI."""
    return len(ANSI_ESCAPE.sub("", texte))


def formater_diff_stat(cle: str, nom_court: str, joueur: Player, largeur_colonne: int = 33) -> str:
    """Génère un bloc comparatif calibré exactement à largeur_colonne caractères visibles."""
    av = joueur.stats_precedentes.get(cle, getattr(joueur, cle))
    ap = getattr(joueur, cle)
    diff = ap - av
    c = COULEURS_JAUGES.get(cle, BLANC)

    # Le tag de variation est cadré sur 5 caractères visibles : "(+10)", "( -5)", "( = )"
    if diff > 0:
        s_diff = f"{VERT}(+{diff:<2d}){RESET}"
    elif diff < 0:
        s_diff = f"{ROUGE}({diff:<3d}){RESET}"
    else:
        s_diff = f"{DIM}( = ){RESET}"

    # Découpage : nom (9) + ": " (2) + avant (3) + " -> " (4) + après (3) + " " (1) + diff (5) = 27 caractères visibles
    partie_gauche = f"{c}{nom_court:<9}{RESET}: {av:3d} -> {ap:3d} {s_diff}"
    
    # Remplissage dynamique pour combler jusqu'à largeur_colonne
    manque = max(0, largeur_colonne - longueur_visible(partie_gauche))
    return partie_gauche + (" " * manque)


def afficher_tableau_de_bord(joueur: Player) -> None:
    w = 72
    largeur_interieure = w - 2  # 70 caractères

    print(f"{DIM}┌{'─' * largeur_interieure}┐{RESET}")

    # Ligne 1 : Titre + Semaine + Nom
    gauche = " Tech N1-N2 — Période d'essai"
    milieu = f"Semaine : {joueur.semaine_actuelle:02d}/26"
    droite = f"Tech : {joueur.nom.upper()}"

    texte_visible_l1 = f"{gauche}  |  {milieu}  |  {droite}"
    pad_l1 = max(0, largeur_interieure - len(texte_visible_l1))
    print(
        f"{DIM}│{RESET}{BOLD}{BLANC}{gauche}{RESET}  {DIM}|{RESET}  "
        f"Semaine : {JAUNE}{joueur.semaine_actuelle:02d}/26{RESET}  {DIM}|{RESET}  "
        f"Tech : {CYAN}{joueur.nom.upper()}{RESET}{' ' * pad_l1}{DIM}│{RESET}"
    )
    print(f"{DIM}├{'─' * largeur_interieure}┤{RESET}")

    # Lignes 2 & 3 : Comparatif dynamique tour précédent
    if joueur.stats_precedentes:
        titre_recent = "  MÉTRIQUES RÉCENTES (DERNIER TICKET) :"
        pad_titre = max(0, largeur_interieure - len(titre_recent))
        print(f"{DIM}│{RESET}{BOLD}{titre_recent}{RESET}{' ' * pad_titre}{DIM}│{RESET}")

        # 2 colonnes de 33 caractères + 2 espaces initiaux + 2 espaces finaux = 70 caractères
        col_w = 33

        # Ligne A : Moral & Technique
        c_mor = formater_diff_stat("moral", "Moral", joueur, largeur_colonne=col_w)
        c_tec = formater_diff_stat("technique", "Tech", joueur, largeur_colonne=col_w)
        ligne_a = f"  {c_mor}  {c_tec}"
        pad_a = max(0, largeur_interieure - longueur_visible(ligne_a))
        print(f"{DIM}│{RESET}{ligne_a}{' ' * pad_a}{DIM}│{RESET}")

        # Ligne B : Relationnel & Promotion
        c_rel = formater_diff_stat("relationnel", "Relation", joueur, largeur_colonne=col_w)
        c_pro = formater_diff_stat("promotion", "Promotion", joueur, largeur_colonne=col_w)
        ligne_b = f"  {c_rel}  {c_pro}"
        pad_b = max(0, largeur_interieure - longueur_visible(ligne_b))
        print(f"{DIM}│{RESET}{ligne_b}{' ' * pad_b}{DIM}│{RESET}")

        print(f"{DIM}├{'─' * largeur_interieure}┤{RESET}")

    # Ligne Énergie
    b_nrg = barre_simple(joueur.energie, joueur.energie_max, 10, COULEURS_JAUGES["energie"])
    ligne_nrg = f"  Énergie   : {b_nrg}"
    pad_nrg = max(0, largeur_interieure - longueur_visible(ligne_nrg))
    print(f"{DIM}│{RESET}{ligne_nrg}{' ' * pad_nrg}{DIM}│{RESET}")

    # Jauges principales (Grille 2 colonnes)
    b_mor = barre_simple(joueur.moral, 100, 10, COULEURS_JAUGES["moral"])
    b_tec = barre_simple(joueur.technique, 100, 10, COULEURS_JAUGES["technique"])
    b_rel = barre_simple(joueur.relationnel, 100, 10, COULEURS_JAUGES["relationnel"])
    b_pro = barre_simple(joueur.promotion, 100, 10, COULEURS_JAUGES["promotion"])

    ligne_j1 = f"  Moral     : {b_mor}    Tech      : {b_tec}"
    pad_j1 = max(0, largeur_interieure - longueur_visible(ligne_j1))
    print(f"{DIM}│{RESET}{ligne_j1}{' ' * pad_j1}{DIM}│{RESET}")

    ligne_j2 = f"  Relation  : {b_rel}    Promotion : {b_pro}"
    pad_j2 = max(0, largeur_interieure - longueur_visible(ligne_j2))
    print(f"{DIM}│{RESET}{ligne_j2}{' ' * pad_j2}{DIM}│{RESET}")

    print(f"{DIM}└{'─' * largeur_interieure}┘{RESET}\n")


def afficher_evenement(
    event: GameEvent,
    peut_automatiser: bool = False,
    catalogue_pnj: list[dict] | None = None,
) -> None:
    """Affiche le ticket ou la crise en masquant les tags techniques."""
    type_tag = f"{ROUGE}[CRISE]{RESET}" if event.type == "crise" else f"{CYAN}[TICKET]{RESET}"

    # Récupération automatique du catalogue si non fourni
    if catalogue_pnj is None:
        catalogue_pnj = charger_pnj()

    # Identification du demandeur
    demandeur = "Utilisateur anonyme"
    if event.pnj and catalogue_pnj:
        pnj_match = next((p for p in catalogue_pnj if p.get("id") == event.pnj), None)
        if pnj_match:
            demandeur = f"{pnj_match['nom']} ({pnj_match['role']})"

    # Affichage de l'en-tête sans les tags
    print(f"▶ {type_tag} {BOLD}#{event.id.upper()}{RESET} — {event.titre}")
    print(f"  {DIM}Demandeur : {demandeur}{RESET}")
    print(f"{DIM}{'─' * 72}{RESET}")
    print(f"  {event.description}\n")

    print(f"{BOLD}Options disponibles :{RESET}")
    for idx, c in enumerate(event.choix, start=1):
        cout = f"{JAUNE}-{c.cout_energie}⚡{RESET}" if c.cout_energie > 0 else f"{DIM}gratuit{RESET}"
        print(f"  {BOLD}[{idx}]{RESET} {c.texte} ({cout})")

    if peut_automatiser and event.type != "crise":
        print(f"  {VERT}{BOLD}[A] Déployer un script Bash/PowerShell automatisé (-1⚡, expert Tech){RESET}")

    print(f"  {DIM}[6] Annuaire des collègues & Relations PNJ{RESET}")
    print(f"  {DIM}[9] Consulter la Salle des Succès{RESET}")
    print(f"  {DIM}[0] Quitter le bureau pour cette semaine{RESET}\n")

def barre_relation(valeur: int, longueur: int = 8) -> str:
    rempli = int((max(0, min(100, valeur)) / 100) * longueur)
    vide = longueur - rempli
    if valeur >= 70:
        c = VERT
    elif valeur >= 40:
        c = JAUNE
    else:
        c = ROUGE
    return f"{c}[{'█' * rempli}{'░' * vide}]{RESET} {valeur:3d}/100"


def afficher_annuaire_pnj(joueur: Player, catalogue_pnj: list[dict]) -> None:
    """Affiche la liste détaillée des PNJ basée sur le YAML avec retour à la ligne automatique."""
    w = 72
    largeur_interieure = w - 2  # 70 caractères utiles

    print(f"\n{CYAN}{BOLD}┌{'─' * largeur_interieure}┐{RESET}")
    
    # Titre avec un préfixe textuel propre pour éviter le décalage de largeur des émojis
    titre = "  👥 ANNUAIRE : RELATIONS ET COLLÈGUES DU BUREAU"
    pad_titre = max(0, largeur_interieure - longueur_visible(titre) - 1)    
    print(f"{CYAN}{BOLD}│{RESET}{BOLD}{titre}{' ' * pad_titre}{CYAN}{BOLD}│{RESET}")
    print(f"{CYAN}{BOLD}├{'─' * largeur_interieure}┤{RESET}")

    for pnj in catalogue_pnj:
        p_id = pnj["id"]
        nom_complet = f"{pnj['nom']} ({pnj['role']})"
        affinite = joueur.relations.get(p_id, pnj.get("affinite_initiale", 50))
        desc = pnj.get("description", "")
        barre = barre_relation(affinite)

        # Ligne 1 : Nom + Jauge d'affinité
        ligne_nom = f"  {BOLD}{nom_complet}{RESET}"
        bloc_affinite = f"Affinité : {barre}"
        espaces_milieu = max(2, largeur_interieure - longueur_visible(ligne_nom) - longueur_visible(bloc_affinite) - 2)
        ligne_haut = f"{ligne_nom}{' ' * espaces_milieu}{bloc_affinite}  "
        pad_haut = max(0, largeur_interieure - longueur_visible(ligne_haut))
        print(f"{CYAN}{BOLD}│{RESET}{ligne_haut}{' ' * pad_haut}{CYAN}{BOLD}│{RESET}")

        # Ligne(s) de description enveloppée(s)
        lignes_desc = textwrap.wrap(desc, width=largeur_interieure - 6)
        for sub_ligne in lignes_desc:
            texte_desc = f"    {DIM}{sub_ligne}{RESET}"
            pad_desc = max(0, largeur_interieure - longueur_visible(texte_desc))
            print(f"{CYAN}{BOLD}│{RESET}{texte_desc}{' ' * pad_desc}{CYAN}{BOLD}│{RESET}")

        # Ligne vide séparatrice entre collègues
        print(f"{CYAN}{BOLD}│{RESET}{' ' * largeur_interieure}{CYAN}{BOLD}│{RESET}")

    print(f"{CYAN}{BOLD}└{'─' * largeur_interieure}┘{RESET}\n")

def demander_choix(
    nb_options: int,
    peut_quitter: bool = False,
    username: str = "sysadmin",
    autoriser_auto: bool = False,
) -> int | str:
    """Retourne l'index du choix (0 à n-1), -1 pour quitter, 'A' pour auto, '6' pour l'annuaire, ou '9' pour les succès."""
    borne_min = 0 if peut_quitter else 1
    user_clean = username.lower().replace(" ", "-")

    extra_auto = "/A" if autoriser_auto else ""
    prompt = f"{BOLD}{VERT}{user_clean}@support:~$ {RESET}Action ({borne_min}-{nb_options}{extra_auto} | 6:Annuaire | 9:Succès) > "

    while True:
        saisie = input(prompt).strip()

        # 1. Commandes spéciales prioritaires
        if autoriser_auto and saisie.upper() == "A":
            return "A"
        if saisie in ("6", "9"):
            return saisie

        # 2. Choix numériques de tickets ou sortie
        if saisie.isdigit():
            valeur = int(saisie)
            if valeur == 0 and peut_quitter:
                return -1
            if 1 <= valeur <= nb_options:
                return valeur - 1

        msg = f"{borne_min} à {nb_options}"
        if autoriser_auto:
            msg += ", A"
        print(f"{ROUGE}Entrée invalide. Choisis {msg} (ou 6:Annuaire, 9:Succès).{RESET}")

def afficher_appel_astreinte() -> None:
    print(f"\n{ROUGE}{BOLD}┌{'─' * 60}┐{RESET}")
    print(f"{ROUGE}{BOLD}│ 🚨 ALERTE ASTREINTE : SAMEDI 03:14 DU MATIN !               │{RESET}")
    print(f"{ROUGE}{BOLD}├{'─' * 60}┤{RESET}")
    print(f"{ROUGE}{BOLD}│ {BLANC}Le smartphone pro vibre violemment sur ta table de chevet.{ROUGE}{BOLD} │{RESET}")
    print(f"{ROUGE}{BOLD}│ {DIM}Une sonde Zabbix signale que le serveur ERP ne ping plus.  {RESET}{ROUGE}{BOLD} │{RESET}")
    print(f"{ROUGE}{BOLD}└{'─' * 60}┘{RESET}\n")
    print(f"  {BOLD}[1]{RESET} Décrocher, allumer le PC portable et investiguer en SSH")
    print(f"  {BOLD}[2]{RESET} Activer le mode avion, se retourner dans son lit et se rendormir\n")

def afficher_pop_up_succes(titre: str, description: str) -> None:
    """Affiche une bannière dorée lors d'un déverrouillage."""
    print(f"\n{JAUNE}{BOLD}┌{'─' * 60}┐{RESET}")
    print(f"{JAUNE}{BOLD}│ 🏆 SUCCÈS DÉVERROUILLÉ !                                   │{RESET}")
    print(f"{JAUNE}{BOLD}├{'─' * 60}┤{RESET}")
    print(f"{JAUNE}{BOLD}│ {BLANC}{titre:<58}{JAUNE}{BOLD} │{RESET}")
    print(f"{JAUNE}{BOLD}│ {DIM}{description:<58}{RESET}{JAUNE}{BOLD} │{RESET}")
    print(f"{JAUNE}{BOLD}└{'─' * 60}┘{RESET}\n")

def afficher_succes_automatisation() -> None:
    """Affiche le retour visuel lors de l'exécution d'un script d'automatisation."""
    print(f"\n{VERT}{BOLD}▶ Script exécuté avec succès en 0.42s !{RESET}")
    print("Ticket résolu sans lever le petit doigt. La direction apprécie l'efficacité.")

def afficher_intro_narrative(joueur: Player) -> None:
    """Introduction immersive façon briefing de bienvenue."""
    effacer_ecran()
    print(f"{CYAN}{BOLD}╔{'═' * 70}╗{RESET}")
    print(f"{CYAN}{BOLD}║  🏢 LUNDI MATIN — 08H45 : PREMIER JOUR CHEZ TECHCORP SOLUTIONS      ║{RESET}")
    print(f"{CYAN}{BOLD}╚{'═' * 70}╝{RESET}\n")

    print(f"Marc, le Responsable Support N2/N3, t'accueille avec un mug ébréché à la main.\n")
    print(f"« Ah, salut {joueur.nom} ! Installe-toi au bureau 14, à côté de l'onduleur qui siffle.")
    print(f"Bienvenue dans l'équipe. Ta mission pour les 26 prochaines semaines :")
    print(f"survivre à la période d'essai sans faire flamber le serveur de prod. »\n")

    # Discours personnalisé selon le profil
    arch = joueur.archetype.lower()
    if "autodidacte" in arch:
        print(f"{JAUNE}« On m'a dit que tu montais des clusters Linux dans ta cave la nuit.")
        print(f"C'est cool, mais ici c'est Windows 11 et Office 365. Range tes scripts Bash,")
        print(f"branche ton casque et commence par vider la file d'attente. »{RESET}\n")
    elif "reconverti" in arch:
        print(f"{JAUNE}« Ravi d'avoir quelqu'un qui sait parler aux humains et aligner deux phrases.")
        print(f"La technique, ça s'apprend sur le tas ; par contre, calmer un comptable furieux")
        print(f"dont le tableau Excel a planté, ça c'est ton rayon. »{RESET}\n")
    elif "diplômé" in arch or "diplome" in arch:
        print(f"{JAUNE}« Bac+3 tout frais sorti d'école ? Oublie la théorie propre des cours.")
        print(f"Ici, le mot de passe du compte Admin racine est collé sous le clavier du DSI")
        print(f"sur un Post-it jaune. On fait avec les moyens du bord. »{RESET}\n")
    elif "planqué" in arch or "planque" in arch:
        print(f"{JAUNE}« Tu as l'air détendu... presque trop détendu. Sache que le DSI a l'œil partout,")
        print(f"mais si tu sais te rendre invisible au bon moment, tu devrais tenir l'année. »{RESET}\n")
    elif "passionné" in arch or "passionne" in arch:
        print(f"{JAUNE}« Ton enthousiasme fait plaisir à voir, mais calme tes ardeurs :")
        print(f"n'essaie pas de refaire l'architecture réseau le premier vendredi après-midi. »{RESET}\n")

    print(f"{DIM}Les règles d'or :{RESET}")
    print(f"  • {JAUNE}Énergie{RESET}     : Ton carburant hebdo. Si tu tombes à 0⚡, ta semaine s'arrête.")
    print(f"  • {CYAN}Moral{RESET}       : Garde-le au-dessus de 0, sous peine de burn-out direct.")
    print(f"  • {BLEU}Promotion{RESET}   : Si elle chute à 0, c'est la porte avant la fin des 6 mois.")
    print(f"  • {VERT}Technique{RESET}   : À 80+, tu débloqueras la commande magique [A] pour scripter.\n")

    input(f"{BOLD}Appuie sur Entrée pour enfiler ton badge et ouvrir la boîte mail...{RESET}")


def afficher_epilogue(code_fin: str, joueur: Player) -> None:
    """Affiche une fin scénarisée détaillée."""
    effacer_ecran()
    print(f"\n{BOLD}{'═' * 70}{RESET}")

    if code_fin == "burnout":
        print(f"{ROUGE}{BOLD}             🥀 ÉPILOGUE : LE BURN-OUT DU N1{RESET}")
        print(f"{BOLD}{'═' * 70}{RESET}\n")
        print("Mardi, 10h14. La notification d'un énième ticket 'Mon écran est tout noir'")
        print("provoque un court-circuit dans ton esprit. Tu te lèves en silence, tu laisses")
        print("ton badge sur le clavier et tu sors du bâtiment sans même prendre ta veste.\n")
        print("Ton médecin traitant te met en arrêt immédiat. Le bruit d'un ventilateur de PC")
        print("te donne désormais des sueurs froides.")

    elif code_fin == "licenciement":
        print(f"{ROUGE}{BOLD}             📦 ÉPILOGUE : FIN DE PÉRIODE D'ESSAI ANTICIPÉE{RESET}")
        print(f"{BOLD}{'═' * 70}{RESET}\n")
        print("Vendredi, 16h45. Convoqué dans le bureau vitré des RH.")
        print("« Nous apprécions votre sympathie, mais le management estime que votre profil")
        print("ne correspond pas au dynamisme de l'équipe... »\n")
        print("Tu rends ton PC portable et repars avec un carton sous le bras contenant")
        print("ton mug et trois câbles RJ45 que tu avais récupérés au local technique.")

    elif code_fin == "rssi":
        print(f"{VERT}{BOLD}             🛡️ ÉPILOGUE : L'ASCENSION FULGURANTE (RSSI){RESET}")
        print(f"{BOLD}{'═' * 70}{RESET}\n")
        print("Après avoir géré les crises de main de maître, le DSI t'appelle en direct :")
        print("« On ne va pas te laisser au support N1. Tu as prouvé que tu avais le niveau. »\n")
        print("Six mois après ton arrivée, tu hérites d'un bureau individuel, du budget cyber")
        print("et de la casquette officielle de Responsable de la Sécurité des Systèmes d'Information.")

    elif code_fin == "campagne":
        print(f"{CYAN}{BOLD}             🐐 ÉPILOGUE : RETRAITE EN CREUSE{RESET}")
        print(f"{BOLD}{'═' * 70}{RESET}\n")
        print("Trop de compétences, trop d'absurdités managériales. Tu as compris les rouages")
        print("du système et tu as fait le seul choix rationnel possible : débrancher la prise.\n")
        print("Tu as vendu ton setup, acheté une ferme en pierre dans la Creuse et adopté")
        print("un troupeau de chèvres alpines. Ton seul réseau aujourd'hui est une clôture électrifiée.")

    elif code_fin == "cdi":
        print(f"{VERT}{BOLD}             📝 ÉPILOGUE : PÉRIODE D'ESSAI VALIDÉE (CDI){RESET}")
        print(f"{BOLD}{'═' * 70}{RESET}\n")
        print("L'entretien des 6 mois s'achève sur une poignée de main chaleureuse.")
        print("Ton responsable signe l'avenant : tu es officiellement titularisé en CDI !\n")
        print("Tu as survécu aux imprimantes capricieuses, aux serveurs poussiéreux et aux VIP.")
        print("Tu fais désormais partie des meubles chez TechCorp Solutions.")

    else:
        print(f"{JAUNE}{BOLD}             ⚖️ ÉPILOGUE : SURVEILLANCE RAPPROCHÉE{RESET}")
        print(f"{BOLD}{'═' * 70}{RESET}\n")
        print("La direction hésite encore. Ta période d'essai est renouvelée pour 3 mois.")
        print("Tu gardes ton poste, mais tu marches sur des œufs.")

    print(f"\n{BOLD}{'═' * 70}{RESET}\n")
