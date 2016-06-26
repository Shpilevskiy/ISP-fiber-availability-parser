# coding: utf8
from __future__ import print_function, unicode_literals

import argparse
import re

import requests
from bs4 import BeautifulSoup as bs


class ByflyIsXponParser(object):
    PARSER_URL = "http://byfly.by{}"
    XPON_COME_SOON = u"Переключение на технологию xPON планируется в ближайшее время"
    XPON_AVAILABLE = u"Техническая возможность подключения по технологии xPON имеется"
    XPON_CHECK_URL = (
        "http://www.byfly.by/gPON-spisok-domov?field_obl_x_value_many_to_one={}&field_street_x_value={}&"
        "field_ulica_x_value={}&field_number_x_value={}&field_sostoynie_x_value_many_to_one=All"
    )

    REGIONS_MAP = {
        "Брестская": "0",
        "Витебская": "1",
        "Гомельская": "2",
        "Гродненская": "3",
        "Минская": "4",
        "Могилевская": "5",
        "Минск": "6"
    }

    FIELD_CLASS_MAP = {
        "region": "views-field-field-obl-x-value",
        "city": "views-field views-field-field-street-x-value",
        "street": "views-field-field-ulica-x-value",
        "number": "views-field-field-number-x-value",
        "status": "views-field-field-sostoynie-x-value",
    }

    def __init__(self, region=u"Минск", city=u"",
                 street_name=u"", number=u""):
        self.result = self.check_street(region=region, city=city,
                                        street_name=street_name, number=number)

    def check_street(self, region=u"Минск", city=u"",
                     street_name=u"", number=u""):
        r = requests.get(self.XPON_CHECK_URL.format(self.REGIONS_MAP[region],
                                                    city,
                                                    street_name,
                                                    number))
        soup = bs(r.text, "html.parser")

        self.result = []
        while True:
            rows = soup.find_all("tr", class_=re.compile(r"(odd|even)"))
            self.result += [self._street_connection_data(r) for r in rows]
            next_page_link = soup.find("a", title=u"На следующую страницу", href=True)
            if not next_page_link:
                break
            next_r = requests.get(self.PARSER_URL.format(next_page_link["href"]))
            soup = bs(next_r.text, "html.parser")
        return self.result

    def _street_connection_data(self, street_row):
        status_data = {}
        for k, v in self.FIELD_CLASS_MAP.items():
            el = street_row.find("td", class_=v)
            status_data[k] = el.text.strip()
        return status_data


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('street',
                        help=u"Имя улицы, для которой необходимо проверить наличие подключения.")
    parser.add_argument('--number', '-n',
                        help=u"Номер дома, для которого необходимо проверить подключение.",
                        default=""
                        )
    return parser.parse_args()


def print_result(results):
    for s in results:
        print("{} {} - {}".format(s["street"], s["number"],
                                  s["status"]))


def main():
    args = parse_args()
    parser = ByflyIsXponParser(region=u"Минск",
                               street_name=args.street,
                               number=args.number)
    print_result(parser.result)

    print_result(parser.check_street(street_name="Алибегова"))


if __name__ == "__main__":
    main()
