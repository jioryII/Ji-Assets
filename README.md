# Ji-Assets

Repositorio central de multimedia (portadas, showcases, botones de redes) para los mods de la familia **Ji Cinematic**.

Su objetivo es **centralizar** todos los recursos visuales usados en los README de los mods públicos, de modo que un mismo archivo sirva para todos los repos y sea trivial actualizarlos.

## Mods que consumen estos assets

- [Ji-AFK-Cinematic](https://github.com/jioryII/Ji-AFK-Cinematic)
- [Ji-Zoom-Cinematic](https://github.com/jioryII/Ji-Zoom-Cinematic)

## Estructura

```
Ji-Assets/
├── shared/
│   └── buttons/        ← Botones de redes sociales (comunes a todos los mods)
├── ji-afk/             ← Portada + showcase de Ji AFK Cinematic
└── ji-zoom/            ← Portada + showcase de Ji Zoom Cinematic
```

### `shared/buttons/`

Botones cuadrados de 64×64 px para los enlaces sociales del encabezado de cada README:

| Archivo | Plataforma |
|---|---|
| `Discord-Button-64.png` | Discord |
| `Github-Button-64.png` | GitHub |
| `Modrinth-Button-64.png` | Modrinth |
| `Curseforge-Button-64.png` | CurseForge |
| `Kofi-Button-64.png` | Ko-fi |
| `Tiktok-Button-64.png` | TikTok |
| `Youtube-Button-64.png` | YouTube |

### `ji-afk/`

- `portada-ji-afk.png` — Imagen de portada del README.
- `showcase-ji-afk.gif` — GIF de muestra del comportamiento del mod.

### `ji-zoom/`

- `portada-ji-zoom.png` — Imagen de portada del README (recomprimida, <600 KB).
- `showcase-ji-zoom.webp` — Video de muestra en formato WebP animado.

## Cómo referenciar desde un README

Usar la URL raw de la rama `main`:

```
https://raw.githubusercontent.com/jioryII/Ji-Assets/main/<carpeta>/<archivo>
```

Ejemplos:

```markdown
![portada](https://raw.githubusercontent.com/jioryII/Ji-Assets/main/ji-afk/portada-ji-afk.png)
<img src="https://raw.githubusercontent.com/jioryII/Ji-Assets/main/shared/buttons/Discord-Button-64.png" width="7%">
```

## Notas

- Las portadas están optimizadas para pesar menos de **600 KB** manteniendo el formato original.
- Las carpetas de cada mod NO mezclan contenido: cada una es independiente, salvo los botones compartidos en `shared/buttons/`.
- Si agregas un nuevo mod, crea su carpeta dedicada (p. ej. `ji-<nombre>/`) y reutiliza `shared/buttons/`.
