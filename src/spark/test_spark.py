
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

python_path = sys.executable

os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path

spark = (
    SparkSession.builder
    .appName("GlobalFootballIntelligence")
    .master("local[1]")
    .config("spark.sql.shuffle.partitions", "1")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\n=== PRUEBA APACHE SPARK ===")
    print("Python:", python_path)
    print("Spark:", spark.version)

    # Crear registros directamente en Spark
    df = spark.range(0, 1000)

    df = df.withColumn(
        "valor",
        col("id") * 2
    )

    print("Total de registros:", df.count())
    df.show(5)

    print("\nPRUEBA SPARK COMPLETADA CORRECTAMENTE")

finally:
    spark.stop()
