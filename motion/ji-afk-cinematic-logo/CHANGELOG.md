# Historial

## 2.0.0 · 19 de octubre de 2026

- Nueva animación nativa de 225 fotogramas a 30 fps y 7,5 segundos.
- Rig 2.5D con escorzo y oclusión de ojos, deformación Bézier y orejas con inercia.
- Dibujo real de espiral, giro y sobrepaso del +, anticipación comprimida e impacto en f90.
- Letras por trazos y desfase, tracking central, parpadeo y cierre amortiguado.
- Render con sobremuestreo espacial 2× y seis submuestras temporales selectivas.
- Revisión visual: se sustituyeron los extremos planos de las orejas, se eliminaron
  puntos prematuros de entrada y se corrigió la unión del hocico durante el yaw.
- Comparación V1/V2 en doce tiempos, tira del impacto, 225 fotogramas inspeccionables,
  reproducción completa en Chromium y controles de regeneración.
- V1 preservada; V2 se entrega en archivos con sufijo y fuentes en `v2/`.

## 1.0.0 · 19 de octubre de 2026

- Reconstrucción manual de curvas Bézier, cruz, espiral y tipografía trazada.
- Rig vectorial: capas, pivotes, parallax, reacción de orejas y anticipación.
- Revelación por máscaras y construcción de cada letra por pases geométricos.
- Revisión 1: inspección de la reconstrucción a resolución completa y de las
  primeras diez fases. Ajuste de las uniones de la nariz.
- Revisión 2: MP4 completo codificado y decodificado. Corrección de líneas
  entre fragmentos de la silueta mediante regiones de solapamiento.
- Revisión 3: exportación final con sobremuestreo, controles de cobertura de
  máscaras y estabilidad, capturas desde el MP4 y documentación reproducible.
