"""main.py : Point d'entrée de Helpdesk RPG."""
import random
import sys
import time

from src.achievements import (
    AchievementManager,
)
from src.engine import (
    GameEngine,
    charger_archetypes,
    charger_partie,
    sauvegarder_partie,
    supprimer_sauvegarde,
)
from src.models import Player
from src.ui import (
    afficher_appel_astreinte,
    afficher_epilogue,
    afficher_evenement,
    afficher_intro_narrative,
    afficher_pop_up_succes,
    afficher_succes_automatisation,
    afficher_tableau_de_bord,
    demander_choix,
    effacer_ecran,
)


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
        # Introduction narrative personnalisée
        afficher_intro_narrative(joueur)

    moteur = GameEngine(joueur)

    # 3. Boucle principale
    while True:
        fin = moteur.verifier_fin_de_partie()
        if fin:
            effacer_ecran()
            afficher_tableau_de_bord(joueur)

            ach_manager = AchievementManager()
            id_succes = None
            code_epilogue = "renouvellement"

            if "Burn-out" in fin:
                id_succes = "fin_burnout"
                code_epilogue = "burnout"
            elif "fin à ton contrat" in fin:
                id_succes = "fin_licenciement"
                code_epilogue = "licenciement"
            elif "RSSI" in fin:
                id_succes = "fin_rssi"
                code_epilogue = "rssi"
            elif "chèvres" in fin:
                id_succes = "fin_campagne"
                code_epilogue = "campagne"
            elif "CDI Confirmé" in fin:
                id_succes = "fin_survie"
                code_epilogue = "cdi"

            # Affiche l'histoire de fin
            afficher_epilogue(code_epilogue, joueur)

            # Déblocage du trophée
            if id_succes and ach_manager.deverrouiller(id_succes):
                succes = ach_manager.achievements[id_succes]
                afficher_pop_up_succes(succes["titre"], succes["description"])

            supprimer_sauvegarde()
            input("Appuie sur Entrée pour clore la partie...")
            break

        # Sauvegarde automatique au début de chaque nouvelle semaine
        sauvegarder_partie(joueur)

        joueur.reinitialiser_energie()
        effacer_ecran()
        print(f"--- DÉBUT DE LA SEMAINE {joueur.semaine_actuelle} ---")
        time.sleep(1)

        # Détection d'une crise ou événement scripté pour cette semaine
        evenement_scripté = moteur.obtenir_evenement_scripté_semaine()

        # DÉBUT DE LA SEMAINE
        while joueur.energie > 0:
            fin = moteur.verifier_fin_de_partie()
            if fin:
                break

            # Tirage de l'événement
            if evenement_scripté:
                event = evenement_scripté
                evenement_scripté = None
            else:
                events_dispo = moteur.obtenir_evenements_disponibles()
                if not events_dispo:
                    events_dispo = [e for e in moteur.events if e.semaine_declenchement is None]
                event = random.choice(events_dispo)

            ticket_resolu = False
            while not ticket_resolu:
                effacer_ecran()
                afficher_tableau_de_bord(joueur)

                peut_automatiser = (joueur.technique >= 80 and event.type != "crise")
                afficher_evenement(event, peut_automatiser=peut_automatiser)

                choix_brut = demander_choix(
                    len(event.choix),
                    peut_quitter=True,
                    username=joueur.nom,
                    autoriser_auto=peut_automatiser,
                )

                match choix_brut:
                    case -1:
                        # Le joueur décide volontairement de quitter le bureau
                        print("\nTu fermes ta session et quittes le bureau pour le week-end...")
                        joueur.energie = 0
                        time.sleep(0.8)
                        ticket_resolu = True
                        break

                    case "9":
                        effacer_ecran()
                        AchievementManager().afficher_galerie()
                        input("Appuie sur Entrée pour revenir au bureau...")
                        continue

                    case "A":
                        if joueur.energie < 1:
                            print("\n[!] Pas assez d'énergie (1⚡ requis) !")
                            time.sleep(1.2)
                            continue

                        joueur.enregistrer_snapshot()
                        joueur.consommer_energie(1)
                        joueur.ajuster_jauge("promotion", 5)
                        joueur.ajuster_jauge("technique", 2)
                        moteur.enregistrer_passage_evenement(event)

                        afficher_succes_automatisation()
                        time.sleep(1.2)
                        ticket_resolu = True
                        break

                    case int(idx):
                        choix_selectionne = event.choix[idx]

                        if joueur.energie < choix_selectionne.cout_energie:
                            print(
                                f"\n[!] Énergie insuffisante "
                                f"({joueur.energie}⚡ dispo, {choix_selectionne.cout_energie}⚡ requis)."
                            )
                            time.sleep(1.2)
                            continue

                        joueur.enregistrer_snapshot()
                        moteur.appliquer_choix(choix_selectionne, event)

                        # Événements spéciaux de skip
                        if event.id == "mission_deplacement_multisites":
                            duree = 1
                            if "deplacement_2_semaines" in choix_selectionne.flags_ajoutes:
                                duree = 2
                            elif "deplacement_3_semaines" in choix_selectionne.flags_ajoutes:
                                duree = 3
                            elif "deplacement_4_semaines" in choix_selectionne.flags_ajoutes:
                                duree = 4
                            joueur.semaine_actuelle += (duree - 1)
                            # On vide l'énergie pour terminer la semaine de mission
                            joueur.energie = 0

                        if "vacances_ete_prises" in choix_selectionne.flags_ajoutes:
                            joueur.semaine_actuelle += 1
                            joueur.bonus_energie_suivante += 3
                            joueur.bonus_technique_suivant += 3
                            joueur.energie = 0

                        if "vacances_hiver_prises" in choix_selectionne.flags_ajoutes:
                            joueur.bonus_energie_suivante += 3
                            joueur.bonus_technique_suivant += 3
                            joueur.energie = 0

                        if event.id == "mission_formation_pro":
                            joueur.semaine_actuelle += 1
                            joueur.energie = 0

                        moteur.enregistrer_passage_evenement(event)
                        time.sleep(1)
                        
                        ticket_resolu = True
                        break  # Sort de la boucle du ticket, mais RESTE dans while joueur.energie > 0 !

        # Aléa d'astreinte le week-end (20% de probabilité)
        if random.random() < 0.20 and joueur.semaine_actuelle < 52:
            effacer_ecran()
            afficher_appel_astreinte()
            choix_astreinte = demander_choix(2, username=joueur.nom)

            if choix_astreinte == 0:  # Option 1 : Décrocher
                print("\nTu passes 2 heures les yeux embrumés à relancer le service.")
                print("Le lundi matin, le management salue ton dévouement sans faille.")
                joueur.ajuster_jauge("moral", -10)
                joueur.ajuster_jauge("promotion", 15)
                joueur.ajuster_jauge("technique", 5)
                joueur.bonus_energie_suivante -= 2
            else:  # Option 2 : Ignorer
                print("\nTu coupes le téléphone. Après tout, l'astreinte n'était pas déclarée.")
                print("Lundi 8h30, le patron t'attend avec un café froid et les yeux noirs.")
                joueur.ajuster_jauge("moral", 15)
                joueur.ajuster_jauge("promotion", -15)
                joueur.ajuster_jauge("relationnel", -5)

            time.sleep(2)
            input("\nAppuie sur Entrée pour clore le week-end...")

        # Fin de semaine
        joueur.semaine_actuelle += 1


if __name__ == "__main__":
    main()