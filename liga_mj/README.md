# Liga MJ — panel de competición

Aplicación de gestión para la liga de 24 clubes. Está hecha con **Python + Streamlit**, usa el logo de la liga y los 24 escudos incluidos, y guarda los cambios en un archivo JSON local. No necesita base de datos, claves API ni servicios de imágenes externos.

## Funciones

- Planteles separados por JNKA, Mati y Maxi.
- Escudos locales junto a los equipos en la tabla, el calendario, el cuadro de eliminatorias y las listas por presidente.
- Armado manual de las 8 fechas. Un equipo solo puede figurar una vez en cada fecha.
- Carga y edición de resultados; la tabla se actualiza automáticamente.
- Clasificación con PJ, ganados, empatados, perdidos, goles a favor/en contra, diferencia y puntos.
- Criterios de desempate: enfrentamiento directo cuando empatan dos clubes; diferencia de goles; menos goles en contra; más goles a favor. Para empates de tres o más, se usa una mini-tabla entre los clubes empatados antes de los criterios generales.
- Bracket de fase previa, cuartos, semifinales y final. Las series empatadas permiten elegir manualmente quién avanza.
- Descenso marcado para los puestos 23 y 24.
- Guarda automáticamente fechas, resultados y eliminatorias en `liga_data.json`.
- Permite descargar y restaurar copias JSON desde **Respaldo de datos** en la barra lateral.

## Ejecutar localmente

Requiere Python 3.10 o superior.

```bash
git clone <URL-DE-TU-REPOSITORIO>
cd liga-mj
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit abre la aplicación en `http://localhost:8501`.

## Subir a GitHub

1. Crea un repositorio nuevo en GitHub.
2. Descomprime el paquete y sube su contenido (incluida la carpeta `assets/`).
3. No subas `.venv/`, secretos ni `liga_data.json`: ese archivo contiene los resultados de tu liga y está excluido por `.gitignore`.

## Publicar en Streamlit Community Cloud

1. En Streamlit Community Cloud, elige **New app**.
2. Conecta tu GitHub y selecciona el repositorio, la rama y `app.py`.
3. Publica la app. No hacen falta variables secretas.

### Importante sobre los datos y el acceso

La app escribe en `liga_data.json` junto al código. En una computadora local, los datos permanecen en ese equipo. En servicios de alojamiento gratuitos como Streamlit Community Cloud, el sistema de archivos local puede ser efímero y los datos podrían no sobrevivir a reinicios o reconstrucciones; descarga periódicamente **Descargar copia JSON** desde la barra lateral y guarda el archivo fuera de la app. Si necesitas recuperar los resultados, cárgalo desde **Restaurar una copia JSON**. No se debe guardar información sensible en este archivo.

La app no incluye inicio de sesión. Si el enlace de Streamlit es accesible públicamente, quien pueda abrirlo podría cargar o cambiar resultados. Mantén la app privada o limita el acceso a personas de confianza antes de usarla como registro oficial.

## Formato del torneo

- 24 equipos distribuidos en partes iguales entre los tres presidentes.
- 8 fechas configurables manualmente desde **Fechas y resultados**.
- Posiciones 1–4: clasificación directa a cuartos.
- Posiciones 5–12: fase previa (5 vs 12, 7 vs 10, 6 vs 11 y 8 vs 9). Los ganadores se cruzan respectivamente con los puestos 1, 3, 2 y 4.
- Los ganadores continúan por el cuadro hasta la final.
- Posiciones 23 y 24: descenso.

## Escudos y atribución

Los 24 archivos PNG de `assets/clubs/` se incluyen en el repositorio para que la app no dependa de un servidor de imágenes al cargarse. Veintiún escudos se descargaron de `https://crests.football-data.org/{id}.png`, servicio cuyo recurso Team documenta el campo `crest`: [documentación de football-data.org](https://docs.football-data.org/general/v4/team.html). El escudo de **Fenerbahçe** se obtuvo de [football-logos.cc — Fenerbahçe](https://football-logos.cc/turkey/fenerbahce/), y los de **River Plate** y **Boca Juniors** de [FootyLogos — River Plate](https://www.footylogos.com/logos/river-plate) y [FootyLogos — Boca Juniors](https://www.footylogos.com/logos/boca-juniors). Ambos sitios solicitan citar su material. Los escudos y nombres pertenecen a sus respectivos titulares. Este proyecto independiente los muestra para identificar los equipos y no está afiliado ni respaldado por los clubes, football-data.org, football-logos.cc o FootyLogos. Si vas a publicar el sitio abiertamente o usarlo con fines comerciales, revisa los permisos aplicables.

## Estructura

```text
liga-mj/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/config.toml
└── assets/
    ├── logo.png
    └── clubs/       # 24 escudos PNG
```
