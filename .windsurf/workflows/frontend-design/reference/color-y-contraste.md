# Color y contraste

## Espacios de color: usa OKLCH

**Deja de usar HSL.** Usa OKLCH (o LCH). Es perceptualmente uniforme: pasos iguales de luminosidad *se ven* iguales, a diferencia de HSL donde 50% de luminosidad en amarillo se ve brillante y 50% en azul se ve oscuro.

```css
/* OKLCH: lightness (0-100%), chroma (0-0.4+), hue (0-360) */
--color-primary: oklch(60% 0.15 250);        /* Azul */
--color-primary-light: oklch(85% 0.08 250);  /* Mismo tono, más claro */
--color-primary-dark: oklch(35% 0.12 250);   /* Mismo tono, más oscuro */
```

**Insight clave**: al acercarte a blanco o negro, reduce el chroma (saturación). Chroma alto en luminosidad extrema se ve estridente. Un azul claro a 85% necesita ~0.08 chroma, no el 0.15 del color base.

## Construir paletas funcionales

### La trampa de los neutros tintados

**El gris puro está muerto.** Añade un toque sutil del tono de marca a los neutros:

```css
/* Grises muertos */
--gray-100: oklch(95% 0 0);
--gray-900: oklch(15% 0 0);

/* Grises cálidos */
--gray-100: oklch(95% 0.01 60);
--gray-900: oklch(15% 0.01 60);

/* Grises fríos */
--gray-100: oklch(95% 0.01 250);
--gray-900: oklch(15% 0.01 250);
```

El chroma es diminuto (0.01) pero perceptible: crea cohesión subconsciente.

### Estructura de paleta

Un sistema completo necesita:

| Rol | Propósito | Ejemplo |
|------|---------|---------|
| **Primario** | Marca, CTAs, acciones clave | 1 color, 3-5 tonos |
| **Neutro** | Texto, fondos, bordes | escala 9-11 tonos |
| **Semántico** | Éxito, error, warning, info | 4 colores, 2-3 tonos |
| **Superficie** | Cards, modales, overlays | 2-3 niveles |

**Evita secundario/terciario si no lo necesitas.** Un color de acento suele bastar.

### Regla 60-30-10 (bien aplicada)

Es sobre **peso visual**, no sobre píxeles:

- 60%: fondos neutros y superficies base
- 30%: secundarios (texto, bordes, inactivos)
- 10%: acento (CTAs, highlights, focus)

Error común: usar el acento en todas partes porque es “color de marca”. Su poder está en ser raro.

## Contraste y accesibilidad

### Requisitos WCAG

| Tipo | AA mínimo | AAA objetivo |
|------|----------|--------------|
| Texto de cuerpo | 4.5:1 | 7:1 |
| Texto grande (18px+ o 14px bold) | 3:1 | 4.5:1 |
| Componentes UI, iconos | 3:1 | 4.5:1 |
| Decoración no esencial | Ninguno | Ninguno |

**Ojo**: el placeholder también necesita 4.5:1.

### Combinaciones peligrosas

- Gris claro sobre blanco
- **Texto gris sobre fondos coloreados**: se ve lavado; usa un tono del color o transparencia
- Rojo sobre verde (o viceversa)
- Azul sobre rojo (vibra)
- Amarillo sobre blanco
- Texto fino claro sobre imágenes

### Nunca usar gris puro o negro puro

El gris puro y el negro puro no existen en la naturaleza. Un chroma de 0.005-0.01 basta para sentirse natural.

### Testing

No confíes en tus ojos:

- WebAIM Contrast Checker
- DevTools: emular deficiencias de visión
- Polypane

## Theming: modo claro y oscuro

### Dark mode no es invertir light mode

No basta con intercambiar colores. Dark mode requiere decisiones distintas:

| Claro | Oscuro |
|------|--------|
| Sombras para profundidad | Superficies más claras (sin sombras) |
| Texto oscuro sobre claro | Texto claro sobre oscuro (bajar peso) |
| Acentos vibrantes | Desaturar acentos ligeramente |
| Fondos blancos | Nunca negro puro (usar gris oscuro 12-18% OKLCH) |

```css
:root[data-theme="dark"] {
  --surface-1: oklch(15% 0.01 250);
  --surface-2: oklch(20% 0.01 250);
  --surface-3: oklch(25% 0.01 250);

  --body-weight: 350;
}
```

### Jerarquía de tokens

Dos capas: tokens primitivos (`--blue-500`) y semánticos (`--color-primary`). En dark mode redefine solo la capa semántica.

## El alpha es “design smell”

El uso pesado de transparencia suele indicar paleta incompleta. Alpha crea contraste impredecible e inconsistencia. Excepción: focus rings y estados interactivos.

---

**Evita**: depender solo del color para comunicar. Paletas sin roles. Negro puro (#000) en grandes áreas. No probar daltonismo.
