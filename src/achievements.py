"""src/achievements.py : Gestion persistante des trophées et succès."""
from datetime import datetime
import json
from pathlib import Path

CHEMIN_ACHIEVEMENTS = Path(__file__).resolve().parent.parent / "data" / "achievements.json"


class AchievementManager:
    def __init__(self):
        self.achievements = self._charger()

    def _charger(self) -> dict:
        if not CHEMIN_ACHIEVEMENTS.exists():
            return {}
        try:
            with open(CHEMIN_ACHIEVEMENTS, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _sauvegarder(self) -> None:
        with open(CHEMIN_ACHIEVEMENTS, "w", encoding="utf-8") as f:
            json.dump(self.achievements, f, indent=2, ensure_ascii=False)

    def deverrouiller(self, id_succes: str) -> bool:
        """Débloque un succès s'il existe et n'était pas encore validé.
        Retourne True si le succès vient tout juste d'être acquis."""
        if id_succes in self.achievements and not self.achievements[id_succes]["debloque"]:
            self.achievements[id_succes]["debloque"] = True
            self.achievements[id_succes]["date"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            self._sauvegarder()
            return True
        return False

    def afficher_galerie(self) -> None:
        """Affiche l'ensemble des trophées débloqués et verrouillés."""
        print("\n" + "=" * 64)
        print("                 🏆 SALLE DES SUCCÈS 🏆")
        print("=" * 64)
        total = len(self.achievements)
        debloques = sum(1 for a in self.achievements.values() if a["debloque"])
        print(f" Progression globale : {debloques}/{total}\n")

        for a in self.achievements.values():
            if a["debloque"]:
                statut = "\033[92m[DÉBLOQUÉ]\033[0m"
                print(f" {statut} \033[1m{a['titre']}\033[0m (le {a['date']})")
                print(f"    {a['description']}")
            else:
                statut = "\033[2m[VERROUILLÉ]\033[0m"
                print(f" {statut} \033[2m{a['titre']}\033[0m")
                print(f"    \033[2m{a['description']}\033[0m")
            print("-" * 64)
        print()