import datetime
import time

import requests
from bs4 import BeautifulSoup


def scrape_curseforge_individual_mod(url: str, cookie: str, output_file_name="individual_mod_data.csv",
                                     file_mode="w+", retry_time=3) -> None:
    """
    Scrapes a specific minecraft mod information from curseforge.com. The scraper takes in the link to the mod and a
    cookie to bypass cloudflare and writes the data to a csv file.

    :param url: link to the mod
    :param cookie: user cookie
    :param output_file_name: name of the output file (defaults to "individual_mod_data.csv")
    :param file_mode: file mode to write the output file ("w+" for overwrite, "a" for append, defaults to "w+")
    :param retry_time: amount of time before requesting to the server again (defaults to 3 seconds)
    :return: None
    """

    def log(message: str) -> None:
        print(f"[{datetime.datetime.now()}] {message}")

    with open(output_file_name, file_mode) as output_file:
        if 'w' in file_mode:
            output_file.write("mod_name,author_name(s),downloads,last_updated,game_version,project_id,date_created,"
                              "license,categories\n")

        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/92.0.4515.107 "
                          "Safari/537.36",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.9", 'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7', 'Cache-Control': 'max-age=0', 'Cookie': cookie,
            'Sec-Ch-Ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'Referer': f'https://www.curseforge.com/minecraft/mc-mods',
            'Upgrade-Insecure-Requests': '1'}

        html_text = ""
        while True:
            try:
                request = requests.get(url, headers=headers)
                log(f"Request Result: {request}.")
                if "200" not in str(request):
                    raise ConnectionError

                html_text = request.text
                log(f"Request was accepted.")
                break
            except:
                log(f"Request failed. Retrying in {retry_time} seconds...")
                time.sleep(retry_time)

        soup = BeautifulSoup(html_text, "lxml")

        mod_name = soup.find("h2", class_="font-bold text-lg break-all").text.replace('"', "'")

        categories = []
        for tag in soup.findAll("figure", class_="relative h-6 w-6"):
            category = tag["title"].replace('"', "'")
            categories.append(f'{category}')

        authors = soup.findAll("div", class_="flex flex-col flex-grow")
        author_roles = soup.findAll("p", class_="text-xs")
        author_names = []
        author_links = []

        for i, author in enumerate(authors):
            author_name = author.find('span').text.replace('"', "'").replace("  ", "").replace("\r\n", "")
            author_role = author_roles[i].text.replace('"', "'")

            author_names.append(f'{author_name}:{author_role}')
            author_links.append(f"{author.find('a')['href']}")

        downloads = soup.find("span", class_="mr-2 text-sm text-gray-500").text

        last_updated = soup.find("span", class_="mr-2 text-gray-500").find("abbr").text

        created_date = f'{soup.find("div", class_="flex flex-col mb-3").find("abbr", class_ = "tip standard-date standard-datetime").text}'.replace("\n", "").replace("  ", "")

        project_id = soup.findAll("div", class_="w-full flex justify-between")[0].findAll("span")[1].text

        mod_license = soup.find("a", rel="modal:open").text.replace("\r\n", "").replace("  ", "")

        game_version = soup.findAll("span", class_="text-gray-500")[2].text
        game_version = game_version.split(":")[1].replace(" ", "")

        output_file.write(f'"{mod_name}",')
        output_file.write(f'"{author_names}",')
        output_file.write(f'"{downloads}",')
        output_file.write(f'"{last_updated}",')
        output_file.write(f"{game_version},")
        output_file.write(f"{project_id},")
        output_file.write(f'"{created_date}",')
        output_file.write(f'"{mod_license}",')
        output_file.write(f'"{categories}"\n')

        log(f'"{mod_name}" has been written to "{output_file_name}."')


def scrape_curseforge_modpages(cookie: str, start_page=1, end_page=1241, rest_time=2,
                               output_file_name="curseforge_mods_data.csv", file_mode="w+") -> None:
    """
    Scrapes general minecraft mod information by page number from curseforge.com. The scraper takes in a cookie to
    bypass cloudflare and writes the data to a csv file.

    :param cookie: user cookie
    :param start_page: first page to be scraped (defaults to 1)
    :param end_page: last page to be scraped (defaults to 1241)
    :param rest_time: amount of time before the scrape requests the next page (defaults to 2 secs)
    :param output_file_name: name of the data file (defaults to "curseforge_mods_data.csv")
    :param file_mode: file mode to write the output file ("w+" for overwrite, "a" for append)
    :return: None
    """

    def log(message: str) -> None:
        print(f"[{datetime.datetime.now()}] {message}")

    with open(output_file_name, file_mode) as output_file:

        if 'w' in file_mode:
            output_file.write("mod_name,author_name,downloads,last_updated,description,page_link,author_link,"
                              "page_number\n")

        for page_index in range(start_page, end_page + 1):
            log(f"Page {page_index} started.")

            url = f"https://www.curseforge.com/minecraft/mc-mods?page={page_index}"
            headers = {
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/92.0.4515.107 "
                              "Safari/537.36",
                'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                          "*/*;q=0.8,"
                          "application/signed-exchange;v=b3;q=0.9",
                'Accept-Encoding': "gzip, deflate, br",
                'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'Cache-Control': 'max-age=0',
                'Cookie': cookie,
                'Sec-Ch-Ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                'Referer': f'https://www.curseforge.com/minecraft/mc-mods?page={page_index - 1}',
                'Upgrade-Insecure-Requests': '1'
            }

            html_text = ""
            while True:
                try:
                    request = requests.get(url, headers=headers)
                    log(f"Request Result: {request}.")
                    if "200" not in str(request):
                        raise ConnectionError

                    html_text = request.text
                    log(f"Request for page {page_index} was accepted.")
                    break
                except:
                    log(f"Request to page {page_index} failed. Retrying in {rest_time} seconds...")
                    time.sleep(rest_time)

            soup = BeautifulSoup(html_text, "lxml")

            mods = soup.find("div", class_="flex flex-col").find_all("div", class_="my-2")

            for i, mod in enumerate(mods):
                mod_name = mod.h3.text.replace('"', "'")  # name of the mod
                author_name = mod.find("div", class_="flex items-end lg:hidden").find("a", class_="font-bold hover:no-underline").text.replace('"', "'")
                details = mod.find_all("span", class_="mr-2 text-xs text-gray-500")
                description = mod.find("p", class_="text-sm leading-snug").text.replace("  ", "").replace("\r\n", "").replace('"', "'")
                page_link = mod.find("a", class_="my-auto")["href"]

                author_link = ""
                try:
                    author_link = mod.find("div", class_="flex items-end lg:hidden").find("a", class_="font-bold hover:no-underline")["href"]
                except:
                    pass

                output_file.write(f'"{mod_name}",')

                output_file.write(f'"{author_name}",')

                for info in details:
                    formatted_info = info.text.replace("  ", "").replace("\r\n", " ")
                    output_file.write(f'"{formatted_info}",')

                output_file.write(f'"{description}",')

                output_file.write(f'"https://www.curseforge.com{page_link}",')

                output_file.write(f'"https://www.curseforge.com{author_link}",')

                output_file.write(f"{page_index}\n")

                log(f"Mod #{i + 1} on page {page_index} has been written to disk.")

            if page_index != end_page:
                log(f"Page {page_index} completed, sleeping for {rest_time} seconds.\n")
                time.sleep(rest_time)

    log("All pages completed.")
