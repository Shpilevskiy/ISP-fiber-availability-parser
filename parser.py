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
        'http://www.byfly.by/gPON-spisok-domov?field_obl_x_value_many_to_one=6&field_street_x_value=&field_ulica_x_value=%s&field_number_x_value=&field_sostoynie_x_value_many_to_one=All' % (
            STREET))

    def get_result_dict(self):
        r = requests.get(self.XPON_CHECK_URL)
        soup = bs(r.text, 'html.parser')
        # Need to parse all pagination
        data = soup.find_all('td', class_='views-field')
        data = self.__clean_data(str(data))
        data = data.split('\n')
        result = [[{"region": data[a].strip(), "city": data[a+1].strip(), "street": data[a+2].strip(), "house": data[a+3].strip(), "status": data[a+4].strip()}] for a in range(1, len(data), 5)]
        for lis in result:
            for dic in lis:
                if dic['status'] == self.XPON_COME_SOON:
                    print(dic['status'])

    def __clean_data(self, data):
        res = data
        res = res.replace(',', '')
        res = res.replace('  ', '')
        res = res.replace('[', '')
        res = res.replace(']', '')
        res = re.sub(r'(\<(/?[^\>]+)\>)', r'', res)
        return res


def main():
    parser = ByflyIsXponParser()
    parser.get_result_dict()

if __name__ == '__main__':
    main()
