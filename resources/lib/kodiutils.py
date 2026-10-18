# -*- coding: utf-8 -*-
"""Utilidades minimas de Kodi."""

import xbmc
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
NOMBRE = ADDON.getAddonInfo("name")


def ajuste(clave, defecto=""):
    try:
        valor = ADDON.getSetting(clave)
        return valor if valor else defecto
    except Exception:
        return defecto


def notificar(mensaje, titulo=None, tiempo=4000):
    try:
        xbmcgui.Dialog().notification(titulo or NOMBRE, mensaje, xbmcgui.NOTIFICATION_INFO, tiempo)
    except Exception:
        xbmc.log("%s: %s" % (NOMBRE, mensaje), xbmc.LOGINFO)
