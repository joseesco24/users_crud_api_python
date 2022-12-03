# Python
from functools import partial
from datetime import datetime
import logging
import re
import gc

# FastAPI
from fastapi import HTTPException
from fastapi import status

# Commons
from src.commons.path_manager import get_file_name
from src.commons.yaml_reader import yaml_reader

# Database
from src.database.postgres import Postgres

# ETL Core
from src.etl_core.post_transformer import PostTransformer
from src.etl_core.post_transformer import post_transformer
from src.etl_core.transformer import Transformer
from src.etl_core.transformer import transformer
from src.etl_core.extractor import Extractor
from src.etl_core.extractor import extractor
from src.etl_core.mapper import Mapper
from src.etl_core.mapper import mapper

# App Files
from src.commons.config import configs

# Storage
if configs.environment_mode == "production" or configs.storage_mode == "gcs":
    from src.storage.google_cloud_storage import transactional_files
    from src.storage.google_cloud_storage import TransactionalFiles
    from src.storage.google_cloud_storage import configuration_files
    from src.storage.google_cloud_storage import ConfigurationFiles
else:
    from src.storage.local_storage import transactional_files
    from src.storage.local_storage import TransactionalFiles
    from src.storage.local_storage import configuration_files
    from src.storage.local_storage import ConfigurationFiles

__all__ = ["loading_controller", "LoadingController"]

script_name = get_file_name()


class LoadingController:
    def __init__(
        self,
        transactional_files: TransactionalFiles = transactional_files,
        configuration_files: ConfigurationFiles = configuration_files,
        post_transformer: PostTransformer = post_transformer,
        transformer: Transformer = transformer,
        extractor: Extractor = extractor,
        mapper: Mapper = mapper,
        database_instance: Postgres = None,
    ) -> None:
        self.transactional_files = transactional_files
        self.configuration_files = configuration_files

        self.post_transformer = post_transformer
        self.transformer = transformer
        self.extractor = extractor
        self.mapper = mapper

        self.database_instance = database_instance

        self.__error_tail__ = list()

    async def controller(self, file_name: str, file_directory: str) -> None:

        """loading controller

        this is the controller in charge of loading transactional files to a database that is given in
        their respective configuration file, this controller works as an etl pipeline, so it receives
        a transactional file references, then the controller loads it, extract and transform all the
        entities indicated in the configuration file and then loads the results

        args:
        - file_name (str): the name of the file to load
        - file_directory (str): the url of the file to load

        returns:
        - None

        raises HTTPException (status code 424):
        - when a file configuration is not found
        - when a file configuration is not valid
        """

        logging.debug(yaml_reader.get_logg_message(script_name, "logg_001"))

        """
        ----------------------------------------------------------------------------------------------------------------------------
        stage 0 - configuration search
        previous stage results [2]:
        file_name, file_directory
        stage results [4+7]:
        configuration_id, configuration_name, file_name, external_configuration_sign
        ----------------------------------------------------------------------------------------------------------------------------
        """

        logg_data = {"stage_name": "0 - configuration search"}
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_002", logg_data))
        start = datetime.now()

        self.transactional_files.check_if_file_exist(
            file_name=file_name, file_directory=file_directory
        )

        end = datetime.now()
        execution_time = end - start
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_003", logg_data))
        seconds = execution_time.seconds
        milliseconds = int(execution_time.microseconds / 1000)
        logg_data.update(
            {
                "seconds": seconds,
                "milliseconds": milliseconds,
            }
        )
        logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

        settings_map = self.configuration_files.load_settings_map_content()

        for configuration in settings_map:

            match = re.match(configuration["regex"], file_name)

            if match is not None and configuration["isValid"] is True:

                configuration_name = configuration["configName"]
                configuration_id = configuration["configId"]
                configuration_regex = configuration["regex"]

                logg_data = {
                    "configuration_name": configuration["configName"],
                    "file_name": file_name,
                }
                logging.info(
                    yaml_reader.get_logg_message(script_name, "logg_011", logg_data)
                )

                await self.__extract_transform_and_load__(
                    configuration_regex=configuration_regex,
                    configuration_name=configuration_name,
                    configuration_id=configuration_id,
                    file_directory=file_directory,
                    file_name=file_name,
                )

            elif match is None:

                logg_data = {
                    "configuration_name": configuration["configName"],
                    "file_name": file_name,
                }
                logging.info(
                    yaml_reader.get_logg_message(script_name, "logg_010", logg_data)
                )

            elif match is not None and configuration["isValid"] is False:

                msg = yaml_reader.get_error_message(script_name, "error_001")
                logging.error(msg)

        self.database_instance = None

    async def __extract_transform_and_load__(
        self,
        configuration_regex: str,
        configuration_name: str,
        configuration_id: str,
        file_directory: str,
        file_name: str,
    ) -> None:

        error_counter = 0

        external_configuration_sign = (
            f"{configuration_name}:{configuration_id}:{configuration_regex}".lower()
        )

        del configuration_regex
        gc.collect()

        """
        ----------------------------------------------------------------------------------------------------------------------------
        stage 1 - configuration file load
        previous stage results [4+7]:
        configuration_id, configuration_name, file_name, external_configuration_sign
        stage results [7+7]:
        file_name, destination_configuration, domain_file_type, configuration_structure_type, configuration_file_targets
        transformation_map, extraction_map
        ----------------------------------------------------------------------------------------------------------------------------
        """

        logg_data = {"stage_name": "1 - configuration file load"}
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_002", logg_data))
        start = datetime.now()

        configuration_file = self.configuration_files.load_file_content(
            file_name=f"{configuration_id}.json"
        )

        domain_file_type = configuration_file["domainFileType"]

        destination_configuration = configuration_file["destination"]

        configuration_structure_type = configuration_file["fileStructureType"]
        configuration_content_type = configuration_file["fileContentType"]

        configuration_file_targets = configuration_file["targets"]

        configuration_name = configuration_file["configName"]
        configuration_id = configuration_file["configId"]
        configuration_regex = configuration_file["regex"]

        transformation_map = self.mapper.build_transformation_map(
            configuration_file=configuration_file
        )

        batch_transformation_map = self.mapper.build_batch_transformation_map(
            configuration_file=configuration_file
        )

        extraction_map = self.mapper.build_base_extraction_map(
            configuration_file=configuration_file
        )

        internal_configuration_sign = (
            f"{configuration_name}:{configuration_id}:{configuration_regex}".lower()
        )

        if internal_configuration_sign != external_configuration_sign:
            logging.warning(yaml_reader.get_logg_message(script_name, "logg_006"))

        logging.info(
            f"configuration type: {configuration_structure_type}:{configuration_content_type}"
        )

        del (
            internal_configuration_sign,
            external_configuration_sign,
            configuration_content_type,
            configuration_regex,
            configuration_file,
            configuration_name,
            configuration_id,
        )
        gc.collect()

        end = datetime.now()
        execution_time = end - start
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_003", logg_data))
        seconds = execution_time.seconds
        milliseconds = int(execution_time.microseconds / 1000)
        logg_data.update(
            {
                "seconds": seconds,
                "milliseconds": milliseconds,
            }
        )
        logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

        """
        ----------------------------------------------------------------------------------------------------------------------------
        stage 2 - warming database instance
        previous stage results:
        previous stage results [7+7]:
        file_name, destination_configuration, domain_file_type, configuration_structure_type, configuration_file_targets
        transformation_map, extraction_map
        stage results [8+7]:
        file_name, domain_file_type, configuration_structure_type, configuration_file_targets
        transformation_map, extraction_map, table
        ----------------------------------------------------------------------------------------------------------------------------
        """

        logg_data = {"stage_name": "2 - warming database instance"}
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_002", logg_data))
        start = datetime.now()

        if "calendar" in destination_configuration:
            calendar_table = destination_configuration["calendar"]
        else:
            calendar_table = None

        on_error_table = destination_configuration["onError"]
        on_load_table = destination_configuration["onLoad"]
        target_table = destination_configuration["target"]
        schema = destination_configuration["schema"]

        password = destination_configuration["credentials"]["password"]
        user = destination_configuration["credentials"]["user"]
        host = destination_configuration["credentials"]["host"]
        name = destination_configuration["credentials"]["name"]
        port = destination_configuration["credentials"]["port"]

        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{name}"

        if self.database_instance is None:
            self.database_instance = Postgres(
                connection_string=connection_string, schema=schema
            )

        self.database_instance.start_connection()

        if batch_transformation_map is None:
            self.database_instance.check_mandatory_table_schema(
                table_name=target_table["name"], table_keys=extraction_map.keys()
            )

        if calendar_table is not None:
            self.database_instance.check_mandatory_table_schema(
                table_name=calendar_table["name"],
                table_keys=calendar_table["keys"].values(),
            )

        if batch_transformation_map is not None:
            for treatement_config in batch_transformation_map:
                if treatement_config["method"] == "database_reference_replacer":
                    replace_keys: list[str] = list()
                    for replace_dict in treatement_config["parameters"][
                        "filter_using_keys"
                    ]:
                        replace_keys.append(replace_dict["as"])
                    self.database_instance.check_mandatory_table_schema(
                        table_name=treatement_config["parameters"]["target_table"],
                        table_keys=replace_keys,
                    )

        self.database_instance.check_mandatory_table_schema(
            table_name=on_error_table["name"],
            table_keys=on_error_table["keys"].values(),
        )
        self.database_instance.check_mandatory_table_schema(
            table_name=on_load_table["name"],
            table_keys=on_load_table["keys"].values(),
        )
        self.database_instance.check_mandatory_table_schema(
            table_name=target_table["name"],
            table_keys=target_table["keys"].values(),
        )

        del (
            destination_configuration,
            connection_string,
            password,
            schema,
            user,
            host,
            name,
            port,
        )
        gc.collect()

        end = datetime.now()
        execution_time = end - start
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_003", logg_data))
        seconds = execution_time.seconds
        milliseconds = int(execution_time.microseconds / 1000)
        logg_data.update(
            {
                "seconds": seconds,
                "milliseconds": milliseconds,
            }
        )
        logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

        """
        ----------------------------------------------------------------------------------------------------------------------------
        stage 3 - supplie file loading
        previous stage results [8+7]:
        file_name, domain_file_type, configuration_structure_type, configuration_file_targets
        transformation_map, extraction_map, table
        stage results [9+7]:
        file_name, domain_file_type, configuration_structure_type, configuration_file_targets
        transformation_map, extraction_map, table, transactional_file
        ----------------------------------------------------------------------------------------------------------------------------
        """

        logg_data = {"stage_name": "3 - supplie file loading"}
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_002", logg_data))
        start = datetime.now()

        transactional_file = self.transactional_files.load_file_content(
            file_name=file_name, file_directory=file_directory
        )

        end = datetime.now()
        execution_time = end - start
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_003", logg_data))
        seconds = execution_time.seconds
        milliseconds = int(execution_time.microseconds / 1000)
        logg_data.update(
            {
                "seconds": seconds,
                "milliseconds": milliseconds,
            }
        )
        logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

        """
        ----------------------------------------------------------------------------------------------------------------------------
        stage 4 - supplie file data extraction
        previous stage results [9+7]:
        file_name, domain_file_type, configuration_structure_type, configuration_file_targets
        transformation_map, extraction_map, table, transactional_file
        stage results [6+7]:
        file_name, domain_file_type, transformation_map, table, extracted_data
        ----------------------------------------------------------------------------------------------------------------------------
        """

        logg_data = {"stage_name": "4 - supplie file data extraction"}
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_002", logg_data))
        start = datetime.now()

        extracted_data = self.extractor.extract_data_into_extraction_maps(
            extraction_map=extraction_map,
            transactional_file=transactional_file,
            configuration_file_targets=configuration_file_targets,
            configuration_structure_type=configuration_structure_type,
        )
        extracted_data_length = len(extracted_data)

        del (
            configuration_structure_type,
            configuration_file_targets,
            transactional_file,
            extraction_map,
            file_directory,
        )
        gc.collect()

        end = datetime.now()
        execution_time = end - start
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_003", logg_data))
        seconds = execution_time.seconds
        milliseconds = int(execution_time.microseconds / 1000)
        logg_data.update(
            {
                "seconds": seconds,
                "milliseconds": milliseconds,
            }
        )
        logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

        """
        ----------------------------------------------------------------------------------------------------------------------------
        stage 5 - supplie file data cleaning
        previous stage results [6+7]:
        file_name, domain_file_type, transformation_map, table, extracted_data
        stage results [6+7]:
        file_name, domain_file_type, transformation_map, table, clean_data
        ----------------------------------------------------------------------------------------------------------------------------
        """

        logg_data = {"stage_name": "5 - supplie file data cleaning"}
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_002", logg_data))
        start = datetime.now()

        clean_data = self.mapper.flatt_extraction_maps(extraction_maps=extracted_data)

        del extracted_data
        gc.collect()

        end = datetime.now()
        execution_time = end - start
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_003", logg_data))
        seconds = execution_time.seconds
        milliseconds = int(execution_time.microseconds / 1000)
        logg_data.update(
            {
                "seconds": seconds,
                "milliseconds": milliseconds,
            }
        )
        logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

        """
        ----------------------------------------------------------------------------------------------------------------------------
        stage 6 - supplie file data transformation
        previous stage results [6+7]:
        file_name, domain_file_type, transformation_map, table, clean_data
        stage results [5+7]:
        file_name, domain_file_type, table, final_data
        ----------------------------------------------------------------------------------------------------------------------------
        """

        # TODO: improve database objet propagation

        logg_data = {"stage_name": "6 - supplie file data transformation"}
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_002", logg_data))
        start = datetime.now()

        if calendar_table is not None:
            final_data_with_errors = self.transformer.transform(
                data=clean_data,
                transformation_map=transformation_map,
                database_instance=self.database_instance,
                table_metadata=calendar_table,
            )
        else:
            final_data_with_errors = self.transformer.transform(
                data=clean_data,
                transformation_map=transformation_map,
                database_instance=self.database_instance,
            )

        final_data = list()

        data = {}
        for data in final_data_with_errors:
            if "error" in data:
                self.__error_tail__.append(data)
                error_counter += 1
            else:
                final_data.append(data)

        del transformation_map, clean_data, data, final_data_with_errors
        gc.collect()

        end = datetime.now()
        execution_time = end - start
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_003", logg_data))
        seconds = execution_time.seconds
        milliseconds = int(execution_time.microseconds / 1000)
        logg_data.update(
            {
                "seconds": seconds,
                "milliseconds": milliseconds,
            }
        )
        logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

        logg_data.update({"count": error_counter})
        logging.info(yaml_reader.get_logg_message(script_name, "logg_008", logg_data))

        """
        ----------------------------------------------------------------------------------------------------------------------------
        stage 7 - loading data into database
        previous stage results [5+7]:
        file_name, domain_file_type, table, final_data
        ----------------------------------------------------------------------------------------------------------------------------
        """

        logg_data = {"stage_name": "7 - loading data into database"}
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_002", logg_data))
        start = datetime.now()

        register_dict = {
            on_load_table["keys"]["registersCount"]: extracted_data_length,
            on_load_table["keys"]["timeStamp"]: datetime.now(),
            on_load_table["keys"]["domain"]: domain_file_type,
            on_load_table["keys"]["fileName"]: file_name,
        }

        file_register_result = self.database_instance.load_one(
            table_name=on_load_table["name"],
            data=register_dict,
        )

        if type(file_register_result) is dict and "error" in file_register_result:
            msg = yaml_reader.get_error_message(script_name, "error_003")
            logging.error(msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )

        if batch_transformation_map is not None:
            final_data = self.post_transformer.transform(
                batch_transformation_map=batch_transformation_map,
                database_instance=self.database_instance,
                data=final_data,
            )

            final_data_0 = list()

            for data in final_data:
                if type(data) is dict and "error" in data:
                    self.__error_tail__.append(data)
                    error_counter += 1
                else:
                    final_data_0.append(data)

            final_data = final_data_0

        data = list(
            map(
                partial(
                    self.transformer.add_values_to_dict,
                    values={
                        target_table["keys"]["onLoadReference"]: int(
                            file_register_result
                        )
                    },
                ),
                final_data,
            )
        )

        loaded_registers = self.database_instance.load_batch(
            table_name=target_table["name"],
            data=data,
        )

        for data in loaded_registers:
            if type(data) is dict and "error" in data:
                self.__error_tail__.append(data)
                error_counter += 1

        del loaded_registers, data
        gc.collect()

        end = datetime.now()
        execution_time = end - start
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_003", logg_data))
        seconds = execution_time.seconds
        milliseconds = int(execution_time.microseconds / 1000)
        logg_data.update(
            {
                "seconds": seconds,
                "milliseconds": milliseconds,
            }
        )
        logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

        logg_data.update({"count": error_counter})
        logging.info(yaml_reader.get_logg_message(script_name, "logg_008", logg_data))

        """
        ----------------------------------------------------------------------------------------------------------------------------
        stage 8 - errors tail cleaning
        ----------------------------------------------------------------------------------------------------------------------------
        """

        logg_data = {"stage_name": "8 - errors tail cleaning"}
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_002", logg_data))
        start = datetime.now()

        register_dict = {
            on_load_table["keys"]["errorCount"]: error_counter,
            on_load_table["keys"]["successCount"]: (
                extracted_data_length - error_counter
            ),
        }

        self.database_instance.update_one(
            table_name=on_load_table["name"],
            primary_key_value=file_register_result,
            data=register_dict,
        )

        logging.debug(yaml_reader.get_logg_message(script_name, "logg_009"))

        data = list()

        for register in self.__error_tail__:
            data.append(
                {
                    on_error_table["keys"]["onLoadReference"]: int(
                        file_register_result
                    ),
                    on_error_table["keys"][
                        "traceback"
                    ]: f"{str(register['error']['error type']).replace('/n', '')}: {str(register['error']['error message']).replace('/n', '')}".strip()[
                        :500
                    ],
                    on_error_table["keys"]["number"]: register["error"]["lineno"],
                }
            )

        loaded_registers = self.database_instance.load_batch(
            table_name=on_error_table["name"],
            data=data,
        )

        self.database_instance.close_connection()
        self.database_instance = None

        end = datetime.now()
        execution_time = end - start
        logging.debug(yaml_reader.get_logg_message(script_name, "logg_003", logg_data))
        seconds = execution_time.seconds
        milliseconds = int(execution_time.microseconds / 1000)
        logg_data.update(
            {
                "seconds": seconds,
                "milliseconds": milliseconds,
            }
        )
        logging.info(yaml_reader.get_logg_message(script_name, "logg_004", logg_data))

        logging.debug(yaml_reader.get_logg_message(script_name, "logg_005"))
