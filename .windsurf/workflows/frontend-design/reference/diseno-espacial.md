# Diseño espacial

## Sistemas de espaciado

### Usa base de 4pt, no de 8pt

Los sistemas de 8pt son demasiado “gruesos”: a menudo necesitas 12px (entre 8 y 16). Usa 4pt para granularidad: 4, 8, 12, 16, 24, 32, 48, 64, 96px.

### Nombra tokens de forma semántica

Nombra por relación (`--space-sm`, `--space-lg`), no por valor (`--spacing-8`). Usa `gap` en lugar de márgenes para el espaciado entre hermanos: elimina el colapso de márgenes y hacks de limpieza.

## Sistemas de grilla

### La grilla auto-ajustable

Usa `repeat(auto-fit, minmax(280px, 1fr))` para grids responsivas sin breakpoints. Las columnas tienen mínimo 280px; caben tantas como sea posible por fila y el espacio sobrante se reparte. Para layouts complejos, usa áreas con nombre (`grid-template-areas`) y redefínelas en breakpoints.

## Jerarquía visual

### La prueba de entornar los ojos

Difumina la vista (o haz captura y aplica blur). ¿Sigues identificando?

- El elemento más importante
- El segundo más importante
- Agrupaciones claras

Si todo se ve con el mismo peso al difuminar, tienes un problema de jerarquía.

### Jerarquía con múltiples dimensiones

No dependas solo del tamaño. Combina:

| Herramienta | Jerarquía fuerte | Jerarquía débil |
|------------|------------------|----------------|
| **Tamaño** | ratio 3:1 o más | <2:1 |
| **Peso** | Bold vs Regular | Medium vs Regular |
| **Color** | Alto contraste | Tonos similares |
| **Posición** | Arriba/izquierda | Abajo/derecha |
| **Espacio** | Rodeado de blanco | Apretado |

La mejor jerarquía usa 2-3 dimensiones a la vez: un heading más grande, más pesado y con más espacio arriba.

### Las cards no son obligatorias

Las cards se abusan. El espaciado y la alineación ya crean agrupación visual. Usa cards solo cuando:

- el contenido es realmente distinto y accionable
- los ítems necesitan comparación en grilla
- necesitas límites claros de interacción

**Nunca anides cards dentro de cards**: usa espaciado, tipografía y separadores sutiles.

## Container queries

Las viewport queries son para layouts de página. **Las container queries son para componentes**:

```css
.card-container {
  container-type: inline-size;
}

.card {
  display: grid;
  gap: var(--space-md);
}

@container (min-width: 400px) {
  .card {
    grid-template-columns: 120px 1fr;
  }
}
```

**Por qué importa**: una card en un sidebar estrecho se mantiene compacta; la misma card en el contenido principal se expande, sin hacks.

## Ajustes ópticos

Texto con `margin-left: 0` puede verse “indentado” por el espacio interno de las letras: usa margen negativo (`-0.05em`) para alinear ópticamente. Iconos centrados geométricamente a veces se ven descentrados: el icono de play suele ir un poco a la derecha; flechas hacia su dirección.

### Touch targets vs tamaño visual

Los botones pueden verse pequeños pero necesitan targets táctiles grandes (mínimo 44px). Usa padding o pseudo-elementos:

```css
.icon-button {
  width: 24px;
  height: 24px;
  position: relative;
}

.icon-button::before {
  content: '';
  position: absolute;
  inset: -10px;
}
```

## Profundidad y elevación

Crea escalas semánticas de z-index (dropdown → sticky → modal-backdrop → modal → toast → tooltip) en lugar de números arbitrarios. Para sombras, define una escala (sm → md → lg → xl).

**Insight clave**: las sombras deben ser sutiles; si se ven claramente, probablemente son demasiado fuertes.

---

**Evita**: valores de espaciado fuera de tu escala. Hacer todo el espaciado igual (la variedad crea jerarquía). Crear jerarquía solo con tamaño: combina tamaño, peso, color y espacio.
