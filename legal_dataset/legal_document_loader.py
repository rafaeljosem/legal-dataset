# legal_document_loader.py

"""
Module: legal_document_loader.py
Description: Module for loading legal documents from various sources.
"""

import os
import re
import zipfile
from typing import Dict, List

import pandas as pd
import requests
from utf8_encoder import convert_to_utf8

def remove_new_lines(lines: list) -> list:
    clean_text = []
    for line in lines:
        if not isinstance(line, str):
            continue
        line = line.strip(' ')
        if line == '':
            continue
        clean_text.append(line)
    return clean_text


class LegalDocumentLoader:
    """
    Class for loading legal documents from various sources.
    """

    @staticmethod
    def clean_text(doc):
        """
        Function that removes more that two subsequent line breaks

        :param doc: The text content of the legal document.
        """
        if isinstance(doc, (str, bytes)):
            # Remove all subsequent line breaks greater than 2
            clean_text = re.sub('\n{1,} | \n', '\n', doc)
            clean_text = re.sub('\n{2,}', '\n\n', clean_text)

            return clean_text
        else:
            return ""

    @staticmethod
    def load_from_url(url: str) -> List[Dict[str, str]]:
        """
        Load legal documents from a URL.

        :param url: The URL containing the ZIP file with the legal documents.
        :return: List of dictionaries, where each dictionary represents a legal document with keys 'Title', 'Filename', and 'Text'.
        """
        # Download the ZIP file from the URL
        response = requests.get(url)
        zip_filename = "legal_documents.zip"
        with open(zip_filename, "wb") as file:
            file.write(response.content)

        # print(f"Downloaded ZIP file: {zip_filename}")

        # Extract the contents of the ZIP file
        extract_directory = "legal_documents"
        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(extract_directory)

        # print(f"Extracted ZIP file to directory: {extract_directory}\n\n")

        legal_documents = []

        # Iterate over the extracted files and read their content
        for path, folders, files in os.walk(extract_directory):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(path, file)
                    # print(f"Processing file: {file_path}\n\n")
                    try:
                        with open(file_path, "r", encoding="latin-1") as f:
                            text = f.read().splitlines()
                            clean_text = remove_new_lines(text)
                            # print(f"Cleaned text: {clean_text[0:1000]}\n")
                            if len(clean_text) != 0:
                                # Extract the title from the first line
                                title = clean_text[0].strip()
                                title = convert_to_utf8(
                                    title.encode('latin-1'))
                                # print(f"Extracted title: {title}\n")
                                # Join the remaining lines as the content
                                content = "\n".join(clean_text[1:])
                                content = convert_to_utf8(
                                    content.encode('latin-1'))
                                # print(f"Extracted content: {content[0:1000]}\n")
                                legal_documents.append({
                                    "Title": title,
                                    "Filename": file,
                                    "Text": content
                                })
                                # print(f"Extracted legal document: {legal_documents}")
                    except UnicodeDecodeError:
                        print(
                            f"**Skipping file {file_path} due to encoding issues.**\n")
                    except Exception as e:
                        print(e)

        # print(f"\n\nExtracted legal documents: {legal_documents}")
        # print(f"Number of legal documents extracted: {len(legal_documents)}")
        # print(f"Type of legal documents: {type(legal_documents)}")
        # print(f"Example legal document: {legal_documents[0]}")
        # print(f"Example legal document text: {legal_documents[0]['Text'][500:700]}")

        # Clean up the downloaded ZIP file and extracted directory
        os.remove(zip_filename)
        for path, folders, files in os.walk(extract_directory, topdown=False):
            for file in files:
                os.remove(os.path.join(path, file))
            for folder in folders:
                os.rmdir(os.path.join(path, folder))
        os.rmdir(extract_directory)

        # print(f"\nCleaned up downloaded ZIP file and extracted directory.")

        return legal_documents

    @ staticmethod
    def load_from_csv(file_path: str) -> List[str]:
        """
        Load legal documents from a CSV file.

        :param file_path: The path to the CSV file containing the legal documents.
        :return: List of strings, where each string represents the text content of a legal document.
        """
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(file_path, index_col=0)

        name_list = df.index.to_list()
        
        # Check if the 'Text' column exists in the DataFrame
        if 'Text' not in df.columns:
            raise ValueError("The 'Text' column is missing in the CSV file.")

        # Apply the clean_text function to the 'Text' column and create a new 'Clean Text' column
        df['Clean Text'] = df['Text'].apply(lambda x: LegalDocumentLoader.clean_text(
            x) if isinstance(x, (str, bytes)) else "")

        # Extract the text content from the 'Clean Text' column and convert it to a list of strings
        text_list = df['Clean Text'].tolist()

        # Remove any None or empty values from the list
        text_list = [doc for doc in text_list if doc and isinstance(doc, str)]

        # Initialize an empty list called 'legal_documents'
        legal_documents = []

        # Iterate through the elements of 'name_list' and 'text' simultaneously using zip
        for name_item, text_item in zip(name_list, text_list):
            # Create a dictionary with keys 'name' and 'text', and assign corresponding values
            data_dict = {'Title': name_item.title(), 'Text': text_item}

            # Append the created dictionary to the 'data' list
            legal_documents.append(data_dict)

        return legal_documents

    @ staticmethod
    def load_from_dataframe(df: pd.DataFrame) -> List[str]:
        """
        Load legal documents from a Pandas DataFrame.

        :param df: The DataFrame containing the legal documents.
        :return: List of strings, where each string represents the text content of a legal document.
        """
        # TODO: Implement the logic to extract the text content from the DataFrame
        # and return a list of strings

        df = df
        pass
