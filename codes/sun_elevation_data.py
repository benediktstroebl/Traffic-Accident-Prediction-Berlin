#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pysolar.solar import *
from dateutil import tz
import datetime
import pandas as pd
import math

from tqdm import tqdm
tqdm.pandas()


# In[2]:


tzone = tz.gettz('Europe/Berlin')


# In[3]:


# EXAMPLE:
latitude = 52.55075
longitude = 13.414106

date = datetime.datetime(2018, 1, 1, 2, 0, 0, tzinfo=tzone)
sun_altitude = get_altitude(latitude, longitude, date)
sun_altitude


# In[4]:


def get_sun_altitude(year,month,weekday,hour, lat, long):
  date_1 = datetime.datetime(year,
                           month,
                           weekday,
                           hour,
                           0, 
                           0, 
                           tzinfo=tzone)
  date_2 = datetime.datetime(year,
                               month,
                               weekday+7,
                               hour,
                               0, 
                               0, 
                               tzinfo=tzone)
  date_3 = datetime.datetime(year,
                               month,
                               weekday+14,
                               hour,
                               0, 
                               0, 
                               tzinfo=tzone)
  date_4 = datetime.datetime(year,
                               month,
                               weekday+21,
                               hour,
                               0, 
                               0, 
                               tzinfo=tzone)
  sun_altitude = get_altitude(lat, long, date_1) + get_altitude(lat, long, date_2) + get_altitude(lat, long, date_3) + get_altitude(lat, long, date_4)
  sun_altitude = sun_altitude/4
  return float(sun_altitude)


# In[5]:


get_sun_altitude(2022,4,1,16,52.509,13.385)


# In[6]:


import findspark
findspark.init()
findspark.find()
import pyspark
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType, FloatType, DoubleType


# In[7]:


from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
conf = pyspark.SparkConf().setAppName('ML_Project').setMaster('local')
sc = pyspark.SparkContext(conf=conf)
spark = SparkSession(sc)


# In[8]:


df_negative_samples = spark.read.csv('../data/output/negative_samples.csv', header=True, inferSchema=True)


# In[9]:


df_collisions_merged = spark.read.csv('../data/output/df_collisions_merged.csv', header=True, inferSchema=True).dropDuplicates(['segment_id'])


# In[10]:


df_collisions_merged.count()


# In[11]:


df_negative_samples.count()


# In[12]:


df_collisions_merged.show(10)


# In[13]:


df_negative_samples = df_negative_samples.join(df_collisions_merged, df_negative_samples.segment_id == df_collisions_merged.segment_id, "left").select(df_negative_samples['*'],df_collisions_merged['XGCSWGS84'],df_collisions_merged['YGCSWGS84'])


# In[14]:


df_negative_samples = df_negative_samples.withColumn('YGCSWGS84', regexp_replace('YGCSWGS84',',','.'))
df_negative_samples = df_negative_samples.withColumn('XGCSWGS84', regexp_replace('XGCSWGS84',',','.'))


# In[15]:


df_negative_samples=df_negative_samples.withColumn("XGCSWGS84",df_negative_samples.XGCSWGS84.cast(FloatType()))
df_negative_samples=df_negative_samples.withColumn("YGCSWGS84",df_negative_samples.YGCSWGS84.cast(FloatType()))


# In[16]:


df_negative_samples.show(5)


# In[17]:


sun_elevation_udf = udf(lambda year,month,weekday,hour,lat,long: get_sun_altitude(year,month,weekday,hour,lat,long), FloatType())


# In[18]:


df_negative_samples = df_negative_samples.withColumn("sun_elevation", sun_elevation_udf(df_negative_samples.year,df_negative_samples.month,df_negative_samples.weekday,df_negative_samples.hour,df_negative_samples.YGCSWGS84,df_negative_samples.XGCSWGS84))


# In[19]:


df_negative_samples.show(10)


# In[20]:


df_negative_samples = df_negative_samples.withColumn("collision", lit(0))


# In[21]:


df_negative_samples = df_negative_samples.drop('_c0')


# In[22]:


df_collisions = spark.read.csv('../data/output/df_collisions_merged.csv', header=True, inferSchema=True)


# In[23]:


df_collisions = df_collisions.select(['hour','year','month','weekday','segment_id','XGCSWGS84','YGCSWGS84'])


# In[24]:


df_collisions = df_collisions.withColumn('YGCSWGS84', regexp_replace('YGCSWGS84',',','.'))
df_collisions = df_collisions.withColumn('XGCSWGS84', regexp_replace('XGCSWGS84',',','.'))


# In[25]:


df_collisions=df_collisions.withColumn("XGCSWGS84",df_collisions.XGCSWGS84.cast(FloatType()))
df_collisions=df_collisions.withColumn("YGCSWGS84",df_collisions.YGCSWGS84.cast(FloatType()))


# In[26]:


df_collisions = df_collisions.withColumn("sun_elevation", sun_elevation_udf(df_collisions.year,df_collisions.month,df_collisions.weekday,df_collisions.hour,df_collisions.YGCSWGS84,df_collisions.XGCSWGS84))


# In[27]:


df_collisions = df_collisions.withColumn('weekday_name',when(df_collisions.weekday == 1,'Sunday').when(df_collisions.weekday == 2,'Monday').when(df_collisions.weekday == 3,'Tuesday').when(df_collisions.weekday == 4,'Wednesday').when(df_collisions.weekday == 5,'Thursday').when(df_collisions.weekday == 6,'Friday').otherwise('Saturday'))


# In[28]:


df_collisions = df_collisions.withColumn("collision", lit(1))


# In[29]:


df_negative_samples.dtypes


# In[30]:


df_collisions.dtypes


# In[31]:


df_collisions.count()


# In[32]:


df_full = df_collisions.union(df_negative_samples)


# In[33]:


df_full.dtypes


# In[ ]:


df_full.show(10)


# In[ ]:


df_full = df_full.withColumn('hour_sin', sin(2 * math.pi * df_full.hour/23.0))
df_full = df_full.withColumn('hour_cos', cos(2 * math.pi * df_full.hour/23.0))
df_full = df_full.withColumn('month_sin', sin(2 * math.pi * df_full.month/12.0))
df_full = df_full.withColumn('month_cos', cos(2 * math.pi * df_full.month/12.0))


# In[ ]:


df_full.toPython().to_csv('full_sample.csv')


# In[ ]:




