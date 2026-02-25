import json
from datetime import datetime

LOG_PATH = "log/log.txt"

def parse_time(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

def compute_metrics():
    with open(LOG_PATH, "r") as f:
        logs = [json.loads(line) for line in f if line.strip()]

    if not logs:
        print("Aucun log trouvé.")
        return

    # Trouver le moment de l'injection de la panne (appel /kill)
    t_panne = None
    t_first_500 = None
    t_first_200_spare = None

    for entry in logs:
        ts = parse_time(entry["timestamp"])
        route = entry.get("route", "")
        code = entry.get("code", 0)
        sent_to = entry.get("sent_to", "")

        # Moment de l'injection
        if route == "kill" and t_panne is None:
            t_panne = ts
            print(f"Injection de la panne : {ts.strftime('%H:%M:%S')}")

        # Première réponse 500 après la panne
        if t_panne and t_first_500 is None and code == 500:
            t_first_500 = ts
            print(f"Première réponse 500   : {ts.strftime('%H:%M:%S')}")

        # Première réponse 200 venant du spare
        if t_panne and t_first_200_spare is None and code == 200 and sent_to == "SPARE":
            t_first_200_spare = ts
            print(f"Première réponse 200 (spare) : {ts.strftime('%H:%M:%S')}")

    if not t_panne:
        print("Aucune panne détectée dans les logs. Faites d'abord un CRASH LE SERVICE.")
        return

    print("\n--- MÉTRIQUES ---")

    # T_bascule
    if t_first_200_spare:
        t_bascule = (t_first_200_spare - t_panne).total_seconds()
        print(f"T_bascule = {t_first_200_spare.strftime('%H:%M:%S')} - {t_panne.strftime('%H:%M:%S')} = {t_bascule:.1f} secondes")
    else:
        print("T_bascule : pas encore de réponse 200 du spare dans les logs.")

    # E_bascule — fenêtre de 10s avant et après la panne
    if t_panne and t_first_200_spare:
        fenetre_debut = t_panne.timestamp() - 10
        fenetre_fin = t_first_200_spare.timestamp() + 5

        total = 0
        echoues = 0
        for entry in logs:
            ts = parse_time(entry["timestamp"]).timestamp()
            code = entry.get("code", 0)
            route = entry.get("route", "")
            if route in ["kill", "revive", "activateSpare"]:
                continue
            if fenetre_debut <= ts <= fenetre_fin:
                total += 1
                if code != 200:
                    echoues += 1

        if total > 0:
            e_bascule = (echoues / total) * 100
            print(f"E_bascule = {echoues} / {total} = {e_bascule:.1f}%")
            print(f"  (fenêtre : {int(fenetre_debut % 86400)}s à {int(fenetre_fin % 86400)}s autour de la panne)")
        else:
            print("E_bascule : pas assez de requêtes dans la fenêtre.")

if __name__ == "__main__":
    compute_metrics()
