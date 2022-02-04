from app.recipe import get_recipe_html, get_ingredients, create_pdf, get_instructions, get_recipe_name, download_picture


def main():
    html = get_recipe_html("https://www.browneyedbaker.com/chipotle-cilantro-lime-rice/")
    # html = get_recipe_html("https://thebusybaker.ca/easy-one-pan-lentil-daal-curry/")
    ingredients = get_ingredients(html)
    instructions = get_instructions(html)
    name = get_recipe_name(html)
    download_picture(html)
    create_pdf(ingredients, instructions, pdf_name=name, recipe_name=name)



if __name__ == '__main__':
    main()