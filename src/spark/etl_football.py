
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, sum as spark_sum, round as spark_round
)
import time
import os

spark = (
    SparkSession.builder
    .appName("GFI-ETL-Football")
    .master("spark://spark-master:7077")
    .config("spark.executor.memory", "512m")
    .config("spark.executor.cores", "1")
    .config("spark.cores.max", "2")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

inicio = time.perf_counter()

try:
    print("=== GLOBAL FOOTBALL INTELLIGENCE - ETL ===")

    # 1. Extracción
    df = spark.read.csv(
        "/opt/spark-data/raw/football_data.csv",
        header=True,
        inferSchema=True
    )

    print("Registros originales:", df.count())

    # 2. Transformación y limpieza
    df_limpio = df.dropDuplicates(["registro_id"]).dropna(
        subset=["liga", "equipo", "rival", "resultado"]
    )

    print("Registros limpios:", df_limpio.count())

    # 3. Análisis estadístico
    estadisticas = (
        df_limpio.groupBy("liga", "equipo")
        .agg(
            count("*").alias("partidos"),
            spark_sum("goles_favor").alias("goles_totales"),
            spark_round(avg("posesion"), 2).alias("posesion_promedio"),
            spark_sum("puntos").alias("puntos_totales")
        )
    )

    estadisticas.show(20, truncate=False)

    # 4. Carga a Parquet
    estadisticas.write.mode("overwrite").parquet(
        "/opt/spark-data/processed/estadisticas_equipos"
    )

    print("Datos guardados en Parquet correctamente")

    # 5. Carga a PostgreSQL
    print("Conectando con PostgreSQL...")

    password = os.environ["GFI_DB_PASSWORD"]

    (
        estadisticas.write
        .format("jdbc")
        .option(
            "url",
            "jdbc:postgresql://host.docker.internal:5432/global_football_db"
        )
        .option("dbtable", "public.estadisticas_equipos_staging")
        .option("user", "postgres")
        .option("password", password)
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")
        .option("truncate", "true")
        .save()
    )

    print("Datos cargados en PostgreSQL correctamente")

    
    # 6. UPSERT automático hacia la tabla principal
    print("Iniciando UPSERT automático...")

    jvm = spark._jvm

    jdbc_url = (
        "jdbc:postgresql://host.docker.internal:"
        "5432/global_football_db"
    )

    connection = None

    try:
        jvm.java.lang.Class.forName("org.postgresql.Driver")

        connection = jvm.java.sql.DriverManager.getConnection(
            jdbc_url, "postgres", password
        )

        connection.setAutoCommit(False)

        statement = connection.createStatement()

        try:
            statement.executeUpdate("""
                INSERT INTO public.estadisticas_equipos (
                    liga, equipo, partidos, goles_totales,
                    posesion_promedio, puntos_totales
                )
                SELECT
                    liga, equipo, partidos, goles_totales,
                    posesion_promedio, puntos_totales
                FROM public.estadisticas_equipos_staging
                ON CONFLICT (liga, equipo)
                DO UPDATE SET
                    partidos = EXCLUDED.partidos,
                    goles_totales = EXCLUDED.goles_totales,
                    posesion_promedio = EXCLUDED.posesion_promedio,
                    puntos_totales = EXCLUDED.puntos_totales
            """)

            connection.commit()
            print("UPSERT completado correctamente")

        except Exception:
            connection.rollback()
            raise

        finally:
            statement.close()

    finally:
        if connection is not None:
            connection.close()


    duracion = time.perf_counter() - inicio

    print("ETL COMPLETADO")
    print(f"Tiempo de procesamiento: {duracion:.2f} segundos")

finally:
    spark.stop()
