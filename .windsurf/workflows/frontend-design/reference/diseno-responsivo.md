# Diseño responsivo

## Mobile-first: hazlo bien

Empieza con estilos base para móvil y usa queries `min-width` para añadir complejidad. Desktop-first (`max-width`) hace que móvil cargue estilos innecesarios primero.

## Breakpoints: guiados por el contenido

No persigas tamaños de dispositivos. Estira el layout hasta que se rompa: ahí va el breakpoint. Tres breakpoints suelen bastar (640, 768, 1024px). Usa `clamp()` para valores fluidos.

## Detecta método de entrada, no solo tamaño

El tamaño no indica input. Usa `pointer` y `hover`:

```css
@media (pointer: fine) {
  .button { padding: 8px 16px; }
}

@media (pointer: coarse) {
  .button { padding: 12px 20px; }
}

@media (hover: hover) {
  .card:hover { transform: translateY(-2px); }
}

@media (hover: none) {
  .card { /* sin hover; usa active */ }
}
```

**Crítico**: no dependas de hover para funcionalidad.

## Safe areas: notch

Usa `env()`:

```css
body {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

.footer {
  padding-bottom: max(1rem, env(safe-area-inset-bottom));
}
```

Meta tag:
```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

## Imágenes responsivas

### srcset con `w`

```html
<img
  src="hero-800.jpg"
  srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1200.jpg 1200w"
  sizes="(max-width: 768px) 100vw, 50vw"
  alt="Hero"
>
```

### picture para art direction

```html
<picture>
  <source media="(min-width: 768px)" srcset="wide.jpg">
  <source media="(max-width: 767px)" srcset="tall.jpg">
  <img src="fallback.jpg" alt="...">
</picture>
```

## Patrones de adaptación de layout

- Navegación: hamburguesa en móvil, horizontal compacta en tablet, completa en desktop.
- Tablas: transformar a cards en móvil (`display: block` + `data-label`).
- Divulgación progresiva: `<details>/<summary>` en móvil.

## Testing

No confíes solo en emulación. Prueba en:

- Un iPhone real
- Un Android real
- Una tablet (si aplica)

DevTools no refleja bien touch real, CPU/memoria, latencia, rendering de fuentes, teclado, etc.

---

**Evita**: desktop-first. Detección de dispositivo en vez de features. Codebases separados móvil/desktop. Ignorar tablet y landscape. Asumir móviles potentes.
