# -*- coding: utf-8 -*-
"""Add-on de Kodi: todo el contenido de elbananero.com.

Los videos son MP4 directos (videos/<id>.mp4), asi que no hacen falta
cookies, cabeceras especiales ni resolver nada raro: se le da la URL a Kodi
y reproduce.
"""

import os
import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

_RUTA = xbmcaddon.Addon().getAddonInfo("path")
_LIB = os.path.join(_RUTA, "resources", "lib")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)

from urllib.parse import parse_qsl, urlencode  # noqa: E402

import elbananero  # noqa: E402
from kodiutils import ADDON_ID, notificar  # noqa: E402

try:
    HANDLE = int(sys.argv[1])
except (IndexError, ValueError):
    HANDLE = -1

BASE = "plugin://%s/" % ADDON_ID
FANART = os.path.join(_RUTA, "resources", "fanart.jpg")


def url_for(**kw):
    return BASE + "?" + urlencode(kw)


def _menu(items):
    for etiqueta, params, icono in items:
        li = xbmcgui.ListItem(label=etiqueta)
        li.setArt({"icon": icono, "fanart": FANART})
        xbmcplugin.addDirectoryItem(HANDLE, url_for(**params), li, isFolder=True)


def _videos(videos):
    for v in videos:
        miniatura = elbananero.url_miniatura(v["id"])
        li = xbmcgui.ListItem(label=v["titulo"])
        li.setArt({"thumb": miniatura, "icon": miniatura, "fanart": FANART})
        li.setInfo("video", {"title": v["titulo"]})
        li.setProperty("IsPlayable", "true")
        xbmcplugin.addDirectoryItem(
            HANDLE, url_for(action="play", vid=v["id"], titulo=v["titulo"]), li, isFolder=False)


def menu_principal():
    xbmcplugin.setContent(HANDLE, "files")
    _menu([
        ("Novedades", {"action": "lista", "tipo": "novedades", "pagina": 1},
         "DefaultRecentlyAddedMovies.png"),
        ("Categorías", {"action": "categorias"}, "DefaultGenre.png"),
        ("Buscar", {"action": "buscar"}, "DefaultAddonsSearch.png"),
    ])
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)


def menu_categorias():
    xbmcplugin.setContent(HANDLE, "files")
    items = []
    for categoria in elbananero.CATEGORIAS:
        items.append((categoria.title(),
                      {"action": "lista", "tipo": "categoria", "valor": categoria, "pagina": 1},
                      "DefaultGenre.png"))
    _menu(items)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)


def lista(tipo, valor, pagina):
    try:
        pagina = int(pagina or 1)
    except (TypeError, ValueError):
        pagina = 1
    xbmcplugin.setContent(HANDLE, "videos")
    try:
        if tipo == "categoria":
            videos, ultima = elbananero.por_categoria(valor, pagina)
        elif tipo == "busqueda":
            videos, ultima = elbananero.buscar(valor, pagina)
        else:
            videos, ultima = elbananero.novedades(pagina)
    except elbananero.ErrorSitio as e:
        xbmc.log("El Bananero: no pude leer la web: %s" % e, xbmc.LOGERROR)
        notificar("No he podido conectar con la web")
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return

    _videos(videos)
    if videos and pagina < ultima:
        li = xbmcgui.ListItem(label="Página siguiente (%d de %d)" % (pagina + 1, ultima))
        li.setArt({"icon": "DefaultFolder.png", "fanart": FANART})
        xbmcplugin.addDirectoryItem(
            HANDLE, url_for(action="lista", tipo=tipo, valor=valor, pagina=pagina + 1),
            li, isFolder=True)
    xbmcplugin.endOfDirectory(HANDLE)


def buscar():
    texto = xbmcgui.Dialog().input("Buscar en El Bananero", type=xbmcgui.INPUT_ALPHANUM)
    if not texto or not texto.strip():
        return
    lista("busqueda", texto.strip(), 1)


def reproducir(vid, titulo):
    if not vid:
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return
    url = elbananero.url_video(vid)
    xbmc.log("El Bananero: reproduciendo %s" % url, xbmc.LOGINFO)
    li = xbmcgui.ListItem(path=url)
    li.setInfo("video", {"title": titulo or ("Vídeo %s" % vid)})
    li.setArt({"thumb": elbananero.url_miniatura(vid), "fanart": FANART})
    xbmcplugin.setResolvedUrl(HANDLE, True, li)


def router(params):
    accion = params.get("action", "")
    if accion == "categorias":
        menu_categorias()
    elif accion == "lista":
        lista(params.get("tipo", "novedades"), params.get("valor", ""), params.get("pagina", 1))
    elif accion == "buscar":
        buscar()
    elif accion == "play":
        reproducir(params.get("vid", ""), params.get("titulo", ""))
    else:
        menu_principal()


if __name__ == "__main__":
    try:
        argumentos = dict(parse_qsl(sys.argv[2][1:])) if len(sys.argv) > 2 else {}
        router(argumentos)
    except Exception:
        import traceback
        xbmc.log("El Bananero: error: " + traceback.format_exc(), xbmc.LOGERROR)
