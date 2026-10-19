# QA de entrega

Se renderizó y revisó la animación completa; la entrega es un MP4 final
decodificable, acompañado de la geometría vectorial y su proyecto fuente.

## Video

- 1080 × 1080, H.264 High, yuv420p, 60/1 fps, duración exacta 8.000 s.
- 480 fotogramas contados mediante decodificación con ffprobe y recorrido
  completo con FFmpeg sin errores.
- Render SVG a 2160 × 2160, reducción Lanczos y codificación CRF 16.
- Inicio rápido (`faststart`), etiquetas de color Rec.709, sin marcas de agua.
- Sin audio por decisión artística; no hay pista sonora incompleta.
- Máster adicional a 2160 × 2160, con el mismo timing, a CRF 14.

## Revisión visual

Se inspeccionaron el SVG maestro a 1536 × 1383, las doce capturas de las fases
extraídas del MP4 final y una secuencia de 48 capturas a intervalos de 1/6 s.
Se comprobó el contorno, la asimetría de las orejas, sus ornamentos, la cruz,
la espiral, los dos remates laterales, la nariz y la escritura exacta de
«JI AFK» y «CINEMATIC» contra la referencia visual del mensaje.

La primera revisión detectó líneas de antialias en cortes entre las capas y
pequeñas separaciones en la nariz. Se ajustaron los solapamientos y se volvió
a renderizar el video completo. La versión entregada tiene cero píxeles
interiores descubiertos en la unión de las capas de la silueta.

La revelación de la silueta usa geometría expansiva. Los ojos conservan sus
formas oficiales durante los gestos; no se usan ojos genéricos. Las letras
se construyen mediante máscaras de trazos independientes sobre sus contornos
reales. Se verificó que las máscaras cubren todos los glifos antes de retirarse:
cero píxeles faltantes, por lo que no hay cambio súbito al finalizar la escritura.

No se observaron cortes en el borde del encuadre, huecos interiores, parpadeos
ni cambios de proporción en el cierre. El mayor cambio temporal coincide con
la revelación principal, a 3.317 s. El movimiento se asienta antes del texto.
El cierre permanece estable desde 5.85 s durante 2.15 s, sin fundido a negro.

## Controles reproducibles

`python3 src/verify.py` verifica dimensiones, codec, duración, frames, estabilidad
de cierre, ausencia de imágenes raster y fuentes externas en el SVG, cobertura
de máscaras y unión de fragmentos. También produce `verification.json`,
`temporal-analysis.csv` y la hoja de 48 fotogramas.

El SVG maestro tiene 28 grupos con nombre. La comparación del SVG final con
el maestro, en composición cuadrada, da un error medio de 0.00042 niveles
por canal; las diferencias de hasta 7/255 se limitan al antialias de los bordes.
La variación media máxima entre frames codificados después de 6 s es inferior
a 0.002/255, debida a compresión; la geometría fuente es idéntica.

## Límite de la comparación con el original

La imagen oficial estaba visible en el chat, pero el archivo binario
`01-50910.png` no estaba montado. La fidelidad se verificó por observación;
no se presenta un cálculo de similitud contra ese PNG. El fondo y las curvas
se han limpiado como arte vectorial, conservando la composición de referencia.

No se utilizó un modelo generativo de imágenes o video, una imagen incrustada,
un archivo After Effects ficticio ni material sonoro de terceros.

El trabajo del repositorio se limita a `motion/ji-afk-cinematic-logo/`.
Las huellas SHA-256 de los videos y sus metadatos se conservan en
`verification.json`; el paquete completo incluye un manifiesto de archivos.
