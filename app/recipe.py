import logging
import requests
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def get_recipe_html(url) -> str:
    """Function to get recipe from url endpoint
    and return raw html
    :param url: url endpoint to recipe site.
    :return str"""

    resp = requests.get(url)
    if resp.status_code != 200:
        logging.info(f"GET request failed on url {url}, Error is: {resp.content}")

    return resp.text


def get_recipe_name(html) -> str:
    """Function to get recipe name
    from html string and return the name for
    use in the pdf creation.

    :param html: html str to be passed into bs4
    :return str"""

    soup = BeautifulSoup(html, "html.parser")
    data = soup.find("h2", attrs={"class": "wprm-recipe-name"})
    if data is None:
        data = soup.find("h2", attrs={"class": "wprm-recipe-name wprm-block-text-bold"})

    return data.text


def get_ingredients(html):
    """Function that filters through html
    and returns ingredients list.
    :param html: html string to be parsed by bs4
    :return bs4.element.Tag"""

    soup = BeautifulSoup(html, "html.parser")
    data = soup.find('ul', attrs={'class': "wprm-recipe-ingredients"})

    return data


def get_instructions(html) -> list:
    """Function that will cooking instructions
    from html and return them in a list.
    :param html: html string to be parsed by bs4
    :return list"""

    soup = BeautifulSoup(html, "html.parser")
    data = soup.find("div", attrs={"class": "wprm-recipe-instruction-group"})

    return data.text.split(".")


def _get_picture_url(html) -> str:
    """Function that finds picture of the meal and returns the image url
    :param html: html string to be parsed by bs4
    :return str"""

    soup = BeautifulSoup(html, "html.parser")
    data = soup.find("div", attrs={"class": "wprm-recipe-image wprm-block-image-circle"})

    if data is None:
        data = soup.find("div", attrs={"class": "wprm-recipe-image wprm-block-image-normal"})
    return data.findChild("img")["data-lazy-src"]


def download_picture(html) -> None:
    """Function that will download picture
    for local reference to paint into pdf
    :param html: html string to be parsed by bs4
    :return None"""
    url = _get_picture_url(html)
    resp = requests.get(url, stream=True)
    with open("img.png", "wb") as out_file:
        for chunk in resp.iter_content():
            out_file.write(chunk)
    out_file.close()
    del resp


def create_pdf(ingredients, instructions, pdf_name, recipe_name) -> None:
    """Function to create the pdf file of the online recipe.
    :param ingredients: bs4.elementTag
    :param instructions: list<str>
    :param pdf_name: str
    :param recipe_name: str
    :return None
    """

    image = "img.png"
    doc_title = "Recipe"
    pdf = canvas.Canvas(f"{pdf_name}.pdf")
    pdf.setTitle(doc_title)

    pdf.setFont('Courier', 25)
    pdf.drawCentredString(300, 770, recipe_name)

    #draw line
    pdf.line(30, 710, 550, 710)
    text = pdf.beginText(40, 680)
    text.setFont("Courier", 12)
    text.setFillColor(colors.black)
    text.textLine("Ingredients:")
    text.setFont("Courier", 10)
    text.setFillColor(colors.black)

    for x in ingredients:
        text.textLine(x.text)

    text.setFont("Courier", 12)
    text.setFillColor(colors.black)
    text.textLine("Instructions:")
    text.setFont("Courier", 10)

    text.setFillColor(colors.black)
    for y in instructions:
        if len(y) > 100:
            begin = y[:90]
            end = y[90:]
            text.textLine(begin)
            text.textLine(end)
        else:
            text.textLine(y)
    pdf.drawText(text)
    pdf.drawInlineImage(image, 3, 10)

    pdf.save()
