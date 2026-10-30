
import csv
import random
import time
from pathlib import Path
from datetime import date, timedelta

# Configuración
TOTAL_REGISTROS = 1_000_000
LOTE = 10_000
random.seed(42)

LIGAS = {
    "Liga MX": ["Rayados", "Tigres", "America", "Chivas", "Pumas", "Cruz Azul"],
    "Premier League": ["Arsenal", "Liverpool", "Chelsea", "Manchester City"],
    "LaLiga": ["Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla"],
    "Bundesliga": ["Bayern Munich", "Dortmund", "Leverkusen", "Leipzig"],
    "Serie A": ["Inter", "Milan", "Juventus", "Napoli"],
    "Ligue 1": ["PSG", "Marseille", "Lyon", "Monaco"],
    "Primera Argentina": ["River Plate", "Boca Juniors", "Racing", "Independiente"]
}

COLUMNAS = [
    "registro_id", "liga", "temporada", "fecha",
    "equipo", "rival", "local", "goles_favor",
    "goles_contra", "tiros", "posesion",
    "pases", "resultado", "puntos"
]

def generar_datos():
    inicio = time.perf_counter()

    ruta = Path(__file__).resolve().parents[2] / "data" / "raw"
    ruta.mkdir(parents=True, exist_ok=True)
    archivo = ruta / "football_data.csv"

    with archivo.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNAS)

        for i in range(1, TOTAL_REGISTROS + 1):
            liga = random.choice(list(LIGAS.keys()))
            equipo, rival = random.sample(LIGAS[liga], 2)

            goles_favor = random.randint(0, 5)
            goles_contra = random.randint(0, 5)

            if goles_favor > goles_contra:
                resultado, puntos = "Victoria", 3
            elif goles_favor < goles_contra:
                resultado, puntos = "Derrota", 0
            else:
                resultado, puntos = "Empate", 1

            fecha = date(2023, 1, 1) + timedelta(
                days=random.randint(0, 1095)
            )

            writer.writerow([
                i,
                liga,
                f"{fecha.year}-{fecha.year + 1}",
                fecha.isoformat(),
                equipo,
                rival,
                random.randint(0, 1),
                goles_favor,
                goles_contra,
                random.randint(goles_favor, 25),
                random.randint(25, 75),
                random.randint(200, 800),
                resultado,
                puntos
            ])

            if i % LOTE == 0:
                print(f"Registros generados: {i:,}")

    duracion = time.perf_counter() - inicio

    print("\nGENERACION COMPLETADA")
    print(f"Total de registros: {TOTAL_REGISTROS:,}")
    print(f"Tiempo: {duracion:.2f} segundos")
    print(f"Archivo: {archivo}")

if __name__ == "__main__":
    generar_datos()
