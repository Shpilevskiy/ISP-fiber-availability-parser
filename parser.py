# coding: utf8
from __future__ import print_function, unicode_literals

from bs4 import BeautifulSoup as bs
import requests
import re


class ByflyIsXponParser(object):
    PARSER_URL = 'http://byfly.by'
    STREET = u'Либкнехта'
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

        rows = soup.find_all('tr', class_=re.compile(r"(odd|even)"))
        result = [self._street_connection_data(r) for r in rows]
        return result

    def _street_connection_data(self, street_row):
        status_data = {}

        for k, v in self.FIELD_CLASS_MAP.items():
            el = street_row.find('td', class_=v)
            status_data[k] = el.text.strip()
        return status_data


def main():
    parser = ByflyIsXponParser()
    # parser.get_result_dict()
    street_avail_data = parser.check_street(u"Либкнехта")
    for s in street_avail_data:
        if s["status"] == parser.XPON_COME_SOON:
            print("{}, {} - {}".format(s["street"], s["number"],
                  parser.XPON_COME_SOON))

if __name__ == '__main__':
    main()
