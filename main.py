import sys
import html
import requests
import json
import re
import os
from PyQt5.QtWidgets import (QApplication, QTextEdit, QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QMessageBox, QFormLayout, QSpacerItem, QSizePolicy, QListWidget)
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from mega import Mega
from urllib.parse import parse_qs
from bs4 import BeautifulSoup

class DownloadThread(QThread):
    log_signal = pyqtSignal(str)
    download_complete_signal = pyqtSignal(str)

    def __init__(self, slug, selected_items):
        super().__init__()
        self.slug = slug
        self.selected_items = selected_items

    def run(self):
        global ep
        for item in self.selected_items:
            try:
                ep = item.data(Qt.UserRole)
                link = f'https://www3.animeflv.net/ver/{self.slug}-{ep}'
                url_list = self.get_url(link)

                # Intentar descargar desde mega
                download_success = self.download_from_mega(url_list[0], ep)

                if download_success:
                    self.print_log(f"{self.slug} - {ep} Was downloaded from Mega")
                else:
                    self.print_log(f"{self.slug} - {ep} Was not found in Mega!")

                    if "streamwish" in url_list[1]:
                        yu_id = url_list[2][url_list[2].find('embed/') + len('embed/'):].replace("'", "")
                        url_yu = self.check_yu(yu_id)
                        if url_yu:
                            cookie_value, params, name = self._get_sid_p_(url_yu)
                            self.download_you(cookie_value, params, name)
                        else:
                            sm_link = url_list[1].replace("/e/", "/f/") + "_h"
                            self.log_save(sm_link, self.slug, ep)
                    else:
                        yu_id = url_list[1][url_list[1].find('embed/') + len('embed/'):].replace("'", "")
                        url_yu = self.check_yu(yu_id)
                        if url_yu:
                            cookie_value, params, name = self._get_sid_p_(url_yu)
                            self.download_you(cookie_value, params, name)
                        else:
                            sm_link = url_list[2].replace("/e/", "/f/") + "_h"
                            self.log_save(sm_link, self.slug, ep)
            except:
                with open("download_L.log", "a+") as f:
                    f.write(f"Unable to find or download! -> {self.slug} - {ep}\n")
                    f.close()
                self.print_log(f"{self.slug} - {ep} Was unable to find or download! Skipping...")

    def print_log(self, text):
        self.log_signal.emit(text)
    def _get_sid_p_(self, url: str):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        title = soup.title.string
        name = title.split(".mp4")[0].split("Downloading ")[1]
        cookie_value = r.cookies.get('connect.sid')
        url = r.text[r.text.find('data-url="') + len('data-url="'):].split('" id="download"')[0]
        url = url.replace("&amp;", "&")
        params = parse_qs(url.split('?')[1])
        params = {key: value[0] for key, value in params.items()}
        return cookie_value, params, name
    
    def download_you(self, sid:str, parameters:dict, name: str):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        new_folder_name = slug
        new_folder_path = os.path.join(script_dir, new_folder_name)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        cookies = {
            'connect.sid': sid,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'https://www.yourupload.com/',
        }
        response = requests.get('https://www.yourupload.com/download', params=parameters, cookies=cookies, headers=headers, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('Content-Length', 0))
            with open(f"{slug}/{name}.mp4", "wb") as file:
                downloaded = 0 
                with open("download_L.log", "a+") as f:
                    f.write(f"{slug} - {ep} Download started...")
                    f.close()
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        self.print_log(f"\rDownloading... {percent:.2f}% completed\n")
            with open("download_L.log", "a+") as f:
                    f.write(f"\nFile succesfully downloaded as {name}.mp4\n")
            self.print_log(f"\nFile succesfully downloaded as {name}.mp4")
        else:
            with open("download_L.log", "a+") as f:
                    f.write(f"\nError al descargar el archivo. Status Code: {response.status_code}")
            self.print_log(f"Error al descargar el archivo. Status Code: {response.status_code}")
    def get_url(self, ep) -> list:
        url = ep
        try:
            r = requests.get(url)
            html = r.text
            html = html[html.find('var videos =') + len('var videos = '):]
            html = html[:html.find("//")]
            match = re.search(r'\{.*\}', html, re.DOTALL)
            json_str = match.group(0)
            data = json.loads(json_str)
            url_list_ = []
            for i in data['SUB']:
                url_list_.append(i['code'])
            return url_list_
        except Exception as e:
            self.log_signal.emit(f"Error fetching URLs: {str(e)}")
            return []  # Devolver una lista vacia en el error

    def download_from_mega(self, url, ep):
        url = url.replace("embed", "file")
        # Se usa la libreria mega para hacer un login anonimo y sin credenciales
        mega = Mega()
        m = mega.login() 

        try:
            # Se obtiene la informacion del archivo y asi tambien se verifica si existe
            file_info = m.get_public_url_info(url)
            with open("download_L.log", "a+") as f:
                self.print_log(f"{slug} - {ep} File found | The download has started: {file_info}")
                f.write(f"{slug} - {ep} File found | The download has started: {file_info}\n")
        except Exception as e:
            # print(e)
            return False
        try:
            # Ruta absoluta del script actual
            script_path = os.path.abspath(__file__)
            # Directorio donde se encuentra el script
            script_dir = os.path.dirname(script_path)
            
            # Nombre de la nueva carpeta o archivo que deseas crear
            new_folder_name = slug
            # Crear la ruta dentro del mismo directorio del script
            new_folder_path = os.path.join(script_dir, new_folder_name)
            
            # Crear la carpeta si no existe
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            
            
            file = m.download_url(url, new_folder_path)
        except Exception as e:
            pass
        return True

    def check_yu(self, id):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'es-ES,es;q=0.9',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        # Se hace requests a la url del servidor (esto llevaria a la pagina donde se reproduciria el video)
        response = requests.get(f'https://www.yourupload.com/watch/{id}', headers=headers)
        html = response.text
        # Se encuentra el boton de descarga
        html = html[:html.find('class="btn btn-success"')][::-1]
        html = html[:html.find('"=ferh')][::-1].replace('"', '')
        # Se llama a la url de descarga
        url = f"https://www.yourupload.com{html}"
        r = requests.get(url)
        html = r.text
        # Dentro de esta le tienes que dar a otro boton de descarga
        # Antes de llevarte a la pagina de descarga pasas por varios anuncios
        # Entonces simplemente se obtiene la url que hace href a la descarga
        html = html[html.find('<a href="#" data-url="') + len('<a href="#" data-url="'):]
        html = html[:html.find('"')]
        # Se define la url con el endpoint de descarga pero eliminando el "amp;"
        # El "amp;" es como un id, no se hace con los headers del href, la pagina te tira un 403
        url = f"https://www.yourupload.com{html}"
        url_conv = url.replace("amp;", "")
        r = requests.get(url_conv)
        if "bad hand off" in r.text:
            return url
        else:
            return None

    def log_save(self, url, slug, episode):
        with open("download_L.log", "a+") as f:
            f.write(f"{slug} - {episode} Download: {url}\n")
            self.log_signal.emit(f"{slug} - {episode} Download link saved in links.txt")

class AnimeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Anime Downloader')
        self.setGeometry(100, 100, 600, 400)
        
        # Set up layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Set up font
        font = QFont("Arial", 12)
        
        # Set up UI components con "dark" style
        self.prompt_input = QLineEdit(self)
        self.prompt_input.setPlaceholderText("Enter the prompt")
        self.prompt_input.setFont(font)
        self.prompt_input.setAlignment(Qt.AlignCenter)
        self.prompt_input.setStyleSheet("padding: 10px; border: 1px solid #6a0f91; border-radius: 5px; background-color: #2c003e; color: #e3d8f1;")
        self.layout.addWidget(self.prompt_input)

        self.search_button = QPushButton("Search", self)
        self.search_button.setFont(font)
        self.search_button.setStyleSheet("background-color: #6a0f91; color: #e3d8f1; padding: 10px; border: none; border-radius: 5px;")
        self.search_button.clicked.connect(self.search_animes)
        self.layout.addWidget(self.search_button)

        self.anime_label = QLabel("Select Anime:", self)
        self.anime_label.setFont(font)
        self.anime_label.setAlignment(Qt.AlignCenter)
        self.anime_label.setStyleSheet("color: #e3d8f1;")
        self.anime_label.hide()  # Esconder hasta que sea necesario
        self.layout.addWidget(self.anime_label)

        self.anime_combo = QComboBox(self)
        self.anime_combo.setFont(font)
        self.anime_combo.setStyleSheet("padding: 10px; border: 1px solid #6a0f91; border-radius: 5px; background-color: #2c003e; color: #e3d8f1;")
        self.anime_combo.hide()  # Esconder hasta que sea necesario
        self.layout.addWidget(self.anime_combo)

        self.episode_label = QLabel("Select Episodes:", self)
        self.episode_label.setFont(font)
        self.episode_label.setAlignment(Qt.AlignCenter)
        self.episode_label.setStyleSheet("color: #e3d8f1;")
        self.episode_label.hide()  # Esconder hasta que sea necesario
        self.layout.addWidget(self.episode_label)

        self.episode_combo = QListWidget(self)
        self.episode_combo.setFont(font)
        self.episode_combo.setStyleSheet("padding: 10px; border: 1px solid #6a0f91; border-radius: 5px; background-color: #2c003e; color: #e3d8f1;")
        self.episode_combo.setSelectionMode(QListWidget.MultiSelection)  # Permite seleccion multiple
        self.episode_combo.hide()  # Esconder hasta que sea necesario
        self.layout.addWidget(self.episode_combo)

        self.download_button = QPushButton("Download", self)
        self.download_button.setFont(font)
        self.download_button.setStyleSheet("background-color: #6a0f91; color: #e3d8f1; padding: 10px; border: none; border-radius: 5px;")
        self.download_button.clicked.connect(self.start_download)
        self.layout.addWidget(self.download_button)

        self.result_label = QLabel("", self)
        self.result_label.setFont(font)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("color: #e3d8f1;")
        self.layout.addWidget(self.result_label)

        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        palette = self.palette()
        palette.setColor(QPalette.Background, QColor(18, 18, 24))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.output_text = QTextEdit(self)
        self.output_text.setFont(font)
        self.output_text.setStyleSheet("padding: 10px; border: 1px solid #6a0f91; border-radius: 5px; background-color: #2c003e; color: #e3d8f1;")
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

    def start_download(self):
        slug = self.anime_combo.currentData()
        selected_items = self.episode_combo.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "No Episode Selected", "Please select at least one episode to download.")
            return

        self.download_thread = DownloadThread(slug, selected_items)
        self.download_thread.log_signal.connect(self.print_log)
        self.download_thread.start()

    def print_log(self, text):
        self.output_text.append(text)

    def search_animes(self):
        prompt = self.prompt_input.text()
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'es-ES,es;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www3.animeflv.net',
            'referer': 'https://www3.animeflv.net/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        data = {'value': prompt}
        response = requests.post('https://www3.animeflv.net/api/animes/search', headers=headers, data=data)
        anime_list = response.json()  # Respuesta json de la api
        
        self.anime_combo.clear()
        self.episode_combo.clear()

        self.anime_label.show()
        self.anime_combo.show()
        self.episode_label.show()
        self.episode_combo.show()

        for anime in anime_list:
            title = html.unescape(anime['title'])  # Obtener el titulo del json 
            self.anime_combo.addItem(title, anime['slug'])
        
        self.anime_combo.currentIndexChanged.connect(self.update_episodes)

        if len(anime_list) > 0:
            self.auto_select_first_anime()
        else:
            self.episode_label.hide()
            self.episode_combo.hide()

    def auto_select_first_anime(self):
        self.anime_combo.setCurrentIndex(0)
        self.update_episodes()
    
    def update_episodes(self):
        global slug
        slug = self.anime_combo.currentData()
        episodes = self.get_episodes(slug)  # De aqui obtiene el numero mas alto de episodios
        
        self.episode_combo.clear()

        if episodes > 0:
            for ep in range(1, episodes + 1):
                item = QListWidgetItem(f"Episode {ep}") 
                item.setData(Qt.UserRole, ep)  
                self.episode_combo.addItem(item)
        else:
            self.episode_label.hide()
            self.episode_combo.hide()

    def get_episodes(self, slug):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'es-ES,es;q=0.9',
            'referer': 'https://www3.animeflv.net/browse?q=chuunibyou',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

        try:
            response = requests.get(f'https://www3.animeflv.net/anime/{slug}', headers=headers)
            html = response.text

            episodes = html[html.find('var episodes = [[') + len('var episodes = [['):]
            episodes = episodes[:episodes.find(',')]
            return int(episodes)
        except (requests.HTTPError, ValueError) as e:
            return 0

    def download_from_mega(self, url, ep):
        url = url.replace("embed", "file")
        mega = Mega()
        m = mega.login() 

        try:
            file_info = m.get_public_url_info(url)
            with open("download_L.log", "a+") as f:
                self.log_signal.emit(f"{slug} - {ep} File found | The download has started: {file_info}")
                f.write(f"{slug} - {ep} File found | The download has started: {file_info}\n")
        except Exception as e:
            return False
        try:
            script_path = os.path.abspath(__file__)
            script_dir = os.path.dirname(script_path)
            new_folder_name = slug
            new_folder_path = os.path.join(script_dir, new_folder_name)
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            file = m.download_url(url, new_folder_path)
        except Exception as e:
            return False
        return True

    def check_yu(self, id):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'es-ES,es;q=0.9',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        response = requests.get(f'https://www.yourupload.com/watch/{id}', headers=headers)
        html = response.text
        html = html[:html.find('class="btn btn-success"')][::-1]
        html = html[:html.find('"=ferh')][::-1].replace('"', '')
        url = f"https://www.yourupload.com{html}"
        r = requests.get(url)
        html = r.text
        html = html[html.find('<a href="#" data-url="') + len('<a href="#" data-url="'):]
        html = html[:html.find('"')]
        url = f"https://www.yourupload.com{html}"
        url_conv = url.replace("amp;", "")
        r = requests.get(url_conv)
        if "bad hand off" in r.text:
            return url
        else:
            return None

    def log_save(self, url, slug, episode):
        with open("download_L.log", "a+") as f:
            f.write(f"{slug} - {episode} Download: {url}\n")
            self.log_signal.emit(f"{slug} - {episode} Download link saved in links.txt")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AnimeDownloader()
    window.show()
    sys.exit(app.exec_())
