import json
import os
import re
from pathlib import Path
from typing import List

import pandas
import requests
from dotenv import dotenv_values
from unidecode import unidecode


def get_credentials() -> str:
    """Method to get the authentication cookies from SPTRANS Api.

    Args:
        None
    Returns:
        str: string containing the authentication cookie
    """
    config = dotenv_values(".env")
    auth = requests.post(
        f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={config['SPTRANS_API_KEY']}"
    )
    api_credentials = auth.headers["Set-Cookie"].split(";")[0].split("=")[-1]
    return api_credentials


def get_live_buses() -> List:
    """Method to query the `Posicao` resource to get the live running buses

    Args:
        None
    Returns:
        List: list containing the line name and line number of current running buses
    """
    api_credentials = get_credentials()
    url = "http://api.olhovivo.sptrans.com.br/v2.1/Posicao"
    r = requests.get(url=url, cookies={"apiCredentials": api_credentials})
    position_list = []
    for key in r.json().keys():
        if key == "l":
            for item in r.json()["l"]:
                position_list.append([item["c"], item["cl"]])
    return position_list


def scrap_data_from_live_api() -> None:
    """Method to generate CSV file from API scraping

    Args:
        None
    Returns:
        None: Just generates a new csv file with updated data.
    """
    with open("bus-data/company_mismatch_list.json", "r") as n_f:
        fixed_company_name_file = json.load(n_f)

    position_list = get_live_buses()

    result_list = []
    try:
        print(f"running lines: {len(position_list)}")
        for idx, entry in enumerate(position_list):
            line_name = entry[0]
            r = requests.get(
                f"https://sistemas.sptrans.com.br/PlanOperWeb/detalheLinha.asp?TpDiaID=0&project=OV&lincod={line_name}"
            )
            regex_str_company_name = (
                '(<input type="text" id="empresa" disabled="disabled" value=").*(" />)'
            )
            regex_str_region_id = (
                '(<input type="text" id="areCod" disabled="disabled" value=").*(" />)'
            )
            regex_company_name = re.search(regex_str_company_name, r.text)
            regex_region_id = re.search(regex_str_region_id, r.text)

            if regex_company_name is None:
                """Invalid line_name"""
                print(f"ext-{idx}-error ({line_name} -> {line_name+str(0)})")
                r = requests.get(
                    f"https://sistemas.sptrans.com.br/PlanOperWeb/detalheLinha.asp?TpDiaID=0&project=OV&lincod={line_name}0"
                )
                regex_str_company_name = '(<input type="text" id="empresa" disabled="disabled" value=").*(" />)'
                regex_str_region_id = '(<input type="text" id="areCod" disabled="disabled" value=").*(" />)'
                regex_company_name = re.search(regex_str_company_name, r.text)
                regex_region_id = re.search(regex_str_region_id, r.text)

                line_name = line_name + str(0)

            c_name = unidecode(
                regex_company_name.group().split('value="')[-1].split('"')[0].lower()
            )
            region_id = regex_region_id.group().split('value="')[-1].split('"')[0]

            for known_companies in fixed_company_name_file:
                if known_companies["id"] == c_name:
                    c_name = known_companies["fix"]

            print("ext", idx, (line_name, int(entry[1]), c_name, int(region_id)))
            result_list.append((line_name, int(entry[1]), c_name, int(region_id)))

        columns = ["line_sign_name", "line_number", "company_name", "region_id"]
        generate_file(set(result_list), "1-scrapped_data.csv", columns, False)
    except KeyboardInterrupt:
        columns = ["line_sign_name", "line_number", "company_name", "region_id"]
        generate_file(set(result_list), "1-scrapped_data.csv", columns, False)
    except Exception as e:
        print(f"ext-{idx}-error", e)


def generate_file(
    mapped_list: List, file_name: str, columns: List, header: bool
) -> None:
    """Method to generate CSV file

    Args:
        mapped_list (List): List containing live bus data
        file_name (str): File name
        columns (List): List of strings of column names
        header (bool): Add CSV header or not. (True or False)
    Returns:
        None: Just generates a new csv file with updated data.
    """
    df = pandas.DataFrame(data=mapped_list, columns=columns)
    path = Path(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(path, "bus-data/", file_name)
    df.to_csv(path, mode="a", index=False, header=header)


def map_data_from_file_source(file_path: str) -> None:
    """Method to verify from which company the provided line_name is from.

    Args:
        file_path (str): CSV file which contains the data that will be validated.
            The file needs to contain the line_name and line_number columns
    Returns:
        None: Just generates a new csv file with updated data.
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    with open("bus-data/company_mismatch_list.json", "r") as n_f:
        fixed_company_name_file = json.load(n_f)

    result_list = []
    for idx, entry in enumerate(lines[1:]):
        line_name = entry.split(",")[0].strip()

        r = requests.get(
            f"https://sistemas.sptrans.com.br/PlanOperWeb/detalheLinha.asp?TpDiaID=0&project=OV&lincod={line_name}"
        )

        regex_str_company_name = (
            '(<input type="text" id="empresa" disabled="disabled" value=").*(" />)'
        )
        regex_str_region_id = (
            '(<input type="text" id="areCod" disabled="disabled" value=").*(" />)'
        )
        regex_company_name = re.search(regex_str_company_name, r.text)
        regex_region_id = re.search(regex_str_region_id, r.text)

        if regex_company_name is None:
            """Invalid line_name"""
            print(f"ext-{idx}-error ({line_name} -> {line_name+str(0)})")
            r = requests.get(
                f"https://sistemas.sptrans.com.br/PlanOperWeb/detalheLinha.asp?TpDiaID=0&project=OV&lincod={line_name}0"
            )
            regex_str_company_name = (
                '(<input type="text" id="empresa" disabled="disabled" value=").*(" />)'
            )
            regex_str_region_id = (
                '(<input type="text" id="areCod" disabled="disabled" value=").*(" />)'
            )
            regex_company_name = re.search(regex_str_company_name, r.text)
            regex_region_id = re.search(regex_str_region_id, r.text)

            line_name = line_name + str(0)

        c_name = unidecode(
            regex_company_name.group().split('value="')[-1].split('"')[0].lower()
        )
        region_id = regex_region_id.group().split('value="')[-1].split('"')[0]

        for known_companies in fixed_company_name_file:
            if known_companies["id"] == c_name:
                print("entrou", c_name)
                c_name = known_companies["fix"]

        print("ext", idx, (line_name, int(entry.split(",")[1]), c_name, int(region_id)))
        result_list.append(
            (line_name, int(entry.split(",")[1]), c_name, int(region_id))
        )

    columns = ["line_sign_name", "line_number", "company_name", "region_id"]
    generate_file(set(result_list), "2-scrapped_data_v2.csv", columns, False)


def remove_duplicates() -> None:
    """Method to remove duplicated values"""
    with open("bus-data/2-scrapped_data_v3.csv", "r") as f:
        arr_1 = f.readlines()

    """with open("bus-data/aa.csv", "r") as f:
        arr_2 = f.readlines()"""

    # arr_uion = arr_1[1:] + arr_2[1:]

    result_list = [
        (
            line.split(",")[0],
            int(line.split(",")[1]),
            line.split(",")[2],
            int(line.split(",")[3].strip()),
        )
        for line in arr_1[1:]
    ]
    columns = ["line_sign_name", "line_number", "company_name", "region_id"]
    generate_file(set(result_list), "2-scrapped_data_v3.csv", columns, False)


if __name__ == "__main__":
    # map_data_from_file_source(file_path='bus-data/bquxjob_15b49f88_188debeaab7.csv')
    # scrap_data_from_live_api()
    # remove_duplicates()
    pass
