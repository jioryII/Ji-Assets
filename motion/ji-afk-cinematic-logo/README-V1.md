# JI AFK CINEMATIC · animación vectorial

**Entrega final:** `deliverables/ji-afk-cinematic-logo-animation.mp4`.
H.264 High, 1080 × 1080, 60 fps, 8 segundos, 480 fotogramas, color Rec.709,
sin marcas de agua. Versión silenciosa intencional.

Abre `preview.html` para reproducir, cambiar la velocidad y saltar entre fases.
El MP4 también se puede abrir directamente en cualquier reproductor compatible.

## Archivos

- `assets/ji-afk-cinematic-master.svg`: reconstrucción Bézier del logo completo,
  con las proporciones 1536 × 1383 de la referencia. Todas las letras son
  trazados; no requiere instalar fuentes. Capas de orejas, ornamentos, silueta,
  ojos, nariz, remates laterales, letras y fondo. Editable en Inkscape.
- `deliverables/ji-afk-cinematic-logo-animation-2160.mp4`: máster adicional
  H.264 de 2160 × 2160, 60 fps y 8 segundos.
- `src/logo.py`: geometría maestra editable y generador del SVG.
- `src/timeline.json`: poses, duración y configuración de render.
- `src/animate.py`: máscaras, parallax, solapamiento de orejas y construcción
  geométrica individual de letras. Cada instante produce un SVG auténtico.
- `src/raster.py`: rasterizador SVG mediante librsvg y Cairo.
- `src/render.py`: exportación completa y extracción de QA desde el MP4.
- `src/verify.py`: controles de video, geometría, cobertura y estabilidad.
- `qa/`: fotogramas extraídos del MP4, hoja de contacto, último SVG,
  metadatos de ffprobe e informe de verificación.

## Volver a renderizar

Requisitos: Python 3.10+, Pillow, NumPy, FFmpeg/ffprobe con libx264 y las
bibliotecas del sistema librsvg 2 y Cairo. No se necesita navegador, Remotion,
servicio externo ni modelo generativo. En Debian/Ubuntu, las bibliotecas son
`librsvg2-2 libcairo2 ffmpeg fonts-dejavu-core`.

```bash
python3 -m venv work/venv
work/venv/bin/pip install -r requirements.txt
work/venv/bin/python src/render.py
work/venv/bin/python src/verify.py
```

Si tu entorno ya dispone de estas dependencias, utiliza `python3 src/render.py`.
Se procesa cada SVG a 2160 × 2160 y se reduce con Lanczos antes de codificar
el video de 1080 × 1080 a CRF 16. La exportación tiene inicio rápido para web.

```bash
# Máster adicional de 2160 × 2160, con la misma geometría y timing
python3 src/render.py --size 2160 --supersample 1 --crf 14 \
  --skip-qa --output deliverables/ji-afk-cinematic-logo-animation-2160.mp4
```

Para modificar la animación, edita las curvas en `src/logo.py`, las poses en
`src/timeline.json` y los pasos de construcción en `src/animate.py`; después
ejecuta el render. El SVG de `assets/` se regenera desde `logo.py`, por lo que
los cambios dibujados directamente en Inkscape deben trasladarse a esa fuente
antes de ejecutar el generador.

Para guardar cualquier instante como vector editable:

```bash
PYTHONPATH=src python3 -c 'from animate import frame; open("work/pose.svg","w").write(frame(2.28))'
```

## Dirección y fidelidad

0–0.85 s: cruz, espiral y ornamentos se construyen en espacio negativo.
0.85–2.7 s: dos inclinaciones de ritmo diferente, ojos con parallax y orejas
con retraso. 2.7–3.12 s: compresión moderada y anticipación. 3.08–3.85 s:
revelación mediante una lente vectorial expansiva y asentamiento.
3.92–5.25 s: escritura de J, I, A, F y K mediante pases independientes de
máscara que recorren los glifos originales. 5.12–5.78 s: construcción discreta
del subtítulo. Desde 5.85 s hasta el cierre: marca estable durante 2.15 s.

La imagen oficial visible en el chat es la referencia visual; no apareció una
copia binaria de `01-50910.png` entre los archivos montados. La reconstrucción
se realizó manualmente por observación de esa imagen, sin vectorización
automática ni sustitución tipográfica. La verificación de fidelidad es visual;
no se afirma igualdad de píxeles contra un PNG original no disponible en disco.
Los recursos existentes del repositorio se inspeccionaron y no contenían este
emblema. Se conserva el dibujo, la asimetría, los ojos, los remates, la paleta
y los textos exactos. Se limpió el ruido fotográfico en favor de curvas suaves.

El video cuadrado encaja la composición completa sin deformarla; añade margen
rosado arriba y abajo. No usa un PNG como plano animado: todos los fotogramas
proceden de máscaras y geometría vectorial editable.

## Alcance e historial

Todo el trabajo está aislado en `motion/ji-afk-cinematic-logo/` de Ji-Assets.
No se modificaron los demás recursos. Véanse `CHANGELOG.md`, `qa/QA.md` y
`qa/verification.json` para revisiones y evidencia. El paquete de entrega
incluye fuentes, dependencias, SVG, videos y capturas; excluye archivos
temporales y entornos virtuales.
