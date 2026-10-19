# JI AFK CINEMATIC · V2

**Entrega actual: [MP4 V2 — 1080×1080, 30 fps, 7,5 s](deliverables/ji-afk-cinematic-logo-animation-v2.mp4).**
225 fotogramas renderizados desde un rig vectorial nuevo. H.264 High, yuv420p,
Rec.709, faststart y sin audio.

- [Proyecto editable V2 completo (ZIP)](deliverables/ji-afk-cinematic-logo-project-v2.zip)
- [SVG de la pose final](v2/assets/ji-afk-cinematic-v2-final.svg) · [máster por capas](v2/assets/ji-afk-cinematic-master.svg)
- [Reproductor y comparación V1/V2](v2/preview.html) — abrir localmente tras descargar el proyecto.
- [Fuentes, rig, curvas y comandos de reproducción](v2/README.md)
- [Informe visual y técnico](v2/qa/QA-V2.md) · [secuencia del impacto](v2/qa/impact-frames-078-105.jpg)
- [Comparación 0,4–2,5 s](v2/qa/comparison-v1-v2-01.jpg) · [2,9–4,2 s](v2/qa/comparison-v1-v2-02.jpg) · [5–7,3 s](v2/qa/comparison-v1-v2-03.jpg)

V2 introduce proyección por profundidad y escorzo de los ojos, deformación Bézier
de orejas con inercia, dibujo de la espiral por longitud, anticipación comprimida,
revelación radial e impacto en el fotograma 90, letras con desfases individuales,
tracking del subtítulo, parpadeo y un cierre amortiguado. Las fuentes están en
`v2/src/`; su timeline está escrito en fotogramas de 30 fps.

La geometría canónica conserva la reconstrucción de la imagen oficial visible
en el chat. El binario original `01-50910.png` no estaba montado ni presente en
el repositorio: la comparación de fidelidad es visual y contra el máster SVG,
no una afirmación de igualdad de píxeles con ese PNG.

## V1 conservada

Los archivos originales sin sufijo `-v2` y los directorios raíz `src/`, `assets/`
y `qa/` corresponden a V1 (60 fps, 8 s). Permanecen intactos para comparación.
Véanse [README de V1](README-V1.md) y [reproductor V1](preview-v1.html).
La entrega vigente es V2; el ZIP V2 incluye también el MP4 V1 como referencia.

Todos los cambios se limitan a `motion/ji-afk-cinematic-logo/`, en la rama
`motion/ji-afk-cinematic-logo` y el PR #1. No se modifica `main`.
