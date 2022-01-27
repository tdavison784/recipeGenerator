import logging
import requests
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def get_recipe_html(url):
    """Function that gets recipe from url and returns raw html"""

    resp = requests.get(url)
    if resp.status_code != 200:
        logging.info(f"GET request failed on url {url}, Error is: {resp.content}")

    return resp.text


def get_recipe_name(html):
    """Function that will get the recipe name from the html page"""

    soup = BeautifulSoup(html, "html.parser")
    data = soup.find("h2", attrs={"class": "wprm-recipe-name"})
    if data is None:
        data = soup.find("h2", attrs={"class": "wprm-recipe-name wprm-block-text-bold"})

    return data.text


def get_ingredients(html, *keywords):
    """Function that filters with the list of provided keywords
    and returns any found matches"""

    soup = BeautifulSoup(html, "html.parser")
    data = soup.find('ul', attrs={'class': "wprm-recipe-ingredients"})

    return data


def get_instructions(html):
    """Function that will get and return instructions"""

    soup = BeautifulSoup(html, "html.parser")
    data = soup.find("div", attrs={"class": "wprm-recipe-instruction-group"})

    return data.text.split(".")


def _get_picture_url(html):
    """Function that finds picture of the meal and returns the image urlt"""

    soup = BeautifulSoup(html, "html.parser")
    data = soup.find("div", attrs={"class": "wprm-recipe-image wprm-block-image-circle"})

    if data is None:
        data = soup.find("div", attrs={"class": "wprm-recipe-image wprm-block-image-normal"})
    return data.findChild("img")["data-lazy-src"]


def download_picture(html):
    url = _get_picture_url(html)
    resp = requests.get(url, stream=True)
    with open("img.png", "wb") as out_file:
        for chunk in resp.iter_content():
            out_file.write(chunk)
    out_file.close()

    del resp


def create_pdf(ingredients, instructions, pdf_name, recipe_name):

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
    for x in ingredients:
        text.textLine(x.text)

    text.setFont("Courier", 8)
    text.setFillColor(colors.black)
    text.textLine("Instructions:")
    for y in instructions:
        text.textLine(y)
    pdf.drawText(text)
    pdf.drawInlineImage(image, 3, 10)

    pdf.save()
