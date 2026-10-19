# JI AFK CINEMATIC · proyecto V2

[Video final](../deliverables/ji-afk-cinematic-logo-animation-v2.mp4): 1080²,
30/1 fps constantes, 225 fotogramas (0–224), 7,5 segundos. H.264 High, yuv420p,
Rec.709 y faststart. Silencioso. Fuente SVG procedural, sin video generativo.

## Reproducir y regenerar

Desde `motion/ji-afk-cinematic-logo/` (o la raíz del proyecto extraído del ZIP):

```bash
# Debian / Ubuntu, dependencias del sistema
sudo apt-get install python3-venv ffmpeg librsvg2-2 libcairo2 fonts-dejavu-core chromium
python3 -m venv work/venv
work/venv/bin/pip install -r v2/requirements.txt
work/venv/bin/python v2/src/render.py
work/venv/bin/python v2/src/verify.py
work/venv/bin/python v2/src/playback_review.py
```

El render necesita únicamente Pillow, NumPy, FFmpeg, librsvg y Cairo.
Matplotlib se usa para los gráficos QA; Playwright y `/usr/bin/chromium` para
la prueba adicional de reproducción. Probado con Python 3.12.14, FFmpeg 7.1.5,
Pillow 12.3.0 y NumPy 2.3.5; las versiones efectivas del entorno se guardan en QA.
El render usa cuatro procesos. `--workers 2` reduce memoria, `--draft` crea
una previsualización de 540² en `v2/work/`, sin sobrescribir el MP4 final.

Abre `v2/preview.html` localmente o sirve la raíz con `python3 -m http.server`.
El reproductor puede comparar ambas versiones al mismo segundo y ralentizar
el movimiento. El render no necesita navegador ni conexión de red.

## Editar geometría, rig y timing

| Archivo | Contenido editable |
|---|---|
| `src/logo.py` | Curvas originales del zorrito, +, espiral, ornamentos y lettering trazado. |
| `src/timeline.json` | Keyframes en fotogramas de 30 fps, tangentes, profundidad, inercia, sampling. |
| `src/geometry.py` | Hermite con tangentes; easing Bézier; trim por longitud de arco y corte de Casteljau. |
| `src/rig.py` | Proyección 2.5D, pivotes anatómicos, crecimiento, curvas de orejas y resorte amortiguado. |
| `src/animate.py` | Capas SVG, oclusión, máscara radial, revelado de ojos y trazos, movimiento de letras. |
| `src/render.py` | SVG subframe → rasterización → integración temporal lineal → H.264. |
| `assets/ji-afk-cinematic-master.svg` | Máster canónico por capas, editable en Inkscape. |
| `assets/ji-afk-cinematic-v2-final.svg` | Pose final de V2 en composición cuadrada, todo en trazados. |

Cada keyframe acepta `[fotograma, valor, tangente_entrada, tangente_salida]`.
Las tangentes son unidades por fotograma; si se omiten valen cero. Yaw está
en radianes, roll y flexión en grados. Las coordenadas del arte son 1536 unidades;
la composición cuadrada abarca `0 -76.5 1536 1536`. No se deforma el PNG.

Profundidades separadas para cara, ojos, orejas y hocico; compresión del ojo
lejano hasta 79%, mirada adelantada dos fotogramas y oclusión curva. Las orejas
crecen desde sus bases y deforman sus controles Bézier. El resorte se integra a
240 Hz, con retrasos de 3 y 5 fotogramas. La unión superior del hocico comparte
la superficie de la cara; la profundidad propia entra gradualmente hacia abajo.

Para exportar cualquier pose como SVG editable:

```bash
mkdir -p v2/work
PYTHONPATH=v2/src work/venv/bin/python -c 'from animate import frame; from pathlib import Path; Path("v2/work/pose-f090.svg").write_text(frame(3.0))'
```

Los cambios hechos directamente al SVG se deben trasladar a `logo.py` si se
quiere regenerar la animación desde el código.

## Timing y acabado

- 0–1 s: + con giro de 90° y sobrepaso 115%; espiral dibujada por longitud real;
  puntas y rizos crecen con retraso y curvatura.
- 1–2,2 s: curiosidad derecha, inversión por arco a izquierda, escorzo de ojos,
  compensación de profundidad e inercia independiente de orejas.
- 2,2–3,7 s: regreso, acecho comprimido (X110%, Y85%), escala mínima80%,
  impulso112% en f90, rebote97%, asentamiento100%; revelación desde el hocico.
- 3,7–5,1 s: letras desfasadas 2 fotogramas, recorrido vertical40px, máscaras
  por trazos y acento del gancho J; CINEMATIC se expande desde el centro.
- 5,1–7,07 s: parpadeo en f162, giro tenue de espiral y oscilaciones amortiguadas.
- 7,07–7,5 s: pose final idéntica en fuente durante 13 fotogramas.

Se rasteriza cada submuestra a 2160² y se reduce con Lanczos. En intervalos
rápidos se integran seis submuestras en luz lineal con obturador de 120°;
fuera de ellos se usa una muestra. No hay conversión de fps de V1 en producción.
La normalización de V1 a muestras de 30 Hz existe únicamente en el análisis QA.

## Verificación y referencia

[QA-V2.md](qa/QA-V2.md) reúne la revisión, pruebas visuales, ffprobe, densidad
por tramos y hashes de regeneración. Las hojas comparan exactamente los doce
tiempos del brief. La secuencia completa de 225 fotogramas está en cinco hojas.
El ZIP conserva la estructura necesaria para renderizar y comparar V1/V2.

Se reutiliza la geometría canónica V1 contrastada visualmente con la imagen
oficial del chat. El PNG original no existe como binario accesible en este
entorno; no se afirma comparación pixel a pixel contra él. El contraste
numérico de la pose final se realiza contra el máster SVG incluido.
