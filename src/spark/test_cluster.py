
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum
import time

spark = (
    SparkSession.builder
    .appName("GFI-Prueba-Distribuida")
    .master("spark://spark-master:7077")
    .config("spark.executor.instances", "2")
    .config("spark.executor.cores", "1")
    .config("spark.executor.memory", "512m")
    .config("spark.cores.max", "2")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    inicio = time.perf_counter()

    # Generar un millon de registros
    df = spark.range(0, 1000000, 1, 4)

    # Simular valores de rendimiento
    df = df.withColumn(
        "valor",
        col("id") * 2
    )

    total = df.count()
    suma = df.agg(spark_sum("valor")).first()[0]

    duracion = time.perf_counter() - inicio

    print("\n=== GLOBAL FOOTBALL INTELLIGENCE ===")
    print("Registros procesados:", total)
    print("Suma de valores:", suma)
    print("Tiempo de procesamiento:", round(duracion, 2), "segundos")
    print("Particiones:", df.rdd.getNumPartitions())

finally:
    spark.stop()
