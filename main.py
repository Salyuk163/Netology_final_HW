import json
import requests
import urllib.parse
import datetime
from tqdm import tqdm


with open('my_token.txt') as file:
    VK_TOKEN = file.readline().strip()
    YX_TOKEN = file.readline().strip()


class UserVK:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_photo(self, quantity_photo=5):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': 'profile', 'extended': '1'}
        response = requests.get(url, params={**self.params, **params})
        if response.status_code != 200:
            return print(f"Ошибка {response.status_code}! Выполнение невозможно!")
        else:
            count = response.json()['response']['count']
            name_info = []
            json_info = []
            photo_info = []
            while count != 0:
                count -= 1
                likes = response.json()['response']['items'][count]['likes']['count']
                photo_name = f'{likes}.jpg'
                photo_url = response.json()['response']['items'][count]['sizes'][-1]['url']
                date = response.json()['response']['items'][count]['date']
                pub_date = datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d')
                size = response.json()['response']['items'][count]['sizes'][-1]['type']
                if len(name_info) == quantity_photo:
                    break
                else:
                    if photo_name in name_info:
                        photo_name = f'{likes}({pub_date}).jpg'
                        name_info.append(photo_name)
                        json_info.append({"file_name": photo_name, "size": size})
                        photo_info.append({photo_name: photo_url})
                    else:
                        name_info.append(photo_name)
                        json_info.append({"file_name": photo_name, "size": size})
                        photo_info.append({photo_name: photo_url})
                with open("info.json", 'w') as j_file:
                    j_file.write(json.dumps(json_info))
            return photo_info


class YaDiskUser:

    def __init__(self, access_token):
        self.token = access_token
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                        'Authorization': f'OAuth {self.token}'}

    def create_path(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources?'
        path_name = input('Введите название папки: ')
        query = {'path': f'{path_name}'}
        response = requests.put(url + urllib.parse.urlencode(query), headers=self.headers)
        if response.status_code == 201:
            return path_name
        else:
            return print(f"Ошибка {response.status_code}! Выполнение невозможно!")

    def upload_photo(self, path_name, photo_info):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload?'
        pbar = tqdm(total=len(photo_info), desc='Загрузка фото',  bar_format='{desc}: {n_fmt}%')
        for element in photo_info:
            for name in element:
                photo_name = name
                photo_url = element[name]
                query = {'path': f'{path_name}/{photo_name}', 'url': photo_url}
                response = requests.post(url + urllib.parse.urlencode(query), headers=self.headers)
                if response.status_code == 202:
                    pbar.update(100 / len(photo_info))
                else:
                    print(f'Ошибка {response.status_code}! Фотография {photo_name} не загружена!')


def main():
    id_vk = input('Введите ID пользователя ВК: ')
    vk_user = UserVK(VK_TOKEN, id_vk)
    yandex_user = YaDiskUser(YX_TOKEN)
    path_name = yandex_user.create_path()
    photo_upload = vk_user.get_photo()
    yandex_user.upload_photo(path_name, photo_upload)


if __name__ == '__main__':
    main()
