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
        if id_succes in self.achievements and not self.achievements[id_succes].get("debloque", False):
            self.achievements[id_succes]["debloque"] = True
            self.achievements[id_succes]["date"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            self._sauvegarder()
            
            # Alerte visuelle immédiate dans le terminal
            titre = self.achievements[id_succes].get("titre", id_succes)
            icone = self.achievements[id_succes].get("icone", "🏆")
            print(f"\n{VERT}{BOLD}🎉 SUCCÈS DÉBLOQUÉ : {icone} {titre} !{RESET}\n")
            return True
        return False

    def verifier_progression(self, joueur) -> None:
        """Vérifie l'ensemble des conditions dynamiques et débloque les succès correspondants."""
        if not self.achievements.get("mentoring_leo", {}).get("debloque", False):
            affinite_leo = joueur.relations.get("leo", 0)
            a_aide_ad = "leo_aide_restauration_ad" in joueur.flags
            a_soutenu_restic = "leo_soutenu_restic" in joueur.flags

            if affinite_leo > 90 and a_aide_ad and a_soutenu_restic:
                self.deverrouiller("mentoring_leo")

        if not self.achievements.get("didier_ragequit", {}).get("debloque", False):
            if joueur.relations.get("didier", 50) <= 15:
                self.deverrouiller("didier_ragequit")

        if not self.achievements.get("fils_a_papa", {}).get("debloque", False):
            if joueur.relations.get("kevin", 0) >= 80 and joueur.relations.get("patron", 0) >= 80:
                self.deverrouiller("fils_a_papa")
        
        if not self.achievements.get("elu_du_cse", {}).get("debloque", False):
            if joueur.relationnel >= 85 and joueur.promotion >= 70 and joueur.technique < 40:
                self.deverrouiller("elu_du_cse")

        if not self.achievements.get("loopback_master", {}).get("debloque", False):
            # Soit via compteur :
            if getattr(joueur, "tickets_reseau_resolus", 0) >= 3:
                self.deverrouiller("loopback_master")

        if not self.achievements.get("ticket_zero", {}).get("debloque", False):
            if joueur.semaine_actuelle >= 26:
                derniers_vendredis = {23, 24, 25, 26}
                a_quitte_tot = any(s in joueur.semaines_quitte_tot for s in derniers_vendredis)
                if not a_quitte_tot:
                    self.deverrouiller("ticket_zero")

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