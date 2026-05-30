from netsecurity.components.data_ingestion import DataIngestion
from netsecurity.components.data_validation import DataValidation
from netsecurity.components.data_transformation import DataTransformation
from netsecurity.exception.exception import NetworkSecurityException
from netsecurity.logging.logger import logging
from netsecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig, DataTransformationConfig
from netsecurity.entity.config_entity import TrainingPipelineConfig


import sys

if __name__ == '__main__':
    try:
        trainingpipelineconfig = TrainingPipelineConfig()
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion=DataIngestion(dataingestionconfig)
        logging.info("Initiate the data ingestion")
        dataingestionartifact= data_ingestion.initiate_data_ingestion()
        logging.info("Data Initiation completed.")
        print(dataingestionartifact)
        data_validation_config=DataValidationConfig(trainingpipelineconfig)
        data_validation = DataValidation(dataingestionartifact,data_validation_config)
        logging.info("Initiate the data validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation completed")
        print(data_validation_artifact)
        data_transformation_config = DataTransformationConfig(trainingpipelineconfig)
        logging.info("data transformation started")
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("data transformation completed")
    except Exception as e:
        raise NetworkSecurityException(e,sys)