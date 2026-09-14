"""src/models.py : Modèles de données pour Helpdesk RPG."""
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class Choice:
    texte: str
    cout_energie: int = 0
    impacts: Dict[str, int] = field(default_factory=dict)
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
    archetype_requis: str | None = None
    derniere_semaine_jouee: int = -999


@dataclass
class Player:
    nom: str
    archetype: str
    passif: str | None = None

    moral: int = 70
    technique: int = 30
    relationnel: int = 50
    promotion: int = 20

    energie_max: int = 10
    energie: int = 10

    semaine_actuelle: int = 1
    flags: Set[str] = field(default_factory=set)

    bonus_energie_suivante: int = 0
    bonus_technique_suivant: int = 0

    # Historique du tour précédent pour le tableau comparatif
    stats_precedentes: Dict[str, int] = field(default_factory=dict)

    def enregistrer_snapshot(self) -> None:
        """Capture les valeurs actuelles avant qu'un choix ne soit appliqué."""
        self.stats_precedentes = {
            "moral": self.moral,
            "technique": self.technique,
            "relationnel": self.relationnel,
            "promotion": self.promotion,
            "energie": self.energie,
        }

    def consommer_energie(self, montant: int) -> None:
        self.energie = max(0, self.energie - montant)

    def reinitialiser_energie(self) -> None:
        nouvelle_energie = self.energie_max + self.bonus_energie_suivante
        self.energie = max(0, nouvelle_energie)
        self.bonus_energie_suivante = 0

        if self.bonus_technique_suivant > 0:
            self.ajuster_jauge("technique", self.bonus_technique_suivant)
            self.bonus_technique_suivant = 0

    def ajuster_jauge(self, jauge: str, delta: int) -> None:
        if hasattr(self, jauge):
            valeur_actuelle = getattr(self, jauge)
            setattr(self, jauge, max(0, min(100, valeur_actuelle + delta)))

    def est_en_burnout(self) -> bool:
        return self.moral <= 0

    def to_dict(self) -> dict:
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
            "flags": list(self.flags),
            "bonus_energie_suivante": self.bonus_energie_suivante,
            "bonus_technique_suivant": self.bonus_technique_suivant,
            "stats_precedentes": self.stats_precedentes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
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
            flags=set(data.get("flags", [])),
            bonus_energie_suivante=data.get("bonus_energie_suivante", 0),
            bonus_technique_suivant=data.get("bonus_technique_suivant", 0),
            stats_precedentes=data.get("stats_precedentes", {}),
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Reconstitue une instance Player depuis un dictionnaire JSON."""
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
            bonus_energie_suivante=data.get("bonus_energie_suivante", 0),
            bonus_technique_suivant=data.get("bonus_technique_suivant", 0),
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

