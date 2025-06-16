from datetime import datetime, timedelta

import io
import os
import requests
import zipfile


def download_today_public_data():
    financial_disclosures_report_2025_url = "https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2025FD.zip"
    response = requests.get(financial_disclosures_report_2025_url)

    if response.status_code == 200:
        # Extraction of today's zip file
        z = zipfile.ZipFile(io.BytesIO(response.content))
        today = datetime.today()
        today_folder_name = "disclosures_" + today.strftime("%m_%d_%Y")
        path_to_folder = os.path.join('financial_disclosures', today_folder_name)
        z.extractall(path_to_folder)
    else:
        print('Status code is not 200')


def compare_today_yesterday():
    today = datetime.today()
    today_folder_name = "disclosures_" + today.strftime("%m_%d_%Y")
    file_name = '2025FD.txt'  # To be updated yearly
    path_today_txt_file = os.path.join("financial_disclosures", today_folder_name, file_name)
    download_today_public_data()

    # Reading today and yesterday's txt files
    yesterday = today - timedelta(1)
    yesterday_folder_name = "disclosures_" + yesterday.strftime("%m_%d_%Y")
    path_yesterday_txt_file = os.path.join("financial_disclosures", yesterday_folder_name, file_name)

    # Comparing the contents and extracting the difference
    if not os.path.exists(path_yesterday_txt_file):
        with open(path_today_txt_file) as today_txt_file:
            differences = set(today_txt_file.readlines())
    else:
        with open(path_today_txt_file) as today_txt_file, open(path_yesterday_txt_file) as yesterday_txt_file:
            differences = set(today_txt_file.readlines()) - set(yesterday_txt_file.readlines())

    # Comparing today and yesterday
    if differences != set():
        new_entries_list = [diff.split("\t") for diff in differences]
        messages_list = [
            "New entry from {0} {1} {2} on {3}, disclosure_id: {4}".format(entry[0], entry[1], entry[2], entry[7],
                                                                           entry[8][:-1])
            for entry in new_entries_list]
        return messages_list, new_entries_list
    else:
        return ['No new congressional shenanigans'], list()


def get_response(disclosure_id):
    """
    There are two different base URLs on the disclosures-clerk website corresponding
    to two types of files:
    https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2025/ => for new stock purchases
    https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2025/ => for other documents
    """

    disclosure_url = 'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2025/' + disclosure_id + '.pdf'
    document_type = 'stock_purchases'
    response = requests.get(disclosure_url)

    if response.status_code != 200:
        disclosure_url = 'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2025/' + disclosure_id + '.pdf'
        document_type = 'other_documents'
        response = requests.get(disclosure_url)

    return response, document_type


def get_disclosure(response, document_type, full_name, disclosure_id):
    path_to_folder = os.path.join(document_type, datetime.today().strftime('%m_%d_%Y'))
    path_to_file = os.path.join(path_to_folder, full_name.replace('"', '') + '_' + disclosure_id + '.pdf')

    if not os.path.exists(path_to_folder):
        os.mkdir(path_to_folder)

    with open(path_to_file, 'wb') as disclosure:
        disclosure.write(response.content)
    print("File was written to: ", path_to_file)


def run():
    download_today_public_data()
    messages_list, new_entries_list = compare_today_yesterday()
    for entry in new_entries_list:
        disclosure_id = entry[8][:-1]
        response, document_type = get_response(disclosure_id)
        full_name = entry[1] + entry[2]
        get_disclosure(response, document_type, full_name, disclosure_id)

    for message in messages_list:
        print(message)

    return messages_list
