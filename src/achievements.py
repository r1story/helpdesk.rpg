"""src/achievements.py : Gestion persistante des trophées et succès."""
from datetime import datetime
import json
from pathlib import Path
from src.ui import BOLD, DIM, JAUNE, RESET, VERT

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
        """Affiche le Hall des Succès sans révéler les conditions des trophées verrouillés."""
        print(f"\n{BOLD}{'═' * 66}{RESET}")
        print(f"{BOLD}                  🏆 SALLE DES SUCCÈS 🏆{RESET}")
        print(f"{BOLD}{'═' * 66}{RESET}\n")

        total = len(self.achievements)
        debloques = sum(1 for a in self.achievements.values() if a.get("debloque", False))
        print(f"Progression globale : {JAUNE}{debloques}/{total}{RESET} succès déverrouillés\n")

        for id_succes, data in self.achievements.items():
            est_debloque = data.get("debloque", False)
            icone = data.get("icone", "🏆")

            if est_debloque:
                tag = f"{VERT}[DÉBLOQUÉ]{RESET}"
                titre = f"{BOLD}{data['titre']}{RESET}"
                description = f"{DIM}{data['description']}{RESET}"
            else:
                tag = f"{DIM}[VERROUILLÉ]{RESET}"
                titre = f"{DIM}??? {data['titre']}{RESET}"
                description = f"{DIM}??? Objectif masqué — Jouez pour découvrir ce secret.{RESET}"

            print(f" {icone} {tag} {titre}")
            print(f"    {description}\n")

        print(f"{BOLD}{'═' * 66}{RESET}\n")