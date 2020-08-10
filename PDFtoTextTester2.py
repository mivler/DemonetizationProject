"""
Author: Matthew Ivler
Takes a pdf and turns it into text file via tesseract OCR software (Note: This code is not optimized for runtime 
and tesseract is slow.
"""
import pytesseract as tess
import PIL
from pdf2image import convert_from_path
import os


def pdf_to_image(pdf_name, temp_file_name):
    """
    Takes a pdf and turns it into a jpg that can be read by tesseract.
    :param pdf_name: str- path to the pdf being converted
    :param temp_file_name: str- place to store image pages separately
    :return: lst- list of jpg file names each representing a page of the original pdf
    """
    # Creates a list of pages
    pages = convert_from_path(pdf_name)

    # Variable initialization
    page_number = 1
    file_name_list = []

    # Goes through pages to create a temporary JPEG file for each pdf page
    for page in pages:
        file_name = temp_file_name + str(page_number) + ".jpg"
        # Page is a PIL image type and save is a PIL function
        page.save(file_name, "JPEG")
        page_number = page_number + 1
        file_name_list.append(file_name)
    return file_name_list


def tesseract_pdf_reader(file_list, temp_file_name):
    """
    Turns a list of pdfs into a set of text documents by the same name.
    :param file_list: lst- list of pdf file names/paths for files that will be converted to text
    :param temp_file_name: str- the temporary_file_name used to create the jpgs
    :return: None
    """
    # Sets max pages for temp_file deletion later
    max_page_count = 0

    # Sets tesseract path (requires tesseract download on running machine)
    tess.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    for elem in file_list:
        # Counts pages in file
        page_count = 0
        # Creates outfile
        output = elem[:-3] + "txt"
        with open(output, "w") as out_file:

            # Turns pdf file into several temporary image files (1 per page)
            page_list = pdf_to_image(elem, temp_file_name)
            text = ""

            # Goes through image pages and converts from images to strings using Tesseract-OCR
            # Note: Due to OCR, small print, warped print, or non-english letters may be confused for other
            # letter. Poorly formatted documents also may have contact improperly read.
            for page in page_list:
                page_count += 1
                text = text + tess.image_to_string(page)
                text = text.replace("-\n", "")
            out_file.write(text)
        if page_count > max_page_count:
            max_page_count = page_count
        print("TEXT CONVERSION DONE: " + elem)

    # Erase temporary files
    for i in range(1, max_page_count + 1):
        os.remove(temp_file_name + str(i) + ".jpg")


def main():
    tesseract_pdf_reader([], "temp_image_file")


if __name__ == "__main__":
    main()
