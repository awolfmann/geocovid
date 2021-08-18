"""Utils module."""
from pyspark.sql import SparkSession
from sedona.utils import SedonaKryoRegistrator, KryoSerializer
from sedona.register import SedonaRegistrator


def start_spark(
    app_name: str = 'Sedona App',
    master: str ='local[*]'
) -> SparkSession:
    """
    Start Spark session.

    Parameters
    ----------
    app_name: Name of Spark app.
    master: Cluster connection details (defaults to local[*]).

    Returns
    -------
    spark session instance
    """
    spark = SparkSession.\
        builder.\
        master(master).\
        appName(app_name).\
        config("spark.serializer", KryoSerializer.getName).\
        config("spark.kryo.registrator", SedonaKryoRegistrator.getName) .\
        config("spark.jars.packages", """org.apache.sedona:sedona-python-adapter-3.0_2.12:1.0.1-incubating,org.datasyslab:geotools-wrapper:geotools-24.0""") .\
        getOrCreate()

    SedonaRegistrator.registerAll(spark)

    return spark
