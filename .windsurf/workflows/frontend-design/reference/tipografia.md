# Tipografía

## Principios clásicos de tipografía

### Ritmo vertical

Tu `line-height` debería ser la unidad base para TODO el espaciado vertical. Si el texto de cuerpo tiene `line-height: 1.5` con tipografía de `16px` (= 24px), los valores de espaciado deberían ser múltiplos de 24px. Esto crea armonía subconsciente: el texto y el espacio comparten una base matemática.

### Escala modular y jerarquía

El error común: demasiados tamaños de fuente demasiado cercanos entre sí (14px, 15px, 16px, 18px...). Esto crea una jerarquía confusa.

**Usa menos tamaños con más contraste.** Un sistema de 5 tamaños cubre la mayoría de casos:

| Rol | Proporción típica | Caso de uso |
|------|---------------|----------|
| xs | 0.75rem | Leyendas, legal |
| sm | 0.875rem | UI secundaria, metadatos |
| base | 1rem | Texto de cuerpo |
| lg | 1.25-1.5rem | Subtítulos, texto “lead” |
| xl+ | 2-4rem | Titulares, texto hero |

Ratios populares: 1.25 (tercera mayor), 1.333 (cuarta justa), 1.5 (quinta justa). Elige uno y comprométete.

### Legibilidad y medida

Usa unidades `ch` para medida basada en caracteres (`max-width: 65ch`). El `line-height` escala inversamente con la longitud de línea: columnas estrechas necesitan interlineado más apretado; columnas anchas necesitan más.

**No obvio**: Aumenta el `line-height` para texto claro sobre fondos oscuros. El peso percibido es menor, así que el texto necesita más “aire”. Suma 0.05-0.1 a tu `line-height` habitual.

## Selección de fuentes y emparejado

### Elegir fuentes distintivas

**Evita los defaults invisibles**: Inter, Roboto, Open Sans, Lato, Montserrat. Están en todas partes y hacen que el diseño se sienta genérico. Sirven para documentación o herramientas donde la personalidad no es el objetivo, pero si quieres diseño distintivo, busca alternativas.

**Mejores alternativas en Google Fonts**:

- En vez de Inter → **Instrument Sans**, **Plus Jakarta Sans**, **Outfit**
- En vez de Roboto → **Onest**, **Figtree**, **Urbanist**
- En vez de Open Sans → **Source Sans 3**, **Nunito Sans**, **DM Sans**
- Para un look editorial/premium → **Fraunces**, **Newsreader**, **Lora**

**Las fuentes de sistema están infravaloradas**: `-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui` se ve nativo, carga instantáneo y es muy legible. Considera esto para apps donde rendimiento > personalidad.

### Principios de emparejado

**La verdad no obvia**: a menudo no necesitas una segunda fuente. Una familia bien elegida en múltiples pesos crea una jerarquía más limpia que dos tipografías compitiendo. Añade una segunda fuente solo cuando necesites contraste real (por ejemplo, titulares display + cuerpo serif).

Al emparejar, busca contraste en múltiples ejes:

- Serif + Sans (contraste estructural)
- Geométrica + Humanista (contraste de personalidad)
- Display condensada + cuerpo ancho (contraste de proporción)

**Nunca emparejes fuentes que sean similares pero no idénticas** (por ejemplo, dos sans geométricas). Generan tensión visual sin jerarquía clara.

### Carga de fuentes web

El problema del “layout shift”: las fuentes cargan tarde, el texto se refluye y el usuario ve “saltos”. Solución:

```css
/* 1. Usa font-display: swap para visibilidad */
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2');
  font-display: swap;
}

/* 2. Ajusta métricas del fallback para minimizar el shift */
@font-face {
  font-family: 'CustomFont-Fallback';
  src: local('Arial');
  size-adjust: 105%;        /* Escala para igualar x-height */
  ascent-override: 90%;     /* Igualar altura de ascendentes */
  descent-override: 20%;    /* Igualar profundidad de descendentes */
  line-gap-override: 10%;   /* Igualar espaciado */
}

body {
  font-family: 'CustomFont', 'CustomFont-Fallback', sans-serif;
}
```

Herramientas como [Fontaine](https://github.com/unjs/fontaine) calculan estos overrides automáticamente.

## Tipografía web moderna

### Tipografía fluida

Usa `clamp(min, preferred, max)` para tipografía fluida. El valor central (por ejemplo, `5vw + 1rem`) controla la tasa de escalado: más `vw` = escalado más rápido. Añade un offset en `rem` para que no colapse a 0 en pantallas pequeñas.

**Cuándo NO usar tipografía fluida**: texto de botones, labels, elementos de UI (deben ser consistentes), texto muy corto o cuando necesites control preciso por breakpoints.

### Features OpenType

Muchos desarrolladores no saben que existen. Úsalas para pulir:

```css
/* Números tabulares para alinear datos */
.data-table { font-variant-numeric: tabular-nums; }

/* Fracciones correctas */
.recipe-amount { font-variant-numeric: diagonal-fractions; }

/* Small caps para abreviaturas */
abbr { font-variant-caps: all-small-caps; }

/* Desactivar ligaduras en código */
code { font-variant-ligatures: none; }

/* Habilitar kerning (suele venir por defecto, pero explícitalo) */
body { font-kerning: normal; }
```

Comprueba qué features soporta tu fuente en [Wakamai Fondue](https://wakamaifondue.com/).

## Arquitectura de un sistema tipográfico

Nombra tokens de forma semántica (`--text-body`, `--text-heading`), no por valor (`--font-size-16`). Incluye stacks, escala de tamaños, pesos, line-heights y letter-spacing en tu sistema de tokens.

## Consideraciones de accesibilidad

Más allá de ratios de contraste (bien documentados), considera:

- **Nunca desactivar el zoom**: `user-scalable=no` rompe accesibilidad. Si tu layout se rompe al 200% de zoom, arregla el layout.
- **Usa rem/em para tamaños**: respeta configuración del navegador. Nunca `px` para texto de cuerpo.
- **Mínimo 16px de cuerpo**: menor que esto fatiga la vista y falla WCAG en móvil.
- **Objetivos táctiles adecuados**: enlaces de texto necesitan padding o line-height que cree targets de 44px+.

---

**Evita**: más de 2-3 familias tipográficas por proyecto. Omitir fallbacks. Ignorar rendimiento de carga (FOUT/FOIT). Usar fuentes decorativas para texto de cuerpo.
