# Escritura UX

## El problema de las etiquetas de botones

**Nunca uses "OK", "Submit" o "Yes/No".** Son vagas y ambiguas. Usa patrones de verbo + objeto:

| Malo | Bueno | Por qué |
|------|-------|---------|
| OK | Guardar cambios | Dice qué pasará |
| Submit | Crear cuenta | Orientado al resultado |
| Yes | Eliminar mensaje | Confirma la acción |
| Cancel | Seguir editando | Aclara qué significa “cancelar” |
| Click here | Descargar PDF | Describe el destino |

Para acciones destructivas, nombra la destrucción:
- "Eliminar" en vez de "Quitar" (eliminar = permanente)
- "Eliminar 5 elementos" en vez de "Eliminar seleccionados" (muestra el número)

## Mensajes de error: la fórmula

Todo mensaje de error debe responder: (1) ¿Qué pasó? (2) ¿Por qué? (3) ¿Cómo se arregla?

Ejemplo: "El email no es válido. Incluye un símbolo @" en vez de "Entrada inválida".

### Plantillas de error

| Situación | Plantilla |
|----------|-----------|
| Error de formato | "[Campo] debe ser [formato]. Ejemplo: [ejemplo]" |
| Falta requerido | "Introduce [lo que falta]" |
| Sin permisos | "No tienes acceso a [cosa]. [Qué hacer]" |
| Error de red | "No pudimos conectar con [cosa]. Revisa tu conexión y [acción]." |
| Error servidor | "Algo falló de nuestro lado. Lo estamos revisando. [Acción alternativa]" |

### No culpar al usuario

Reformula: "Introduce una fecha en formato DD/MM/AAAA" en lugar de "Has introducido una fecha inválida".

## Estados vacíos = oportunidades

Los estados vacíos son onboarding: (1) reconocer, (2) explicar valor, (3) dar acción.

"Aún no hay proyectos. Crea el primero para empezar." y no solo "No hay elementos".

## Voz vs tono

**Voz**: personalidad de marca (consistente).
**Tono**: se adapta al momento.

| Momento | Cambio de tono |
|--------|----------------|
| Éxito | Celebratorio y breve: "¡Hecho! Tus cambios ya están activos." |
| Error | Empático y útil: "No ha funcionado. Prueba esto…" |
| Loading | Tranquilizador: "Guardando tu trabajo…" |
| Confirmación destructiva | Serio y claro: "¿Eliminar este proyecto? No se puede deshacer." |

**Nunca uses humor en errores.** El usuario ya está frustrado.

## Escribir para accesibilidad

- El texto de enlaces debe tener sentido por sí solo: "Ver planes" no "Haz clic aquí".
- Alt text describe la información, no la imagen: "Los ingresos subieron 40% en Q4" no "Gráfico".
- Usa `alt=""` para imágenes decorativas.
- Botones solo icono necesitan `aria-label`.

## Escribir para traducción

### Planificar expansión

| Idioma | Expansión |
|--------|-----------|
| Alemán | +30% |
| Francés | +20% |
| Finés | +30-40% |
| Chino | -30% (menos caracteres, pero anchura similar) |

### Patrones amigables a traducción

- Mantén números separados ("Mensajes nuevos: 3")
- Evita concatenaciones (el orden cambia por idioma)
- Evita abreviaturas
- Da contexto a traductores sobre dónde aparece el texto

## Consistencia: terminología

Elige un término y manténlo:

| Inconsistente | Consistente |
|--------------|------------|
| Delete / Remove / Trash | Delete |
| Settings / Preferences / Options | Settings |
| Sign in / Log in / Enter | Sign in |
| Create / Add / New | Create |

Crea un glosario y aplícalo.

## Evitar copy redundante

Si el heading lo explica, la intro sobra. Si el botón es claro, no lo expliques otra vez.

## Estados de carga

Sé específico: "Guardando borrador…" no "Cargando…". Para esperas largas, da expectativas o progreso.

## Diálogos de confirmación

Muchos confirm dialogs son fallos de diseño: considera undo. Si debes confirmar: nombra la acción, explica consecuencias, usa labels específicos.

## Instrucciones de formularios

Muestra el formato con placeholders, no con párrafos. En campos no obvios, explica por qué preguntas.

---

**Evita**: jerga sin explicación. Culpar al usuario. Errores vagos. Variar terminología “por estilo”. Humor en errores.
