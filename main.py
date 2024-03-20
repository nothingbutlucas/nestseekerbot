import os
import cloudscraper
from bs4 import BeautifulSoup
from hashlib import sha1
from urllib.parse import urlparse
from dataclasses import dataclass
from time import sleep
import random
import logging

scraper = cloudscraper.create_scraper()

TOKEN = os.environ.get("TOKEN", "")
room = os.environ.get("ROOM", "")
horas = os.environ.get("HORAS", 3)
logging_level = os.environ.get("LOGGING_LEVEL", "INFO")
minutos = int(horas) * 60

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S %p",
    level=logging.getLevelName(logging_level),
)

log = logging


@dataclass
class Parser:
    website: str
    link_regex: str

    def extract_links(self, contents: str):
        """Esta función extrae los elementos de las paginas para poder obtener los links a las publicaciones"""
        soup = BeautifulSoup(contents, "html.parser")
        log.debug(soup)
        ads = soup.select(self.link_regex)
        log.debug("=" * 50)
        log.debug(ads)

        for ad in ads:
            href_string = (
                "href"  # Usamos href porque los sitios suelen usar href, menos zonaprop
            )
            if self.website == "https://www.zonaprop.com.ar":
                href_string = "data-to-posting"
            href = str(ad[href_string])
            log.debug(href)
            if self.website == "https://inmuebles.mercadolibre.com.ar":
                # Y en este caso mercadolibre jode la url, asique la parseamos para poder armar el hash
                href_para_id = href.split("/")[-1].split("#")[0]
                # Este id es el que luego guardamos en un txt para ver si ya vimos o no el sitio
                _id = sha1(href_para_id.encode("utf-8")).hexdigest()
                yield {"id": _id, "url": href}
            else:
                _id = sha1(href.encode("utf-8")).hexdigest()
                yield {"id": _id, "url": "{}{}".format(self.website, href)}


# Acá se definen los sitios que queremos mirar y como llegar al lugar donde esta la url de la publicación
# Creo que se entiende, pero por las dudas:
# Cada parser define el dominio principal del sitio y el regex que hay que hacer para ir a buscar la property donde esta el link a la publicación
# Cada pagina hace lo que quiere acá, asique probablemente esto haya que ir actualizandolo a medida que vayan implementando cambios

parsers = [
    Parser(
        website="https://www.argenprop.com",
        link_regex="div.listing__items div.listing__item a",
    ),
    Parser(
        website="https://www.zonaprop.com.ar",
        link_regex="div.postings-container div.sc-1tt2vbg-3 div.sc-i1odl-0",
    ),
    Parser(
        website="https://inmuebles.mercadolibre.com.ar",
        link_regex="section.ui-search-results ol.ui-search-layout div.ui-search-item__group a",
    ),
]


def main():
    """Ejecución main del bot"""
    urls = read_txt("sitios.txt")
    api_calls = 0
    for url in urls:
        if "https://" in url or "http://" in url:
            sitio = url.split(".com")[0].split("/")[-1].split(".")[1]
            logging.info("Mirando {} ...".format(sitio))
            try:
                res = scraper.get(url)
            except Exception as e:
                logging.error("Error al mirar {}".format(sitio))
                logging.error(e)
                continue
            logging.debug(res)
            ads = list(extract_ads(url, res.text))
            logging.debug(ads)

            seen, unseen = split_seen_and_unseen(ads)

            logging.info("{} vistos, {} no vistos".format(len(seen), len(unseen)))

            for post in unseen:
                if not skips_url(post):
                    api_calls += 1
                    if api_calls == 20:
                        # Durmiendo para no saturar la api de telegram -> Limite de 20 mensajes en 1 minuto
                        api_calls = 0
                        logging.info("Durmiendo para no saturar la api de telegram")
                        random_sleep(60)
                    notify(post)

            mark_as_seen(unseen)
            logging.info("Durmiendo entre sitio y sitio")
            random_sleep(30)
        else:
            logging.debug(
                f"No miramos '{url}', porque probablemente no sea un sitio. En caso de que lo sea, ponele el http:// o https://"
            )


def random_sleep(seconds):
    """Sleeps sort of a random time, but close to the seconds provided. This is to avoid the firewall blocking of the servers"""
    random_seconds = seconds + random.randint(seconds - 6, seconds + 9)
    logging.debug(f"Durmiendo {random_seconds} segundos")
    sleep(random_seconds)


def read_txt(file_to_read):
    try:
        with open(file_to_read, "r") as file:
            lines = file.read().splitlines()
        return lines
    except FileNotFoundError:
        logging.error(
            f"No se encontro el archivo {file_to_read}. Para solucionar este problema crea el archivo."
        )
        exit(1)


def extract_ads(url, text):
    """Extrae los links de las publicaciones"""
    uri = urlparse(url)
    logging.debug(uri)
    logging.debug(uri.hostname)
    parser = next(p for p in parsers if uri.hostname in p.website)
    logging.debug(parser)
    return parser.extract_links(text)


def split_seen_and_unseen(ads):
    """Separamos los vistos y los no vistos"""
    history = read_txt("seen.txt")
    logging.debug(f"Historial obtenido: \n{history}")
    seen = [a for a in ads if a["id"] in history]
    unseen = [a for a in ads if a["id"] not in history]
    logging.debug(f"Vistos: \n{ seen }")
    logging.debug(f"No vistos: { unseen }")
    return seen, unseen


def notify(ad):
    """Notificamos a los usuarios en el grupo de telegram"""
    frases = read_txt("frases.txt")
    texto = f'{str(random.choice(frases))}\n{ad["url"]}'
    bot = TOKEN
    url = f"https://api.telegram.org/bot{bot}/sendMessage?chat_id={room}&text={texto}"
    scraper.get(url)


def mark_as_seen(unseens):
    with open("seen.txt", "a+") as f:
        for unseen in unseens:
            format_unseen = f"{unseen['id']}\n"
            f.write(format_unseen)


def skips_url(post):
    url = post["url"]
    # Verificar si denylist.txt existe
    if os.path.exists("denylist.txt"):
        for word in read_txt("denylist.txt"):
            if word in url:
                logging.info("No miramos '{}'".format(url))
                return True
    return False


while __name__ == "__main__":
    main()
    logging.info(f"Esperando {minutos} minutos, osea {horas} horas")
    for x in range(1, minutos):
        random_sleep(60)
        logging.debug(f"Faltan {minutos -x} minutos")
