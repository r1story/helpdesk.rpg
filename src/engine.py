"""src/engine.py : Moteur logique du jeu."""
from pathlib import Path
from typing import List
import yaml
import json

from src.models import Choice, GameEvent, Player

CHEMIN_SAUVEGARDE = Path(__file__).resolve().parent.parent / "savegame.json"

def sauvegarder_partie(joueur: Player) -> None:
    """Écrit l'état actuel du joueur dans savegame.json."""
    with open(CHEMIN_SAUVEGARDE, "w", encoding="utf-8") as f:
        json.dump(joueur.to_dict(), f, indent=2, ensure_ascii=False)


def charger_partie() -> Player | None:
    """Charge une partie existante, ou retourne None si aucun fichier n'existe."""
    if not CHEMIN_SAUVEGARDE.exists():
        return None
    try:
        with open(CHEMIN_SAUVEGARDE, "r", encoding="utf-8") as f:
            donnees = json.load(f)
            return Player.from_dict(donnees)
    except (json.JSONDecodeError, KeyError):
        return None


def supprimer_sauvegarde() -> None:
    """Supprime la sauvegarde en cas de fin de partie ou de reset."""
    if CHEMIN_SAUVEGARDE.exists():
        CHEMIN_SAUVEGARDE.unlink()
class GameEngine:   
    def __init__(self, player: Player):
        self.player = player
        self.events: List[GameEvent] = []
        self.charger_evenements()

    def charger_evenements(self) -> None:
        """Charge et parse tous les fichiers YAML du dossier data/events/."""
        chemin_events = Path(__file__).resolve().parent.parent / "data" / "events"
        
        for fichier_yaml in chemin_events.glob("*.yaml"):
            with open(fichier_yaml, "r", encoding="utf-8") as f:
                donnees = yaml.safe_load(f) or []
                for item in donnees:
                    liste_choix = [
                        Choice(
                            texte=c["texte"],
                            cout_energie=c.get("cout_energie", 0),
                            impacts=c.get("impacts", {}),
                            flags_requis=c.get("flags_requis", []),
                            flags_ajoutes=c.get("flags_ajoutes", []),
                        )
                        for c in item.get("choix", [])
                    ]
                    event = GameEvent(
                        id=item["id"],
                        type=item.get("type", "routine"),
                        titre=item["titre"],
                        description=item["description"],
                        choix=liste_choix,
                        cooldown=item.get("cooldown", 1),
                        unique=item.get("unique", False),
                        semaine_declenchement=item.get("semaine_declenchement"),
                        archetype_requis=item.get("archetype_requis"),
                    )
                    self.events.append(event)
    def obtenir_evenement_scripté_semaine(self) -> GameEvent | None:
    """Retourne la crise ou l'événement de classe prévu pour cette semaine."""
    for ev in self.events:
        if ev.semaine_declenchement == self.player.semaine_actuelle and ev.derniere_semaine_jouee == -999:
            # S'il y a une restriction de classe, on vérifie l'archétype du joueur
            if ev.archetype_requis:
                # Normalisation pour comparer (ex: "autodidacte" dans "l'autodidacte")
                if ev.archetype_requis.lower() not in self.player.archetype.lower():
                    continue
            return ev
    return None

    def appliquer_choix(self, choix: Choice, event: GameEvent) -> None:
            """Déduit l'énergie, applique les impacts et prend en compte les passifs."""
            self.player.consommer_energie(choix.cout_energie)

            for jauge, delta in choix.impacts.items():
                # Passif "Le Passionné" : gain de moral supplémentaire sur les gros chantiers/crises
                if self.player.passif == "boost_crises" and jauge == "moral":
                    if event.type == "crise" or event.cooldown >= 4:
                        delta += 10
                self.player.ajuster_jauge(jauge, delta)

            for flag in choix.flags_ajoutes:
                self.player.flags.add(flag)

    def verifier_fin_de_partie(self) -> str | None:
            """Vérifie l'arrêt de jeu, avec protection passive."""
            if self.player.est_en_burnout():
                return "Dépression : Burn-out face à la montagne de tickets non résolus."

            # Passif "Le Planqué" : impossible à licencier
            if self.player.promotion <= 0:
                if self.player.passif == "immunite_licenciement":
                    self.player.promotion = 1  # Reste sauvé in extremis
                else:
                    return "Licenciement : La direction estime que tu n'as pas le profil pour l'équipe."

            if self.player.semaine_actuelle > 52:
                if self.player.promotion >= 75 and self.player.technique >= 70:
                    return "Promotion RSSI : Tu prends les commandes de la sécurité du SI !"
                if self.player.technique >= 80 and self.player.moral <= 30:
                    return "Retraite à la campagne : Tu as désinstallé Linux pour élever des chèvres dans la Creuse."
                return "Maintien au poste : Une année de plus au support N1 terminée sain et sauf."

            return None


    def obtenir_evenements_disponibles(self) -> List[GameEvent]:
        disponibles = []
        for ev in self.events:
            # Les crises avec semaine fixe ne sont pas tirées au hasard
            if ev.semaine_declenchement is not None:
                continue

            if ev.unique and ev.derniere_semaine_jouee != -999:
                continue

            semaines_ecoulees = self.player.semaine_actuelle - ev.derniere_semaine_jouee
            if ev.derniere_semaine_jouee == -999 or semaines_ecoulees >= ev.cooldown:
                disponibles.append(ev)

        return disponibles

    def enregistrer_passage_evenement(self, event: GameEvent) -> None:
        """Marque la semaine où l'événement a été tiré."""
        event.derniere_semaine_jouee = self.player.semaine_actuelle


def charger_archetypes() -> list[dict]:
    chemin = Path(__file__).resolve().parent.parent / "data" / "archetypes.yaml"
    with open(chemin, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []