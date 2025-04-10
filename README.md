# 📥 Anime Downloader GUI - Demo funcional

> Aplicación en Python con interfaz gráfica para buscar y descargar episodios de anime desde MEGA y otras fuentes.  
> 🎮 Hecha como práctica personal, funciona bien y sirve como base para cosas más complejas.

---

## 📌 Descripción

Anime Downloader GUI es una pequeña aplicación en Python con interfaz gráfica que permite buscar y descargar episodios de anime desde fuentes como MEGA.  
Combina scraping web, automatización y una GUI hecha con PyQt5, todo en un proyecto práctico pensado para aprender y experimentar.

No es una app “comercial” ni de uso masivo, pero **funciona bien** y es útil como base para mejorar o ampliar.

---

## 🎯 ¿Qué hace?

- 🔍 Busca episodios de anime según el nombre
- 📄 Muestra resultados en una lista interactiva
- 📥 Descarga los episodios desde enlaces MEGA (u otros)
- 🎛️ Tiene una GUI funcional y usable con PyQt5
- 🧪 Incluye scraping/parsing de webs y uso de sesiones HTTP

---

## 🧠 Tecnologías y librerías utilizadas

- 🐍 **Python 3.10+**
- 🖥️ **PyQt5** — para la interfaz gráfica
- 🌐 `requests` — para peticiones HTTP
- 🔐 `mega.py` — acceso a enlaces y descarga directa desde MEGA
- 🧼 `beautifulsoup4` — para parsear HTML
- 🧠 Otras libs: `re`, `json`, `os`, `html`, `urllib.parse`, `sys`, etc.

---

## 🖼️ Interfaz

La app incluye:

- Barra de búsqueda
- Lista de resultados con scroll
- Información del episodio o enlace
- Botón de descarga directa
- Opcional: selección de calidad/servidor si la web lo permite

> 💡 Puedes modificar el script fácilmente para adaptarlo a tu propia fuente o estilo.

---

## 🚀 Cómo ejecutarlo

1. Clona el repositorio:

```bash
git clone https://github.com/TripleA26/anime-downloader-gui.git
cd anime-downloader-gui
```
2.Instala las dependencias necesarias:
```bash
pip install -r requirements.txt
```
3.Ejecuta la aplicación:
```bash
python main.py
```

⚠️ Aviso legal
Este proyecto se ha desarrollado con fines educativos y de autoaprendizaje.
No promueve ni respalda el uso ilegal de contenido protegido por derechos de autor.
Usa el código bajo tu propia responsabilidad.

📫 Contacto
¿Quieres comentar algo, colaborar o simplemente charlar de código?

🗨️ Discord: 2a6a
👤 GitHub: @TripleA26
