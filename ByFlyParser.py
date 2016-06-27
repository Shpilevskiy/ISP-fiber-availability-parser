# coding: utf8
from __future__ import print_function, unicode_literals
from urllib.parse import urlparse, parse_qs

import argparse
import re

import requests, grequests
from bs4 import BeautifulSoup as bs


class ByflyIsXponParser(object):
    PARSER_URL = "http://byfly.by{}"
    XPON_COME_SOON = u"Переключение на технологию xPON планируется в ближайшее время"
    XPON_AVAILABLE = u"Техническая возможность подключения по технологии xPON имеется"
    XPON_CHECK_URL = (
        "http://www.byfly.by/gPON-spisok-domov?page={}&field_obl_x_value_many_to_one={}&field_street_x_value={}&"
        "field_ulica_x_value={}&field_number_x_value={}&field_sostoynie_x_value_many_to_one=All"
    )

    PAGE_STATEMENT = '0,0,0,0,0,0,0,0,0,0,{}'

    REGIONS_MAP = {
        "all": "All",
        "брестская": "0",
        "витебская": "1",
        "гомельская": "2",
        "гродненская": "3",
        "минская": "4",
        "могилевская": "5",
        "минск": "6"
    }

    FIELD_CLASS_MAP = {
        "region": "views-field-field-obl-x-value",
        "city": "views-field views-field-field-street-x-value",
        "street": "views-field-field-ulica-x-value",
        "number": "views-field-field-number-x-value",
        "status": "views-field-field-sostoynie-x-value",
    }

    def __init__(self):
        self.result = []

    def check_address(self, region=u"Минск", city=u"Минск",
                      street_name=u"", number=u""):

        links = self._get_pagination_pages_links(region=region, city=city, street_name=street_name, number=number)
        rs = (grequests.get(l) for l in links)
        results = grequests.map(rs)
        for response in results:
            soup = bs(response.text, "html.parser")
            rows = soup.find_all("tr", class_=re.compile(r"(odd|even)"))
            self.result += [self._street_connection_data(r) for r in rows]
        return self.result

    def _get_pagination_pages_links(self, region, city,
                                    street_name, number):

        default_link = self.XPON_CHECK_URL.format(self.PAGE_STATEMENT.format('0'),
                                                  self.REGIONS_MAP[region],
                                                  city,
                                                  street_name,
                                                  number)
        r = requests.get(default_link)
        soup = bs(r.text, "html.parser")
        last_page_link = soup.find("a", title=u"На последнюю страницу", href=True)
        if not last_page_link:
            return [default_link]
        args = parse_qs(urlparse(last_page_link['href']).query)
        page_args = args['page'][0]
        page_count = [i for i in page_args.split(',') if i.isdigit() and int(i)]
        page_count = int(str(page_count[0])) + 1
        pages_links = (self.XPON_CHECK_URL.format(self.PAGE_STATEMENT.format(str(i)),
                                                  self.REGIONS_MAP[region],
                                                  city,
                                                  street_name,
                                                  number)
                       for i in range(page_count))
        return pages_links

    def _street_connection_data(self, street_row):
        status_data = {}
        for k, v in self.FIELD_CLASS_MAP.items():
            el = street_row.find("td", class_=v)
            status_data[k] = el.text.strip()
        return status_data


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--street', '-s',
                        help=u"Имя улицы, для которой необходимо проверить наличие подключения.",
                        default="")
    parser.add_argument('--region', '-r',
                        help=u"Имя области для поиска. (all, Бресткая, Витебская и т.д.)",
                        default=u"Минск")
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
    parser = ByflyIsXponParser()
    parser.check_address(region=args.region.lower(),
                         street_name=args.street,
                         number=args.number)
    print_result(parser.result)


if __name__ == "__main__":
    main()
