CTR Nitro-Fueled Mod Kit (kyogre21)
===================================

(Versión francesa: README.txt. English version: README_EN.txt.)

Mods de kyogre21 para Crash Team Racing Nitro-Fueled en PC (port CTR-NitroFueled-PC / OCTR-NitroFueled-PC, versión
del juego 01.21), reunidos en un solo repositorio.

El Mod Kit
----------
CTRNF-ModKit.exe reúne todos los mods en una sola ventana: eliges una vez la carpeta del port, activas los mods que
quieras (una pestaña por mod), ves los archivos que han colocado, lo desinstalas todo con un clic y luego «Iniciar el
juego», que abre el launcher oficial del port. Si el juego se cuelga, el kit muestra un informe legible para copiar.
El kit está en español, inglés o francés (lista «Idioma» arriba a la derecha).
Código fuente: carpeta modkit.

Los mods
--------
- Randomizer (carpeta randomizer): mezcla el modo Aventura (circuitos, recompensas, copas, condiciones de apertura,
  ubicación de los portales), siempre se puede terminar, con opciones de comodidad.
- Pegatinas (carpeta autocollants): reemplaza las pegatinas de los karts (y sus iconos del menú) por tus propias
  imágenes.
- Autosplitter de LiveSplit, versión ALFA (carpeta autosplitter): marca los splits solo durante el modo Aventura.
  Desarrollo muy temprano.
- Comodidad (pestaña del Mod Kit): las opciones de comodidad del randomizer en el juego original, sin semilla
  (objetivo por nivel en las carreras de reliquia, reserva de turbo, podios rápidos, consejos de Aku Aku), y
  «Reintentar / Continuar» al final de cada carrera de reliquia (ganada o perdida), para intentar un nivel mejor sin
  volver al hub. Tu partida y tus partidas guardadas no cambian.
Los programas de cada mod siguen disponibles por separado (solo en francés), pero el Mod Kit los contiene
todos.

Descarga
--------
Los programas listos para usar (nada que instalar) están en la página «Releases»:
https://github.com/kyogre21/ctrnf-modkit/releases/latest
Windows puede mostrar «Windows protegió su PC» (programa sin firmar): haz clic en «Más información» y luego en
«Ejecutar de todas formas».

Port OCTR v0.9 o más reciente
-----------------------------
Desde la v0.9.0 (20/11/2026), el port aplica siempre el «Pack Tacho». El Mod Kit 0.3.3 (Randomizer 0.5.3) coloca su
código fuera de las zonas del Pack Tacho: el randomizer funciona en la v0.9 (probado en el juego con la v0.9.4) igual
que en la v0.8.8. Las versiones anteriores del randomizer cuelgan el juego en la v0.9: actualiza el kit y vuelve a
colocar una semilla. Antes de colocar una semilla, el kit sigue comprobando que ningún otro parche escribe en los
mismos sitios.

Usar varios mods juntos
-----------------------
Los mods están hechos para funcionar juntos. Ninguno modifica los archivos del juego: cada uno coloca sus propios
archivos pequeños en la carpeta archives del juego, y nunca se pisan:
- pegatinas: archives\update3.pak;
- randomizer: archives\update4.pak (minimapa de las reliquias) y archives\update_hub3.pak (podios rápidos),
  además de patches\Randomizer.xml en la carpeta del port;
- comodidad: patches\Confort.xml, archives\update_hub3.pak (podios rápidos) y archives\update5.pak
  (Reintentar / Continuar). Cuando Confort.xml está presente, sus ajustes sustituyen a los de comodidad de la semilla
  (ninguna opción se aplica dos veces).
El juego lee update3.pak, update4.pak y luego update5.pak en orden y se detiene en el primero que falta: cuando un
hueco está vacío antes de uno de estos archivos (sin pegatinas, por ejemplo), el kit coloca allí un «relleno» (un
archivo del juego copiado sin cambios, sin efecto), que se quita cuando ya no hace falta.

Este repositorio no contiene ningún archivo del juego: debes tener el juego.

Créditos
--------
- Autor: kyogre21.
- Idea del randomizer inspirada en el CTR-Randomizer de icebound777 para la versión PS1
  (https://github.com/icebound777/CTR-Randomizer-Standalone, licencia MIT).
- Port para PC: CTR-NitroFueled-PC y su versión OCTR-NitroFueled-PC.
- Traducción al español: solicitada por la comunidad (GitHub, octubre de 2026).

Licencia: MIT (archivo LICENSE). Puedes usar, modificar y compartir estos mods, siempre que conserves el nombre del
autor.
