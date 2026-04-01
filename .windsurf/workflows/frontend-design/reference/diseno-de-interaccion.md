# Diseño de interacción

## Los ocho estados interactivos

Todo elemento interactivo necesita estos estados:

| Estado | Cuándo | Tratamiento visual |
|-------|--------|--------------------|
| **Default** | En reposo | Estilo base |
| **Hover** | Puntero encima (no touch) | Lift sutil, cambio de color |
| **Focus** | Foco teclado/programático | Anillo visible |
| **Active** | Presionando | Más “hundido”, más oscuro |
| **Disabled** | No interactivo | Menos opacidad, sin puntero |
| **Loading** | Procesando | Spinner, skeleton |
| **Error** | Estado inválido | Borde rojo, icono, mensaje |
| **Success** | Completado | Check verde, confirmación |

**Fallo común**: diseñar hover sin focus (o al revés). El usuario de teclado nunca ve hover.

## Focus rings: hacerlo bien

**Nunca uses `outline: none` sin reemplazo.** Es una violación de accesibilidad. Usa `:focus-visible`:

```css
button:focus {
  outline: none;
}

button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
```

Diseño del focus ring:
- Alto contraste (mínimo 3:1)
- 2-3px
- Separado del elemento
- Consistente en todos los interactivos

## Formularios: lo no obvio

Los placeholders no son labels: desaparecen. Usa `<label>` visibles. Valida en blur, no en cada pulsación (salvo fuerza de password). Errores debajo del campo con `aria-describedby`.

## Estados de carga

UI optimista: muestra éxito inmediato y revierte si falla (para acciones de bajo riesgo). Skeletons > spinners: anticipan forma y se sienten más rápidos.

## Modales: enfoque inert

Usa `inert`:

```html
<main inert>
  <!-- Contenido detrás del modal no recibe foco ni clic -->
</main>
<dialog open>
  <h2>Título</h2>
</dialog>
```

O `<dialog>` nativo:

```js
const dialog = document.querySelector('dialog');
dialog.showModal();
```

## Popover API

```html
<button popovertarget="menu">Abrir menú</button>
<div id="menu" popover>
  <button>Opción 1</button>
  <button>Opción 2</button>
</div>
```

Beneficios: light-dismiss, stacking correcto, sin guerras de z-index, accesible.

## Acciones destructivas: Undo > Confirm

Undo es mejor que confirmaciones (la gente las “clickea” sin pensar). Quita del UI, muestra toast Undo, borra realmente al expirar. Confirmación solo para acciones irreversibles o de alto coste.

## Patrones de teclado

### Roving tabindex

```html
<div role="tablist">
  <button role="tab" tabindex="0">Tab 1</button>
  <button role="tab" tabindex="-1">Tab 2</button>
  <button role="tab" tabindex="-1">Tab 3</button>
</div>
```

Las flechas mueven el `tabindex="0"`.

### Skip links

Proveer `<a href="#main-content">Saltar al contenido</a>` para saltar navegación. Oculto off-screen, visible en focus.

## Descubribilidad de gestos

Gestos tipo swipe-to-delete son invisibles. Pistas:

- Revelado parcial
- Onboarding
- Fallback visible (menú con “Eliminar”)

No dependas de gestos como única vía.

---

**Evita**: quitar foco sin alternativa. Placeholder como label. Touch targets <44x44. Errores genéricos. Controles custom sin ARIA/teclado.
