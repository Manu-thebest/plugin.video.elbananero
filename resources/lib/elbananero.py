# -*- coding: utf-8 -*-
"""Todo el acceso a elbananero.com: listados, categorias, busqueda y videos.

La web es PHP sencillo y no necesita sesion ni cookies:
  - Listado de novedades: index_.php?page=N   (ojo: index.php es una cascara vacia)
  - Categoria:            categorias.php?page=N&search=<CATEGORIA>&t=menu
  - Busqueda libre:       categorias.php?page=N&search=<texto>   (SIN t=menu)
  - Video:                videos/<id>.mp4  (MP4 directo, 200 video/mp4)
  - Miniatura:            miniaturas/<id>.jpg
"""

import re
import urllib.parse
import urllib.request

BASE = "https://www.elbananero.com/"

# La web devuelve una pagina vacia (1 KB) si no te identificas como navegador.
NAVEGADOR = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Las 11 secciones del menu de la web, en su orden.
CATEGORIAS = (
    "TRAILERAZOS",
    "VS. EL BANANERO",
    "INFOMERCIALES",
    "CANCIONES",
    "NOTICIERO",
    "PROF. PAUL VAZO",
    "PUTORIALES",
    "CARTITAS",
    "VARIOS",
    "CATEGORIA 2005",
    "ANIMACIONES GARKA",
)

_RX_FICHA = re.compile(r'<h5>\s*<a[^>]*href="video\.php\?id=(\d+)"[^>]*>(.*?)</a>', re.S)
_RX_ID = re.compile(r"video\.php\?id=(\d+)")
_RX_ETIQUETA = re.compile(r"<[^>]+>")
_RX_PAGINA = re.compile(r"[?&]page=(\d+)")

_ENTIDADES = (
    ("&amp;", "&"), ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " "),
    ("&aacute;", "á"), ("&eacute;", "é"), ("&iacute;", "í"), ("&oacute;", "ó"),
    ("&uacute;", "ú"), ("&ntilde;", "ñ"), ("&uuml;", "ü"),
    ("&Aacute;", "Á"), ("&Eacute;", "É"), ("&Iacute;", "Í"), ("&Oacute;", "Ó"),
    ("&Uacute;", "Ú"), ("&Ntilde;", "Ñ"),
    ("&laquo;", "«"), ("&raquo;", "»"), ("&hellip;", "…"), ("&mdash;", "—"),
)


class ErrorSitio(Exception):
    """No se pudo leer la web."""


def _limpiar(texto):
    """Quita etiquetas HTML y resuelve las entidades mas habituales."""
    t = _RX_ETIQUETA.sub("", texto or "")
    for viejo, nuevo in _ENTIDADES:
        t = t.replace(viejo, nuevo)
    return " ".join(t.split())


def _descargar(url, timeout=25):
    peticion = urllib.request.Request(url, headers={
        "User-Agent": NAVEGADOR,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(peticion, timeout=timeout) as respuesta:
            return respuesta.read().decode("utf-8", "replace")
    except Exception as e:
        raise ErrorSitio(str(e))


def _recortar(html):
    """Corta antes de los RECOMENDADOS: si no, salen videos repetidos."""
    corte = html.find("RECOMENDADOS")
    return html[:corte] if corte > 0 else html


def _pagina(url):
    """Devuelve (lista de videos, numero de la ultima pagina)."""
    html = _recortar(_descargar(url))
    videos = []
    vistos = set()
    for vid, titulo in _RX_FICHA.findall(html):
        if vid in vistos:
            continue
        vistos.add(vid)
        videos.append({"id": vid, "titulo": _limpiar(titulo) or ("Vídeo %s" % vid)})
    if not videos:
        # Plan B: si cambian el diseno, al menos salen los videos.
        for vid in _RX_ID.findall(html):
            if vid not in vistos:
                vistos.add(vid)
                videos.append({"id": vid, "titulo": "Vídeo %s" % vid})
    paginas = [int(n) for n in _RX_PAGINA.findall(html)]
    return videos, (max(paginas) if paginas else 1)


def novedades(page=1):
    return _pagina("%sindex_.php?page=%d" % (BASE, page))


def por_categoria(nombre, page=1):
    return _pagina("%scategorias.php?page=%d&search=%s&t=menu"
                   % (BASE, page, urllib.parse.quote(nombre)))


def buscar(texto, page=1):
    # OJO: con &t=menu la busqueda libre devuelve cero resultados.
    return _pagina("%scategorias.php?page=%d&search=%s"
                   % (BASE, page, urllib.parse.quote(texto)))


def url_video(vid):
    return "%svideos/%s.mp4" % (BASE, vid)


def url_miniatura(vid):
    return "%sminiaturas/%s.jpg" % (BASE, vid)


def url_ficha(vid):
    return "%svideo.php?id=%s" % (BASE, vid)
