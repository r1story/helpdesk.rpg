"""src/engine.py : Moteur logique du jeu."""
import json
from pathlib import Path
from typing import List
import yaml

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


def charger_archetypes() -> list[dict]:
    """Charge la configuration des archétypes depuis le YAML."""
    chemin = Path(__file__).resolve().parent.parent / "data" / "archetypes.yaml"
    with open(chemin, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


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
                        tags=item.get("tags", []),
                        pnj=item.get("pnj"),
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
                if ev.archetype_requis:
                    if ev.archetype_requis.lower() not in self.player.archetype.lower():
                        continue
                return ev
        return None

    def appliquer_choix(self, choix: Choice, event: GameEvent) -> None:
            """Applique le coût en énergie, les impacts sur les jauges/PNJ et les flags."""
            # Débit de l'énergie
            self.player.consommer_energie(choix.cout_energie)

            # Application de TOUS les impacts définis dans le YAML
            for stat, delta in choix.impacts.items():
                self.player.ajuster_jauge(stat, delta)

            # Ajout des flags débloqués
            for fl in choix.flags_ajoutes:
                self.player.flags.add(fl)

    def verifier_fin_de_partie(self) -> str | None:
            """Vérifie l'arrêt de jeu, avec protection passive."""
            if self.player.est_en_burnout():
                return "Rupture de période d'essai : Burn-out face à la montagne de tickets."

            if self.player.promotion <= 0:
                if self.player.passif == "immunite_licenciement":
                    self.player.promotion = 1
                else:
                    return "Période d'essai non renouvelée : Le management met fin à ton contrat."

            # Terminus : semaine 26 (fin des 6 mois)
            if self.player.semaine_actuelle > 26:
                if self.player.promotion >= 70 and self.player.technique >= 75:
                    return "Promotion RSSI : Période d'essai pulvérisée ! Tu es propulsé à la tête de la cyber."
                if self.player.technique >= 80 and self.player.moral <= 30:
                    return "Retraite à la campagne : Tu as désinstallé Linux pour élever des chèvres dans la Creuse."
                if self.player.promotion >= 40:
                    return "CDI Confirmé : Période d'essai validée avec succès, tu intègres officiellement l'équipe !"
                return "Période d'essai renouvelée de justesse : Tu restes sur la sellette pour 3 mois de plus."

            return None

    def obtenir_evenements_disponibles(self) -> List[GameEvent]:
        disponibles = []
        for ev in self.events:
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

def charger_pnj() -> list[dict]:
    """Charge la configuration des PNJ depuis le fichier data/pnj.yaml."""
    chemin = Path(__file__).resolve().parent.parent / "data" / "pnj.yaml"
    if not chemin.exists():
        return []
    with open(chemin, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []