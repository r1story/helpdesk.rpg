"""src/engine.py : Moteur logique du jeu."""
from pathlib import Path
from typing import List
import yaml

from src.models import Choice, GameEvent, Player


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
                    )
                    self.events.append(event)

    def appliquer_choix(self, choix: Choice) -> None:
        """Déduit l'énergie, applique les variations de jauges et stocke les flags."""
        self.player.consommer_energie(choix.cout_energie)

        for jauge, delta in choix.impacts.items():
            self.player.ajuster_jauge(jauge, delta)

        for flag in choix.flags_ajoutes:
            self.player.flags.add(flag)

    def verifier_fin_de_partie(self) -> str | None:
        """Retourne le nom de la fin si une condition d'arrêt est remplie, sinon None."""
        if self.player.est_en_burnout():
            return "Dépression : Burn-out face à la montagne de tickets non résolus."
        
        if self.player.promotion <= 0:
            return "Licenciement : La direction estime que tu n'as pas le profil pour l'équipe."

        if self.player.semaine_actuelle > 52:
            if self.player.promotion >= 75 and self.player.technique >= 70:
                return "Promotion RSSI : Tu prends les commandes de la sécurité du SI !"
            if self.player.technique >= 80 and self.player.moral <= 30:
                return "Retraite à la campagne : Tu as désinstallé Linux pour élever des chèvres dans la Creuse."
            return "Maintien au poste : Une année de plus au support N1 terminée sain et sauf."

        return None