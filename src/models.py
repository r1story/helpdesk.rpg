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
    tags: List[str] = field(default_factory=list)
    pnj: str | None = None
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

    # Jauges principales (0 à 100)
    moral: int = 70
    technique: int = 30
    relationnel: int = 50
    promotion: int = 20

    # Dictionnaire id_pnj -> affinité (0 à 100)
    relations: Dict[str, int] = field(default_factory=dict)

    # Énergie hebdomadaire
    energie_max: int = 10
    energie: int = 10

    # Dans Player (src/models.py) :
    tickets_reseau_resolus: int = 0
    semaines_quitte_tot: Set[int] = field(default_factory=set)

    # Progression temporelle & flags
    semaine_actuelle: int = 1
    flags: Set[str] = field(default_factory=set)

    # Bonus temporaires
    bonus_energie_suivante: int = 0
    bonus_technique_suivant: int = 0

    # Historique du tour précédent pour le tableau comparatif
    stats_precedentes: Dict[str, int] = field(default_factory=dict)

    def ajuster_relation(self, pnj: str, delta: int) -> None:
        """Modifie l'affinité avec un PNJ/groupe et répercute la mécanique Kévin -> Patron."""
        if pnj not in self.relations:
            # Sécurité au cas où le PNJ n'était pas initialisé dans le dict
            self.relations[pnj] = 50

        # Application du delta borné entre 0 et 100
        self.relations[pnj] = max(0, min(100, self.relations[pnj] + delta))

        # Règle spéciale : froisser Kévin pénalise directement le Patron
        if pnj == "kevin" and delta < 0:
            malus_patron = int(delta * 1.5)
            if "patron" in self.relations:
                self.relations["patron"] = max(0, min(100, self.relations["patron"] + malus_patron))

        # Recalcul systématique de la moyenne globale
        if self.relations:
            self.relationnel = sum(self.relations.values()) // len(self.relations)

    def ajuster_jauge(self, jauge: str, delta: int) -> None:
        """Point d'entrée unique appelé par engine.py pour appliquer les impacts."""
        # 1. Si la clé correspond à un PNJ ou au groupe équipe
        if jauge in self.relations:
            self.ajuster_relation(jauge, delta)
            return

        # 2. Redirection des anciens tickets 'relationnel' vers l'équipe
        if jauge == "relationnel":
            self.ajuster_relation("equipe", delta)
            return

        # 3. Jauges standard (moral, technique, promotion)
        if hasattr(self, jauge):
            val = getattr(self, jauge)
            setattr(self, jauge, max(0, min(100, val + delta)))

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
        energie_base = self.energie_max
        if self.passif == "endurance_etudiant" or "mentor_apprenti" in self.flags:
            energie_base += 1

        total = energie_base + self.bonus_energie_suivante
        self.energie = max(0, total)
        self.bonus_energie_suivante = 0

        if self.bonus_technique_suivant > 0:
            self.ajuster_jauge("technique", self.bonus_technique_suivant)
            self.bonus_technique_suivant = 0

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
            "relations": self.relations,
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
            relations=data.get("relations", {}),
            energie_max=data["energie_max"],
            energie=data["energie"],
            semaine_actuelle=data["semaine_actuelle"],
            flags=set(data.get("flags", [])),
            bonus_energie_suivante=data.get("bonus_energie_suivante", 0),
            bonus_technique_suivant=data.get("bonus_technique_suivant", 0),
            stats_precedentes=data.get("stats_precedentes", {}),
        )