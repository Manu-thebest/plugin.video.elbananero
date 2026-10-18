# plugin.video.elbananero

Add-on de Kodi que lista y reproduce todo el contenido de [elbananero.com](https://www.elbananero.com).

## Que hace

- **Novedades**: los videos de la portada, con paginacion (15 paginas).
- **Categorias**: las 11 secciones de la web (Trailerazos, Infomerciales, Canciones, Putoriales...).
- **Buscar**: por texto, sin salir de Kodi.
- **Reproducir**: usa el MP4 directo de la web (`videos/<id>.mp4`), con caratula.

## Detalles tecnicos

La web es PHP sencillo, sin sesion ni cookies:

| Que | URL |
|---|---|
| Listado | `index_.php?page=N` (ojo: `index.php` es una cascara vacia) |
| Categoria | `categorias.php?page=N&search=<CATEGORIA>&t=menu` |
| Busqueda | `categorias.php?page=N&search=<texto>` (con `&t=menu` da 0 resultados) |
| Video | `videos/<id>.mp4` (MP4 directo, `200 video/mp4`, soporta rangos) |
| Miniatura | `miniaturas/<id>.jpg` |

Hay que mandar un `User-Agent` de navegador: sin el, la web devuelve 1 KB vacio.

## Instalacion

Descarga el ZIP de la ultima release e instalalo desde *Ajustes > Add-ons > Instalar desde archivo zip*.
