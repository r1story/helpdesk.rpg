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

    def to_dict(self) -> dict:
            """Convertit l'état du joueur en dictionnaire prêt pour le JSON."""
            return {
                "nom": self.nom,
                "archetype": self.archetype,
                "passif": self.passif,
                "moral": self.moral,
                "technique": self.technique,
                "relationnel": self.relationnel,
                "promotion": self.promotion,
                "energie_max": self.energie_max,
                "energie": self.energie,
                "semaine_actuelle": self.semaine_actuelle,
                "flags": list(self.flags),  # Conversion set -> list pour le JSON
            }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Recrée une instance de Player à partir d'un dictionnaire."""
        flags_set = set(data.get("flags", []))
        return cls(
            nom=data["nom"],
            archetype=data["archetype"],
            passif=data.get("passif"),
            moral=data["moral"],
            technique=data["technique"],
            relationnel=data["relationnel"],
            promotion=data["promotion"],
            energie_max=data["energie_max"],
            energie=data["energie"],
            semaine_actuelle=data["semaine_actuelle"],
            flags=flags_set,
        )

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
    type: str  # "routine", "crise", "special"
    titre: str
    description: str
    choix: List[Choice]
    cooldown: int = 1
    unique: bool = False
    semaine_declenchement: int | None = None
    archetype_requis: str | None = None  # id de l'archétype requis (ex: "autodidacte")
    derniere_semaine_jouee: int = -999

