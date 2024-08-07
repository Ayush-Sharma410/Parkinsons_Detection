import os
import sys
from src.parkinsons_detection.exception import CustomException
from src.parkinsons_detection.logger import logging
import pandas as pd
from src.parkinsons_detection.utils import read_sql_data

from sklearn.model_selection import train_test_split

from dataclasses import dataclass


@dataclass
class DataIngestionConfig:
    train_data_path:str=os.path.join('artifacts','train.csv')
    test_data_path:str=os.path.join('artifacts','test.csv')
    raw_data_path:str=os.path.join('artifacts','raw.csv')

class DataIngestion:
    def __init__(self):
        self.ingestion_config=DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Entered the data ingestion method or component")
        try:
            # ##reading the data from mysql
            # df = read_sql_data()
            # logging.info("Reading completed mysql database")
            
        
            df=pd.read_csv('notebook\Gait_Data___Arm_swing_02Apr2024.csv')
            logging.info('Read the dataset as dataframe')

            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path),exist_ok=True)

            df.to_csv(self.ingestion_config.raw_data_path,index=False,header=True)
            df = df = df.iloc[:,3:]
            df = df.dropna(subset=['COHORT'])
            df.COHORT = df.COHORT.replace({1.0:0, 3.0:1})

            train_set,test_set=train_test_split(df,test_size=0.2,random_state=42)
            logging.info(f'train_df in data ingestion: {train_set.shape}')
            train_set.to_csv(self.ingestion_config.train_data_path,index=False,header=True)
            test_set.to_csv(self.ingestion_config.test_data_path,index=False,header=True)
            # logging.info(f'Train set columns {train_set.columns}')

            logging.info("Data Ingestion is completed")

            return(
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path


            )


        except Exception as e:
            raise CustomException(e,sys)