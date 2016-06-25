# coding: utf8
from __future__ import print_function, unicode_literals

from bs4 import BeautifulSoup as bs
import requests
import re


class ByflyIsXponParser(object):
    PARSER_URL = 'http://byfly.by{}'
    XPON_COME_SOON = u'Переключение на технологию xPON планируется в ближайшее время'
    XPON_AVAILABLE = u'Техническая возможность подключения по технологии xPON имеется'
    XPON_CHECK_URL = (
        'http://www.byfly.by/gPON-spisok-domov?field_obl_x_value_many_to_one=6&field_street_x_value=&field_ulica_x_value={}&field_number_x_value=&field_sostoynie_x_value_many_to_one=All'
    )

    FIELD_CLASS_MAP = {
        "region": "views-field-field-obl-x-value",
        "city": "views-field views-field-field-street-x-value",
        "street": "views-field-field-ulica-x-value",
        "number": "views-field-field-number-x-value",
        "status": "views-field-field-sostoynie-x-value",
    }

    def check_street(self, street_name):
        r = requests.get(self.XPON_CHECK_URL.format(street_name))
        soup = bs(r.text, 'html.parser')

        result = []
        while True:
            rows = soup.find_all('tr', class_=re.compile(r"(odd|even)"))
            result += [self._street_connection_data(r) for r in rows]
            if not soup.find('a', title=u"На следующую страницу", href=True):
                break
            next_page_link = soup.find('a', title=u"На следующую страницу", href=True)
            next_r = requests.get(self.PARSER_URL.format(next_page_link['href']))
            soup = bs(next_r.text, 'html.parser')
        return result

    def _street_connection_data(self, street_row):
        status_data = {}
        for k, v in self.FIELD_CLASS_MAP.items():
            el = street_row.find('td', class_=v)
            status_data[k] = el.text.strip()
        return status_data


def main():
    parser = ByflyIsXponParser()
    street_avail_data = parser.check_street(u"Либкнехта")
    for s in street_avail_data:
        if s["status"] == parser.XPON_COME_SOON:
            print("{}, {} - {}".format(s["street"], s["number"],
                                       parser.XPON_COME_SOON))

if __name__ == '__main__':
    main()
