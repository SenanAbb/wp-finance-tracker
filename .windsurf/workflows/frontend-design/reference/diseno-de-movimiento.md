# Diseño de movimiento

## Duración: regla 100/300/500

El timing importa más que el easing. Estas duraciones suelen funcionar:

| Duración | Caso de uso | Ejemplos |
|----------|-------------|----------|
| **100-150ms** | Feedback instantáneo | Press de botón, toggle, cambio de color |
| **200-300ms** | Cambios de estado | Abrir menú, tooltip, hover |
| **300-500ms** | Cambios de layout | Acordeón, modal, drawer |
| **500-800ms** | Entradas | Carga, hero reveals |

Las salidas son más rápidas que las entradas (~75%).

## Easing: elige la curva correcta

No uses `ease` por defecto. Usa:

| Curva | Para | CSS |
|------|------|-----|
| **ease-out** | Entradas | `cubic-bezier(0.16, 1, 0.3, 1)` |
| **ease-in** | Salidas | `cubic-bezier(0.7, 0, 0.84, 0)` |
| **ease-in-out** | Toggles | `cubic-bezier(0.65, 0, 0.35, 1)` |

Para micro-interacciones usa curvas exponenciales:

```css
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
--ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
```

Evita bounce/elastic: se sienten anticuadas.

## Solo anima dos propiedades

Solo **transform** y **opacity**. Para altura (acordeón), usa `grid-template-rows: 0fr → 1fr` en lugar de animar `height`.

## Stagger

Usa custom properties:

`animation-delay: calc(var(--i, 0) * 50ms)` con `style="--i: 0"`. Cap total stagger: 10 ítems * 50ms = 500ms.

## Reduced motion

No es opcional.

```css
.card { animation: slide-up 500ms ease-out; }

@media (prefers-reduced-motion: reduce) {
  .card { animation: fade-in 200ms ease-out; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Preservar animaciones funcionales (spinners/progreso) pero sin movimiento espacial.

## Rendimiento percibido

Importa cómo se siente. Umbral 80ms: bajo eso se siente instantáneo.

- Inicio preventivo (skeletons)
- Finalización temprana (progresivo)
- UI optimista

Easing afecta duración percibida: ease-in hacia el final puede sentirse más corto.

Cuidado: respuestas demasiado rápidas pueden reducir confianza en operaciones complejas.

## Performance

No uses `will-change` preemptivo. Para animaciones por scroll usa Intersection Observer, no eventos scroll. Crea motion tokens (duraciones, easing).

---

**Evita**: animar todo. >500ms en feedback. Ignorar reduced motion. Usar animación para esconder cargas lentas.
