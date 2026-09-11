"""main.py : Point d'entrée de Helpdesk RPG."""
import random
import sys
import time

from src.engine import GameEngine, charger_archetypes
from src.models import Player
from src.ui import afficher_evenement, afficher_tableau_de_bord, demander_choix, effacer_ecran
from src.ui import (
    afficher_bilan_action,
    afficher_evenement,
    afficher_tableau_de_bord,
    demander_choix,
    effacer_ecran,
)

from src.engine import (
    GameEngine,
    charger_archetypes,
    charger_partie,
    sauvegarder_partie,
    supprimer_sauvegarde,
)

from src.achievements import AchievementManager
from src.ui import afficher_pop_up_succes

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
    
    # 1. Vérification d'une sauvegarde existante
    partie_sauvegardee = charger_partie()
    joueur = None

    if partie_sauvegardee:
        print("=== SESSION ANTÉRIEURE DÉTECTÉE ===")
        print(f"Technicien : {partie_sauvegardee.nom} ({partie_sauvegardee.archetype})")
        print(f"Progression : Semaine {partie_sauvegardee.semaine_actuelle}/52\n")
        print("  [1] Reprendre le poste")
        print("  [2] Réinitialiser et écraser la session\n")
        choix_save = demander_choix(2)
        if choix_save == 0:  # Option 1
            joueur = partie_sauvegardee

    # 2. Si pas de sauvegarde ou reset choisi
    if not joueur:
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

    # 3. Boucle principale
    while True:
        fin = moteur.verifier_fin_de_partie()
        if fin:
            effacer_ecran()
            afficher_tableau_de_bord(joueur)
            print("=== FIN DE PARTIE ===")
            print(f"Résultat : {fin}\n")

            # Gestion des succès selon la fin
            ach_manager = AchievementManager()
            id_succes = None

            if "Burn-out" in fin:
                id_succes = "fin_burnout"
            elif "Licenciement" in fin:
                id_succes = "fin_licenciement"
            elif "RSSI" in fin:
                id_succes = "fin_rssi"
            elif "chèvres" in fin:
                id_succes = "fin_campagne"
            elif "Maintien au poste" in fin:
                id_succes = "fin_survie"

            if id_succes and ach_manager.deverrouiller(id_succes):
                succes = ach_manager.achievements[id_succes]
                afficher_pop_up_succes(succes["titre"], succes["description"])

            supprimer_sauvegarde()
            input("Appuie sur Entrée pour quitter...")
            break

        # Sauvegarde automatique au début de chaque nouvelle semaine
        sauvegarder_partie(joueur)

        joueur.reinitialiser_energie()
        effacer_ecran()
        print(f"--- DÉBUT DE LA SEMAINE {joueur.semaine_actuelle} ---")
        time.sleep(1)

        
        # Détection d'une crise scriptée pour cette semaine
        evenement_scripté = moteur.obtenir_evenement_scripté_semaine()

        while joueur.energie > 0:
            fin = moteur.verifier_fin_de_partie()
            if fin:
                break

            # Si une crise est en attente, elle passe obligatoirement en premier
            if crise_active:
                event = crise_active
                crise_active = None  # Consommée pour la semaine
            else:
                events_dispo = moteur.obtenir_evenements_disponibles()
                if not events_dispo:
                    events_dispo = [e for e in moteur.events if e.semaine_declenchement is None]
                event = random.choice(events_dispo)


                while True:
                effacer_ecran()
                afficher_tableau_de_bord(joueur)
                afficher_evenement(event)

                idx_choix = demander_choix(len(event.choix), peut_quitter=True, username=joueur.nom)

                # Sortie de secours : le joueur quitte le bureau pour la semaine
                if idx_choix == -1:
                    print("\nTu fermes ta session et quittes le bureau pour le week-end...")
                    joueur.energie = 0  # Force la fin de la semaine
                    time.sleep(1)
                    break

                choix_selectionne = event.choix[idx_choix]

                # Vérification de l'énergie
                if joueur.energie < choix_selectionne.cout_energie:
                    print(f"\n[!] Énergie insuffisante ! Il te reste {joueur.energie}⚡, cette action en demande {choix_selectionne.cout_energie}⚡.")
                    print("Appuie sur Entrée pour rechoisir une option réalisable...")
                    input()
                    continue

                # Si l'énergie est suffisante, on applique et on avance
                moteur.appliquer_choix(choix_selectionne, event)
                moteur.enregistrer_passage_evenement(event)
                afficher_bilan_action(choix_selectionne)
                print("Appuie sur Entrée pour continuer...")
                input()
                break

        # Fin de semaine
        joueur.semaine_actuelle += 1

if __name__ == "__main__":
    main()