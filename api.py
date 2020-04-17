import requests
from core.response_parser import parse_response
from bs4 import BeautifulSoup
from time import sleep


class Arguments:
    def __init__(self):
        self.payload = {
            "is_new_list": '1',
            "type": '1',
            "kind": '0',
            "searchtype": '1',
            "region": '1',
            "firstRow": "0"
        }

        self.url = "https://rent.591.com.tw/"
        self.second_to_sleep = 1

    def next_page(self):
        self.payload["firstRow"] = str(int(self.payload["firstRow"]) + 30)
# https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region=3


class RentingDog:
    def __init__(self):
        self.soup = None
        self.rent_objects_list = []

    def set_soup_from_url(self, url, payload, interval):
        cookies = {'urlJumpIp': payload['region']}
        print(f"sleep for {interval} seconds...")
        sleep(interval)
        response = requests.get(url, params=payload, cookies=cookies)
        print(f"request ===> {response.url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        self.soup = soup
        print(f"{soup.find('span', class_='TotalRecord').text.split()[1]} objects has been found base on your demands")

    def get_591_data(self):
        rent_objects = self.soup.find_all('ul', class_="listInfo clearfix")
        rent_objects_list = []
        for rent_object in rent_objects:
            rent_object_left = rent_object.find('li', class_="pull-left infoContent")
            price = rent_object.find('div', class_="price").text.split()
            rent_object_information = {
                "title": rent_object_left.a.text,
                "link": f"https:{rent_object_left.a.get('href')}",
                "price": f"{price[0]} {price[1]}"
            }

            details = rent_object_left.find_all('p')
            location_detail = details[0].text + details[1].text
            location_detail = location_detail.split()
            try:
                if location_detail[0] == '整層住家' and len(location_detail) == 8:
                    room_detail = {
                        "room_type": location_detail[0],
                        "room_format": location_detail[2],
                        "room_size": location_detail[4],
                        "room_floor": location_detail[6],
                        "room_address": location_detail[7]
                    }
                elif location_detail[0] == '整層住家':
                    room_detail = {
                        "room_type": location_detail[0],
                        "room_format": location_detail[2],
                        "room_size": location_detail[4],
                        "room_floor": location_detail[6],
                        "room_building": location_detail[7],
                        "room_address": location_detail[8]
                    }
                else:
                    room_detail = {
                        "room_type": location_detail[0],
                        "room_size": location_detail[2],
                        "room_floor": location_detail[4],
                        "room_address": location_detail[5]
                    }
                rent_object_information["room_detail"] = room_detail
                rent_objects_list.append(rent_object_information)
            except IndexError:
                print(f"detail can't be formatted {location_detail}")

        self.rent_objects_list += rent_objects_list
        return rent_objects_list


def display_rent_objects(object_list):
    for rent_object in object_list:
        print(rent_object)


if __name__ == '__main__':
    rd = RentingDog()
    arguments = Arguments()
    rd.set_soup_from_url(arguments.url, arguments.payload, arguments.second_to_sleep)
    rd.get_591_data()
    arguments.next_page()
    rd.set_soup_from_url(arguments.url, arguments.payload, arguments.second_to_sleep)
    rd.get_591_data()

    display_rent_objects(rd.rent_objects_list)
    print(len(rd.rent_objects_list))







