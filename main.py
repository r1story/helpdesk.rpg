"""main.py : Point d'entrée de Helpdesk RPG."""
import random
import sys
import time

from src.engine import GameEngine
from src.models import Player
from src.ui import afficher_evenement, afficher_tableau_de_bord, demander_choix, effacer_ecran


def main() -> None:
    effacer_ecran()
    print("=== DÉMARRAGE DU POSTE DE TRAVAIL ===")
    nom = input("Entre le prénom de ton technicien : ").strip() or "Nouveau Tech"
    
    joueur = Player(nom=nom, archetype="Stagiaire N1")
    moteur = GameEngine(joueur)

    if not moteur.events:
        print("[ERREUR] Aucun événement chargé depuis data/events/. Vérifie les fichiers YAML.")
        sys.exit(1)

    # Boucle de jeu (semaine par semaine)
    while True:
        fin = moteur.verifier_fin_de_partie()
        if fin:
            effacer_ecran()
            afficher_tableau_de_bord(joueur)
            print("=== FIN DE PARTIE ===")
            print(f"Résultat : {fin}\n")
            break

        joueur.reinitialiser_energie()
        effacer_ecran()
        print(f"--- DÉBUT DE LA SEMAINE {joueur.semaine_actuelle} ---")
        time.sleep(1)

        # Boucle d'actions dans la semaine tant qu'il reste de l'énergie
        while joueur.energie > 0:
            fin = moteur.verifier_fin_de_partie()
            if fin:
                break

            # On tire un événement au hasard dans la liste
            event = random.choice(moteur.events)

            effacer_ecran()
            afficher_tableau_de_bord(joueur)
            afficher_evenement(event)

            idx_choix = demander_choix(len(event.choix))
            choix_selectionne = event.choix[idx_choix]

            # Vérification de l'énergie
            if joueur.energie < choix_selectionne.cout_energie:
                print("\n[!] Énergie insuffisante pour cette option ! Appuie sur Entrée.")
                input()
                continue

            moteur.appliquer_choix(choix_selectionne)
            print("\nAction appliquée avec succès. Mise à jour des métriques...")
            time.sleep(1)

        # Fin de semaine
        joueur.semaine_actuelle += 1


if __name__ == "__main__":
    main()