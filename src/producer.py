import json
from typing import Dict, List

import requests
from dotenv import dotenv_values
from kafka import KafkaProducer
from unidecode import unidecode

from src.models.bus_company import BusCompany


class BusProducer:
    """Class to define Kafka Producer for live running Buses"""

    def __init__(self, producer_config: Dict) -> None:
        self.producer = KafkaProducer(**producer_config)

    def __authenticate_with_external_api(self) -> str:
        """Method to authenticate in the SPTRANS API.

        Args:
            None
        Returns:
            str: api credentials for sptrans api.
        """
        config = dotenv_values(".env")
        auth = requests.post(
            f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={config['SPTRANS_API_KEY']}"
        )
        api_credentials = auth.headers["Set-Cookie"].split(";")[0].split("=")[-1]
        return api_credentials

    def map_buses_companies(self) -> List[BusCompany]:
        """Method to consume the resource `/Empresa` of SPTRANS API.

        Args:
            None
        Returns:
            List[BusCompany]: List of buses companies that operates under SpTrans
        """
        api_credentials = self.__authenticate_with_external_api()
        r = requests.get(
            "http://api.olhovivo.sptrans.com.br/v2.1/Empresa",
            cookies={"apiCredentials": api_credentials},
        )
        companies = []
        for key, value in r.json().items():
            if isinstance(value, list):
                for item in value:
                    for i in item["e"]:
                        companies.append(BusCompany(i["a"], i["c"], unidecode(i["n"])))
        return companies

    def map_stopped_buses_garage_raw(self, companies: List[BusCompany]) -> List:
        """Method to consume the resource `/Posicao/Garagem` of SPTRANS API.

        Args:
            List[BusCompany]: List of buses companies that operates under SpTrans .
        Returns:
            List[BusCompany]: List of buses companies that operates under SpTrans with updated values.
        """
        api_credentials = self.__authenticate_with_external_api()
        result_list = []

        for company in companies:
            url = f"http://api.olhovivo.sptrans.com.br/v2.1/Posicao/Garagem?codigoEmpresa={company.company_reference_code}"
            r = requests.get(url=url, cookies={"apiCredentials": api_credentials})
            result_json = r.json()

            result_json["company_data"] = [company.__dict__]

            """
            parsing the value of 'qv' to doesnt generate inconsistent values in the `.count()` function.
            also fix unicode erros for words with accentuation.
            for example: if `qv` is 3, it means that there are 3 stopped buses in the company garage
                and after we parse the json to rows, the `qv` for the companie will be the same for all entries,
                so we need to set to 1, so each row will be an individual bus.
            """
            for key, value in result_json.items():
                if key == "l":
                    for v in value:
                        v["lt0"] = unidecode(v["lt0"])
                        v["lt1"] = unidecode(v["lt1"])
                        v["qv"] = int(len(v["vs"]) / len(v["vs"]))
            result_list.append(json.dumps(result_json))
        print(result_list)
        return result_list

    def running_buses_by_line(self):
        """Method to get the live running buses separated by line name and line number"""
        api_credentials = self.__authenticate_with_external_api()
        url = "http://api.olhovivo.sptrans.com.br/v2.1/Posicao"
        r = requests.get(url=url, cookies={"apiCredentials": api_credentials})
        result_list = []
        for key, value in r.json().items():
            if key == "l":
                for record in value:
                    result_list.append(
                        json.dumps(
                            {"c": record["c"], "cl": record["cl"], "qv": record["qv"]}
                        )
                    )
        print(result_list)
        return result_list

    @staticmethod
    def success_delivery_report(event):
        """Callback method for kafka producer."""
        print(f"Message successfully produced to topic: {event.topic}")

    def publish_data(self, topic: str, records):
        """Method to publish data into kafka topic."""
        for idx, value in enumerate(records):
            try:
                data = self.producer.send(topic=topic, key=str(idx), value=value)
                self.success_delivery_report(data.get())
            except KeyboardInterrupt:
                print("Canceled by user.")
                break
            except Exception as e:
                print(f"Exception while producing record - {str(idx)}: {e}")
        self.producer.flush()
