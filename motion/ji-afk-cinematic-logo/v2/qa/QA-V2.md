# Revisión V2 · JI AFK CINEMATIC

## Resultado y evidencia

El MP4 V2 es una animación nueva de **1080×1080, 30/1 fps, 225 fotogramas,
7,5 segundos**, H.264 High / yuv420p, Rec.709, sin audio y con `moov` antes de
`mdat` para inicio rápido. Se decodificó íntegramente y se comprobaron todos
los timestamps de presentación. [Informe automático](verification-v2.json),
[ffprobe](ffprobe-v2.json), [sampling](render-settings.json) y
[entorno efectivo](render-environment.json).

La revisión combinó reproducción del MP4 real a velocidad normal en Chromium,
telemetría del reproductor y examen visual secuencial de todos los fotogramas:
[1 · f000–044](playback/playback-01.jpg), [2 · f045–089](playback/playback-02.jpg),
[3 · f090–134](playback/playback-03.jpg), [4 · f135–179](playback/playback-04.jpg),
[5 · f180–224](playback/playback-05.jpg).
[Telemetría](playback/playback-report.json) y [reproductor al terminar](playback/player-ended.png).
Las hojas contienen los 225 frames decodificados del MP4. La telemetría de
`requestVideoFrameCallback` se conserva por separado: algunos callbacks pueden
agruparse en Chromium headless; no se presentan esos callbacks como capturas
exhaustivas. `getVideoPlaybackQuality` verifica 225 frames y cero descartados.

## Comparación solicitada

| Tiempo | Observación V2 | Prueba |
|---|---|---|
| 0,4 s | + asentándose tras giro y sobrepaso; espiral parcialmente dibujada; crecimiento curvo de orejas. | [0,4–2,5 s](comparison-v1-v2-01.jpg) |
| 1,2 s | Yaw derecho, espiral lejana estrecha, rasgos adelantados y orejas compensadas. | misma hoja |
| 1,8 s | Inversión sobre arco; cambia el escorzo y la flexión de las puntas. | misma hoja |
| 2,5 s | Regreso al eje antes del descenso de anticipación. | misma hoja |
| 2,9 s | Pose compacta y baja; ojos entrecerrados. | [2,9–4,2 s](comparison-v1-v2-02.jpg) |
| 3,0 s | Cabeza revelada desde el hocico, pico de escala en f90. | misma hoja |
| 3,1 s | Rebote descendente, curvas de orejas y mejillas todavía en movimiento. | misma hoja |
| 4,2 s | Letras ya legibles con últimos asentamientos individuales. | misma hoja |
| 5,0 s | CINEMATIC se abre desde el centro con tracking y opacidad coordinados. | [5–7,3 s](comparison-v1-v2-03.jpg) |
| 5,4 s | Cierre expresivo del +; la espiral mantiene su identidad. | misma hoja |
| 6,5 s | Movimiento residual tenue, sin congelación larga. | misma hoja |
| 7,3 s | Pose de marca estable, igual al máster en proporciones. | misma hoja |

Las doce capturas V2 a 1080² están en [frames/](frames/). La
[tira f078–105](impact-frames-078-105.jpg) permite examinar cada fotograma de la
compresión, salida, revelación y rebote. El desenfoque de f087–089 procede de
seis submuestras temporales de vectores, no de un filtro aplicado al MP4.

## Correcciones surgidas de la revisión

1. Los primeros ensayos de orejas tenían extremos planos por división de la
   silueta. Se reemplazaron por puntas curvas trazadas y crecimiento anatómico.
2. La búsqueda numérica del easing devolvía un valor minúsculo en cero, dejando
   puntos con remate redondo antes de la entrada. Se fijaron extremos exactos;
   el primer fotograma se compara con el fondo vacío y coincide byte a byte.
3. El plano del hocico dejaba una línea rosada al cambiar de profundidad en el
   rebote. Sus puntos superiores ahora comparten proyección con la cara y la
   profundidad propia aumenta hacia abajo. Se inspeccionó de nuevo f93 a 1080²
   y se comprueba la continuidad de cuatro puntos de unión durante f088–111.
4. Se verificó la cobertura completa del dibujo de espiral y las máscaras de
   J, I, A, F y K: cero píxeles interiores sin cubrir al completar el trazo.

## Movimiento y cierre

[Gráfico de densidad](motion-density.png), [medidas por tramo](motion-density.csv),
[curvas del rig](rig-curves.png) y [valores de los 225 frames](rig-curves.csv).
La medida es la diferencia RGB absoluta media entre fotogramas consecutivos,
calculada a 270²; la región del personaje excluye el texto. Es una medida de
actividad, no una puntuación de calidad artística. V1 se muestrea a 30 Hz solo
para esta comparación. La producción V2 nunca lee el MP4 V1.

Durante el tramo de tipografía (f111–152), el personaje mantiene movimiento
en todas las transiciones; V1 estaba prácticamente quieto buena parte del
tramo. Durante f153–211 V2 conserva el parpadeo y la amortiguación, mientras
V1 permanece estático. Los últimos 13 SVG (f212–224) son exactamente idénticos.
Las diferencias minúsculas del MP4 durante ese cierre son de compresión.

El ojo lejano llega a 79% de anchura; el escorzo se invierte al cambiar de lado.
La compresión máxima de anticipación es X110% / Y85% antes del impulso.
La escala pasa por 80% en f87, 112% en f90, 97% en f95 y se amortigua a 100%.
Los parámetros y tangentes son editables en `src/timeline.json`.

## Regeneración y fidelidad

Además, se extrajo el ZIP a una carpeta aislada y se volvió a renderizar el
video completo: los bytes del MP4 regenerado coinciden exactamente con la
entrega. [Prueba de regeneración completa](package-regeneration.json).

Se regeneraron dos veces los frames f036, f090, f162 y f224 a resolución final
con la configuración de producción; los bytes RGB coinciden. Sus hashes están
en el informe. El ZIP mantiene el código, los SVG, las dependencias, el MP4 y
las pruebas, sin depender de imágenes prerenderizadas como fuente.

La pose final se contrastó con el máster SVG canónico de V1 en el mismo encuadre:
error medio por canal aproximado 0,00124 sobre 255, limitado a bordes de curvas y
la composición continua de silueta. Todas las letras son trazados vectoriales;
no hay imágenes embebidas ni dependencias tipográficas en el arte.

El original `01-50910.png` solo estuvo visible como imagen de referencia en el
chat; no había binario accesible en los adjuntos montados ni en el repo.
Se conserva la reconstrucción Bézier canónica y su identidad visual, pero no
se afirma una comparación de píxeles contra un PNG no disponible.

V1 permanece intacta. La entrega actual lleva sufijo `-v2`, con fuentes y QA
en `v2/`, dentro del mismo directorio de proyecto y PR #1.
