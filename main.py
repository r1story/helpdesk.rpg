"""main.py : Point d'entrée de Helpdesk RPG."""
import random
import sys
import time

from src.engine import GameEngine, charger_archetypes
from src.models import Player
from src.ui import afficher_evenement, afficher_tableau_de_bord, demander_choix, effacer_ecran


def selectionner_archetype() -> dict:
    archetypes = charger_archetypes()
    
    if not archetypes:
        raise ValueError("Aucun archétype trouvé dans data/archetypes.yaml !")

    effacer_ecran()
    print("=== CHOIX DU PROFIL DU TECHNICIEN ===\n")
    for idx, arch in enumerate(archetypes, start=1):
        print(f"[{idx}] {arch['nom']}")
        print(f"    {arch['description']}\n")

    choix_idx = demander_choix(len(archetypes))
    return archetypes[choix_idx]


def main() -> None:
    effacer_ecran()
    print("=== DÉMARRAGE DU POSTE DE TRAVAIL ===")
    nom = input("Entre le prénom de ton technicien : ").strip() or "Nouveau Tech"

    profil = selectionner_archetype()
    stats = profil["stats"]

    joueur = Player(
        nom=nom,
        archetype=profil["nom"],
        passif=profil.get("passif"),
        technique=stats["technique"],
        relationnel=stats["relationnel"],
        moral=stats["moral"],
        promotion=stats["promotion"],
        energie_max=stats["energie_max"],
        energie=stats["energie_max"],
    )

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
        # Boucle d'actions dans la semaine tant qu'il reste de l'énergie
        while joueur.energie > 0:
            fin = moteur.verifier_fin_de_partie()
            if fin:
                break

            events_dispo = moteur.obtenir_evenements_disponibles()
            if not events_dispo:
                events_dispo = moteur.events

            event = random.choice(events_dispo)

            # Boucle sur LE MÊME événement tant qu'un choix valide n'est pas fait
            while True:
                effacer_ecran()
                afficher_tableau_de_bord(joueur)
                afficher_evenement(event)

                idx_choix = demander_choix(len(event.choix))
                choix_selectionne = event.choix[idx_choix]

                # Vérification de l'énergie
                if joueur.energie < choix_selectionne.cout_energie:
                    print(f"\n[!] Énergie insuffisante ! Il te reste {joueur.energie}⚡, cette action en demande {choix_selectionne.cout_energie}⚡.")
                    print("Appuie sur Entrée pour rechoisir une option réalisable...")
                    input()
                    continue  # Repose la question sur le MÊME événement

                # Si l'énergie est suffisante, on applique et on sort de la boucle de l'événement
                moteur.appliquer_choix(choix_selectionne, event)
                moteur.enregistrer_passage_evenement(event)
                print("\nAction appliquée avec succès. Mise à jour des métriques...")
                time.sleep(1)
                break

if __name__ == "__main__":
    main()