"""src/ui.py : Fonctions d'affichage et de saisie en console."""
import os
from src.models import Choice, GameEvent, Player


def effacer_ecran() -> None:
    """Nettoie le terminal pour garder une vue claire type console."""
    os.system("cls" if os.name == "nt" else "clear")


def barre(valeur: int, max_val: int = 100, longueur: int = 15) -> str:
    """Génère une barre de progression en caractères ASCII."""
    rempli = int((valeur / max_val) * longueur)
    return f"[{'#' * rempli}{'.' * (longueur - rempli)}] {valeur:3d}/{max_val}"


def afficher_tableau_de_bord(joueur: Player) -> None:
    """Affiche le statut global et les jauges du technicien."""
    print("=" * 60)
    print(f" TECH: {joueur.nom.upper()} | RÔLE: {joueur.archetype.upper()} | SEMAINE: {joueur.semaine_actuelle}/52")
    print("-" * 60)
    print(f" Énergie ⚡   : {barre(joueur.energie, joueur.energie_max, 10)}")
    print(f" Moral        : {barre(joueur.moral)}")
    print(f" Technique    : {barre(joueur.technique)}")
    print(f" Relationnel  : {barre(joueur.relationnel)}")
    print(f" Promotion    : {barre(joueur.promotion)}")
    print("=" * 60)
    print()


def afficher_evenement(event: GameEvent) -> None:
    """Affiche la fiche d'incident / ticket."""
    print(f"[{event.type.upper()}] >>> {event.titre}")
    print("-" * 60)
    print(event.description)
    print("\nChoix possibles :")
    for idx, c in enumerate(event.choix, start=1):
        print(f"  [{idx}] {c.texte} (Coût : {c.cout_energie}⚡)")
    print()


def demander_choix(nb_options: int) -> int:
    """Boucle de saisie sécurisée pour éviter les crashs si l'utilisateur tape n'importe quoi."""
    while True:
        saisie = input(f"Action (1-{nb_options}) > ").strip()
        if saisie.isdigit():
            valeur = int(saisie)
            if 1 <= valeur <= nb_options:
                return valeur - 1
        print(f"Entrée invalide. Choisis un nombre entre 1 et {nb_options}.")