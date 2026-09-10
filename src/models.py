"""src/models.py : Modèles de données pour le jeu."""
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class Player:
    nom: str
    archetype: str
    passif: str | None = None  # ex: "immunite_licenciement", "boost_crises"

    # Jauges principales (de 0 à 100)
    moral: int = 70
    technique: int = 30
    relationnel: int = 50
    promotion: int = 20

    # Ressource consommable
    energie_max: int = 10
    energie: int = 10

    # Progression temporelle
    semaine_actuelle: int = 1

    # Flags pour les événements passés et fins secrètes (ex: "sauvegarde_reussie", "hacker_contacted")
    flags: Set[str] = field(default_factory=set)

    def ajuster_jauge(self, nom_jauge: str, delta: int) -> None:
        """Modifie une jauge tout en la bornant strictement entre 0 et 100."""
        if hasattr(self, nom_jauge):
            valeur_actuelle = getattr(self, nom_jauge)
            nouvelle_valeur = max(0, min(100, valeur_actuelle + delta))
            setattr(self, nom_jauge, nouvelle_valeur)
        else:
            raise AttributeError(f"La jauge '{nom_jauge}' n'existe pas chez Player.")

    def consommer_energie(self, cout: int) -> bool:
        """Consomme de l'énergie si possible. Retourne False si pas assez d'énergie."""
        if self.energie >= cout:
            self.energie -= cout
            return True
        return False

    def reinitialiser_energie(self) -> None:
        """Reset de l'énergie en début de semaine."""
        self.energie = self.energie_max

    def est_en_burnout(self) -> bool:
        """Condition de défaite immédiate."""
        return self.moral <= 0


@dataclass
class Choice:
    texte: str
    cout_energie: int
    impacts: Dict[str, int]  # ex: {"moral": -5, "technique": 10}
    flags_requis: List[str] = field(default_factory=list)
    flags_ajoutes: List[str] = field(default_factory=list)


@dataclass
class GameEvent:
    id: str
    type: str  # "routine", "crise", "projet"
    titre: str
    description: str
    choix: List[Choice]
    cooldown: int = 1  # Nombre de semaines de pause après apparition
    unique: bool = False  # Si True, disparaît définitivement après avoir été joué
    derniere_semaine_jouee: int = -999  # Traceur interne