import requests
import math
import sys
import os
from PyQt5.QtCore import QBasicTimer, Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow,\
    QLabel, QLineEdit, QComboBox, QCheckBox


class MyProject(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 150, 800, 500)
        self.setWindowTitle('Большая задача по Maps API. Часть №12')

        self.timer = QBasicTimer()
        self.timer.start(60, self)

        self.map_server = 'http://static-maps.yandex.ru/1.x/'
        self.geocode_server = 'https://geocode-maps.yandex.ru/1.x'
        self.organization_server = 'https://search-maps.yandex.ru/v1/'

        self.geocode_key = '40d1649f-0493-4b70-98ba-98533de7710b'
        self.organization_key = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'

        self.lon, self.lat = None, None
        self.old_lon, self.old_lat = None, None
        self.spn = 0.1
        self.map = 'map'
        self.motion = None
        self.postal_code = False
        self.postal_info = 'не найдено'
        self.old_address = None

        self.push_mouse_left = False
        self.push_mouse_right = False
        self.name_file = 'map.png'
        self.update = True

        self.mode_map = {
            'Схема': 'map',
            'Спутник': 'sat',
            'Гибрид': 'sat,skl'
        }

        self.image = QLabel(self)
        self.image.move(200, 0)
        self.image.resize(600, 500)

        self.title_coordinates = QLabel('Укажите адрес: ', self)
        self.title_coordinates.resize(200, 30)
        self.title_coordinates.move(0, 15)
        self.title_coordinates.setFont(QFont("Bold", 14))
        self.title_coordinates.setAlignment(Qt.AlignCenter)

        self.coordinates = QLineEdit(self)
        self.coordinates.setText('Москва')
        self.coordinates.resize(180, 25)
        self.coordinates.move(10, 60)
        font = QFont()
        font.setPointSize(10)
        self.coordinates.setFont(font)
        self.coordinates.setFocus()
        self.mouseReleaseEvent = self.focus

        self.title_map = QLabel('Вид карты: ', self)
        self.title_map.resize(200, 30)
        self.title_map.move(0, 110)
        self.title_map.setFont(QFont("Bold", 14))
        self.title_map.setAlignment(Qt.AlignCenter)

        self.comboBox_cities = QComboBox(self)
        self.comboBox_cities.move(10, 150)
        self.comboBox_cities.resize(180, 25)
        self.comboBox_cities.addItems(['Схема', 'Спутник', 'Гибрид'])

        self.search = QPushButton('Поиск', self)
        self.search.resize(140, 30)
        self.search.move(30, 195)
        self.search.clicked.connect(self.change_ll)

        self.address_obj = QLabel('Адрес объекта: ', self)
        self.address_obj.resize(200, 30)
        self.address_obj.move(0, 250)
        self.address_obj.setFont(QFont("Bold", 14))
        self.address_obj.setAlignment(Qt.AlignCenter)

        self.checkbox = QCheckBox("Почтовый индекс", self)
        self.checkbox.resize(200, 20)
        self.checkbox.move(10, 290)
        self.checkbox.clicked.connect(self.do_post_code)

        self.name_obj = QLineEdit(self)
        self.name_obj.resize(180, 25)
        self.name_obj.move(10, 325)

        self.reset = QPushButton('Сброс поискового результата', self)
        self.reset.resize(180, 30)
        self.reset.move(10, 370)
        self.reset.clicked.connect(self.change_ll)

        self.change_ll()

    def do_post_code(self, state):
        if state:
            self.name_obj.setText(self.name_obj.text() + self.postal_info)
        else:
            self.name_obj.setText(', '.join(self.name_obj.text().split(', ')[:-1]))

    def change_ll(self, new_lon=None, new_lat=None, mouse=None):
        try:
            self.old_lon, self.old_lat = self.lon, self.lat
            if not mouse:
                self.lon, self.lat = self.get_coordinates(self.coordinates.text())
            elif mouse == 'left':
                self.lon, self.lat = new_lon, new_lat
                self.get_coordinates(f'{self.lon},{self.lat}')
            elif mouse == 'right':
                self.get_coordinates(f'{new_lon},{new_lat}')
                self.get_organization(new_lon, new_lat)
                return
        except ValueError:
            self.coordinates.setText('Ошибка...')
        else:
            try:
                if self.sender().text() == self.reset.text():
                    self.motion = None
                    self.name_obj.clear()
                    self.checkbox.setChecked(False)
                else:
                    self.motion = f'{self.lon},{self.lat},pm2dbm'
            except AttributeError:
                self.motion = f'{self.lon},{self.lat},pm2dbm'

            self.change_map(self.lon, self.lat, show=True)

    def change_map(self, new_lon, new_lat, show=False):
        st_lon, st_lat = self.lon, self.lat
        self.lon = new_lon
        self.lat = new_lat
        try:
            self.get_map()
            self.update = True
        except ValueError:
            self.lon, self.lat = st_lon, st_lat
            if show:
                self.coordinates.setText('Ошибка...')

    def get_coordinates(self, address_or_coordinates):
        geocode_params = {
            'apikey': self.geocode_key,
            'geocode': address_or_coordinates,
            'format': 'json'
        }
        response = requests.get(self.geocode_server, params=geocode_params)

        if not response:
            raise ValueError

        json_response = response.json()
        try:
            toponym = json_response['response']['GeoObjectCollection'][
                'featureMember'][0]['GeoObject']
            coordinates = toponym['Point']['pos']
            full_address = toponym['metaDataProperty']['GeocoderMetaData']['text']
            try:
                post_code = json_response['response']['GeoObjectCollection'][
                    'featureMember'][0]['GeoObject']['metaDataProperty'][
                    'GeocoderMetaData']['Address']['postal_code']
            except KeyError:
                post_code = 'не найден'
            self.postal_info = f', Почтовый индекс: {post_code}'
            if self.postal_code:
                full_address += f', Почтовый индекс: {post_code}'
            self.old_address = self.name_obj.text()
            self.name_obj.setText(full_address)
        except IndexError:
            raise ValueError

        lon_object, lat_object = map(float, coordinates.split())
        return lon_object, lat_object

    def get_organization(self, lon, lat):
        params = {
            'apikey': self.organization_key,
            'lang': 'ru_RU',
            'text': self.name_obj.text(),
            'type': 'biz',
            'll': f'{lon},{lat}',
            'spn': '1,1'
        }
        response = requests.get(self.organization_server, params=params)

        if not response:
            raise ValueError

        json_response = response.json()

        try:
            full_address = json_response['features'][0]['properties'][
                'CompanyMetaData']['address']
            coordinates = json_response['features'][0][
                'geometry']['coordinates']
            lon_org, lat_org = coordinates[0], coordinates[1]

            if self.lonlat_distance((lon, lat), (lon_org, lat_org)) <= 50:
                self.name_obj.setText(full_address)
            else:
                self.name_obj.setText(self.old_address)
        except IndexError:
            self.name_obj.setText(self.old_address)

    def get_map(self):
        maps = self.mode_map[self.comboBox_cities.currentText()]

        if self.push_mouse_left:
            self.lon, self.lat = self.old_lon, self.old_lat
            self.push_mouse_left = False

        map_params = {
            'll': f'{self.lon},{self.lat}',
            'spn': f'{self.spn},{self.spn}',
            'l': maps,
            'pt': self.motion
        }
        response = requests.get(self.map_server, map_params)

        if not response:
            raise ValueError

        with open(self.name_file, "wb") as file:
            file.write(response.content)

    def lonlat_distance(self, a, b):
        degree_to_meters_factor = 111 * 1000
        a_lon, a_lat = a
        b_lon, b_lat = b

        radians_lattitude = math.radians((a_lat + b_lat) / 2.)
        lat_lon_factor = math.cos(radians_lattitude)

        dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
        dy = abs(a_lat - b_lat) * degree_to_meters_factor

        distance = math.sqrt(dx * dx + dy * dy)

        return distance

    def focus(self, event):
        self.setFocus()

    def keyPressEvent(self, event):
        st_lon, st_lat = self.lon, self.lat
        if event.key() == Qt.Key_PageDown:
            if self.spn < 50:
                self.spn *= 2
        elif event.key() == Qt.Key_PageUp:
            if self.spn > 0.0001:
                self.spn /= 2
        elif event.key() == Qt.Key_Up:
            st_lat += self.spn * 1.5
        elif event.key() == Qt.Key_Down:
            st_lat -= self.spn * 1.5
        elif event.key() == Qt.Key_Right:
            st_lon += self.spn * 3
        elif event.key() == Qt.Key_Left:
            st_lon -= self.spn * 3

        self.change_map(st_lon, st_lat)

    def mousePressEvent(self, event):
        if event.button() in (Qt.LeftButton, Qt.RightButton):
            if 200 <= event.x() <= 800 and 25 <= event.y() <= 475:
                copy_lon, copy_lat = self.lon, self.lat
                x, y = event.x() - 200, event.y() - 25
                if x >= 300:
                    x -= 300
                    copy_lon += x / 145.5 * self.spn
                else:
                    x = -x % 300
                    copy_lon -= x / 145.5 * self.spn

                if y <= 225:
                    y = -y % 225
                    copy_lat += y / 257.5 * self.spn
                else:
                    y -= 225
                    copy_lat -= y / 257.5 * self.spn

                if event.button() == Qt.LeftButton:
                    self.push_mouse_left = True
                    self.change_ll(copy_lon, copy_lat, 'left')
                else:
                    self.push_mouse_right = True
                    self.change_ll(copy_lon, copy_lat, 'right')

    def timerEvent(self, event):
        if self.update:
            maps = QPixmap(self.name_file)
            self.image.setPixmap(maps)
            self.image.show()
            self.update = False

    def closeEvent(self, event):
        os.remove(self.name_file)

    def except_hook(self, cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyProject()
    form.show()
    sys.excepthook = form.except_hook
    sys.exit(app.exec())