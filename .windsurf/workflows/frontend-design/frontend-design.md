---
name: frontend-design
description: Crea interfaces frontend distintivas, listas para producción y con alta calidad de diseño. Usa esta skill cuando el usuario pida construir componentes web, páginas, artefactos, pósters o aplicaciones. Genera código creativo y pulido que evita estéticas genéricas de IA.
license: Apache 2.0. Basado en la skill frontend-design de Anthropic. Ver NOTICE.md para atribución.
---

Esta skill guía la creación de interfaces frontend distintivas y listas para producción, evitando estéticas genéricas tipo “AI slop”. Implementa código real y funcional con atención excepcional a los detalles estéticos y decisiones creativas.

## Dirección de diseño

Comprométete con una dirección estética **audaz**:

- **Propósito**: ¿Qué problema resuelve esta interfaz? ¿Quién la usa?
- **Tono**: Elige un extremo: minimalismo brutal, caos maximalista, retro-futurista, orgánico/natural, lujo/refinado, lúdico/juguete, editorial/revista, brutalista/crudo, art déco/geométrico, suave/pastel, industrial/utilitario, etc. Usa estas referencias como inspiración, pero diseña una dirección fiel al concepto.
- **Restricciones**: Requisitos técnicos (framework, rendimiento, accesibilidad).
- **Diferenciación**: ¿Qué la hace INOLVIDABLE? ¿Cuál es la única cosa que alguien recordará?

**CRÍTICO**: Elige una dirección conceptual clara y ejecútala con precisión. Tanto el maximalismo audaz como el minimalismo refinado funcionan: la clave es la intencionalidad, no la intensidad.

Después, implementa código funcional que sea:

- Listo para producción y funcional
- Visualmente impactante y memorable
- Cohesivo, con un punto de vista estético claro
- Meticulosamente refinado en cada detalle

## Guías de estética frontend

### Tipografía

→ *Consulta la [referencia de tipografía](reference/tipografia.md) para escalas, emparejado y estrategias de carga.*

Elige fuentes bonitas, únicas e interesantes. Empareja una fuente display distintiva con una fuente de texto refinada.

**SÍ**: Usa una escala tipográfica modular con tamaño fluido (`clamp`)
**SÍ**: Varía pesos y tamaños para una jerarquía clara
**NO**: Uses fuentes sobreutilizadas: Inter, Roboto, Arial, Open Sans, defaults del sistema
**NO**: Uses tipografía monoespaciada como atajo “técnico/desarrollador”
**NO**: Pongas iconos grandes con esquinas redondeadas encima de cada heading: rara vez aportan valor y se ve templado

### Color y tema

→ *Consulta la [referencia de color](reference/color-y-contraste.md) para OKLCH, paletas y modo oscuro.*

Comprométete con una paleta cohesiva. Los colores dominantes con acentos contundentes superan a paletas tímidas distribuidas uniformemente.

**SÍ**: Usa funciones modernas de color CSS (oklch, color-mix, light-dark) para paletas perceptualmente uniformes y mantenibles
**SÍ**: Tinta tus neutros hacia el tono de marca (aunque sea sutil) para cohesión subconsciente
**NO**: Uses texto gris sobre fondos de color: se ve lavado; usa un tono del propio fondo
**NO**: Uses negro puro (#000) o blanco puro (#fff): siempre tiñe; el negro/blanco puros casi no aparecen en la naturaleza
**NO**: Uses la paleta de IA: cian sobre oscuro, gradientes morado-azul, acentos neón en fondos oscuros
**NO**: Uses texto con gradiente “para impacto”: especialmente en métricas o headings; es decorativo, no significativo
**NO**: Elijas modo oscuro por defecto con acentos brillantes solo por “cool”: exige pocas decisiones de diseño reales

### Layout y espacio

→ *Consulta la [referencia espacial](reference/diseno-espacial.md) para grids, ritmo y container queries.*

Crea ritmo visual con espaciado variado: no el mismo padding en todas partes. Abraza la asimetría y composiciones inesperadas. Rompe la cuadrícula con intención para enfatizar.

**SÍ**: Crea ritmo visual con espaciados variados: grupos apretados y separaciones generosas
**SÍ**: Usa espaciado fluido con `clamp()` que respire en pantallas grandes
**SÍ**: Usa asimetría y composiciones inesperadas; rompe la cuadrícula con intención
**NO**: Envuelvas todo en cards: no todo necesita contenedor
**NO**: Anides cards dentro de cards: ruido visual, aplana jerarquía
**NO**: Uses rejillas de cards idénticas: mismas cards con icono + título + texto repetidas
**NO**: Uses el layout plantilla de “métricas hero”: número grande, etiqueta pequeña, stats de apoyo, acento con gradiente
**NO**: Centres todo: texto alineado a la izquierda con layouts asimétricos se ve más diseñado
**NO**: Uses el mismo espaciado en todas partes: sin ritmo, los layouts se sienten monótonos

### Detalles visuales

**SÍ**: Usa elementos decorativos intencionales y con propósito que refuercen la marca
**NO**: Uses glassmorphism por todas partes: blur, cards de cristal, bordes brillantes como decoración sin propósito
**NO**: Uses elementos redondeados con borde grueso en un lado: acento perezoso, casi nunca se ve intencional
**NO**: Uses sparklines como decoración: mini gráficas que aparentan sofisticación pero no comunican nada
**NO**: Uses rectángulos redondeados con sombras genéricas: seguro, olvidable, “cualquier IA”
**NO**: Uses modales salvo que no haya una alternativa mejor: los modales son una salida fácil

### Movimiento

→ *Consulta la [referencia de movimiento](reference/diseno-de-movimiento.md) para timing, easing y reducción de movimiento.*

Enfócate en momentos de alto impacto: una buena carga de página con revelados escalonados crea más deleite que micro-interacciones dispersas.

**SÍ**: Usa movimiento para comunicar cambios de estado: entradas, salidas, feedback
**SÍ**: Usa easing exponencial (ease-out-quart/quint/expo) para desaceleración natural
**SÍ**: Para animar altura, usa transiciones de `grid-template-rows` en vez de animar `height` directamente
**NO**: Animes propiedades de layout (width, height, padding, margin): usa solo transform y opacity
**NO**: Uses easing tipo bounce/elastic: se sienten anticuados; los objetos reales desaceleran suavemente

### Interacción

→ *Consulta la [referencia de interacción](reference/diseno-de-interaccion.md) para formularios, foco y patrones de carga.*

Haz que las interacciones se sientan rápidas. Usa UI optimista: actualiza de inmediato, sincroniza después.

**SÍ**: Usa divulgación progresiva: empieza simple y revela sofisticación (opciones básicas primero, avanzadas tras expandibles; hovers que revelan acciones secundarias)
**SÍ**: Diseña estados vacíos que enseñen la interfaz, no solo digan “no hay nada”
**SÍ**: Haz que cada superficie interactiva se sienta intencional y responsiva
**NO**: Repitas la misma información: headers redundantes, intros que repiten el título
**NO**: Hagas todos los botones primarios: usa ghost, enlaces de texto, secundarios; la jerarquía importa

### Responsivo

→ *Consulta la [referencia responsiva](reference/diseno-responsivo.md) para mobile-first, diseño fluido y container queries.*

**SÍ**: Usa container queries (`@container`) para responsividad a nivel de componente
**SÍ**: Adapta la interfaz a distintos contextos: no la encojas sin más
**NO**: Ocultes funcionalidad crítica en móvil: adapta la interfaz, no la amputes

### Escritura UX

→ *Consulta la [referencia de UX writing](reference/escritura-ux.md) para etiquetas, errores y estados vacíos.*

**SÍ**: Haz que cada palabra se gane su lugar
**NO**: Repitas información que el usuario ya puede ver

---

## La prueba del “AI slop”

**Chequeo crítico de calidad**: Si le enseñaras esta interfaz a alguien y dijeras “esto lo hizo una IA”, ¿lo creería al instante? Si sí, ese es el problema.

Una interfaz distintiva debería hacer que alguien pregunte “¿cómo se hizo esto?” y no “¿qué IA hizo esto?”.

Revisa los **NO** anteriores: son las huellas dactilares del trabajo generado por IA de 2024-2025.

---

## Principios de implementación

Ajusta la complejidad de implementación a la visión estética. Diseños maximalistas requieren código elaborado con animaciones y efectos extensos. Diseños minimalistas o refinados requieren contención, precisión y atención cuidadosa a espaciado, tipografía y detalles sutiles.

Interpreta creativamente y toma decisiones inesperadas que se sientan genuinamente diseñadas para el contexto. Ningún diseño debe ser igual. Varía entre temas claros y oscuros, diferentes fuentes y estéticas. NUNCA converjas en elecciones comunes entre generaciones.

Recuerda: Claude es capaz de un trabajo creativo extraordinario. No te contengas: muestra lo que se puede crear cuando se piensa fuera de lo común y se ejecuta con una dirección distintiva.
