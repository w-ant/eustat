from bs4 import BeautifulSoup
import requests
import os
import pandas as pd
from csv import writer
from tqdm import tqdm
import sqlite3
import py7zr
import shutil

url = "http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=comext%2FCOMEXT_DATA%2FPRODUCTS"
output_dir = "../data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
database = os.path.join(output_dir, "eurostat.db")
conn = sqlite3.connect(database)


def create_directory(directory, output_dir=output_dir):
    new_path = os.path.join(output_dir, directory)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path


def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    file_urls = [
        link["href"]
        for link in soup.select("tr>td:nth-of-type(1) a")
        if link["href"][-5:-3] != "52"
        and link["href"][-2:] == "7z"
        and link["href"][-13:-9] == "full"
    ]
    return file_urls


def save_links_as_csv(file_urls):
    file_name = "files_urls.csv"
    csv_path = create_directory("csv")
    file_path = os.path.join(csv_path, file_name)

    with open(file_path, "w") as f:
        csv_writer = writer(f)
        for url in file_urls:
            csv_writer.writerow([url[-13:], url])


def download_file(file_url):
    download_path = create_directory("download")
    filename = file_url[-13:]
    r = requests.get(file_url, stream=True)
    total_size = int(r.headers.get("content-length", 0))
    block_size = 1024
    wrote = 0
    print(f"Downloading {filename}")
    file_path = os.path.join(download_path, filename)
    with open(file_path, "wb") as f:
        with tqdm(
            total=total_size / (32 * 1024),
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in r.iter_content(32 * 1024):
                f.write(data)
                pbar.update(len(data))
    return file_path


def extract(filepath):
    print(f"Exracting {filepath}\n")
    unzipped_path = create_directory("unzipped")
    archive = py7zr.SevenZipFile(file_path, mode="r")
    output_file_path = os.path.join(unzipped_path, archive.getnames()[0])
    archive.extractall(path=unzipped_path)
    archive.close()
    return output_file_path


def add_to_database(file_path):
    df = pd.read_csv(
        file_path,
        usecols=[
            "PERIOD",
            "DECLARANT_ISO",
            "PARTNER_ISO",
            "TRADE_TYPE",
            "PERIOD",
            "VALUE_IN_EUROS",
        ],
    )
    data = df.groupby(by=["PERIOD", "DECLARANT_ISO", "TRADE_TYPE", "PARTNER_ISO"])
    data = data.agg({"VALUE_IN_EUROS": "sum"})
    data.to_sql("trade", conn, if_exists="append")
    print(f"{file_path} added to database")


if __name__ == "__main__":
    links = get_links(url)
    save_links_as_csv(links)
    for link in links:
        file_path = download_file(link)
        csv_file = extract(file_path)
        add_to_database(csv_file)
        os.remove(file_path)
        os.remove(csv_file)
    df = pd.read_csv("countries.csv")
    df.to_sql("countries", conn, if_exists="replace")
    conn.close()
    shutil.copyfile(database, "../api/eurostat.db")
