# Datecsa Garantías — Visión Ejecutiva

**Sistema de gestión inteligente de garantías de equipos tecnológicos**

---

## El problema que resuelve

Datecsa gestiona garantías de equipos de alto valor (impresoras Kyocera, sistemas audiovisuales Barco, equipos de sala Crestron, sonido Bose Professional, señalización LG) para clientes corporativos en Colombia. El proceso actual tiene tres fallas estructurales:

### 1. Sin trazabilidad del equipo
Cuando un equipo sale hacia el proveedor para reparación, nadie sabe con certeza dónde está en cada momento. ¿Llegó? ¿Está en diagnóstico? ¿Ya fue reparado y está esperando despacho? La respuesta depende de que alguien recuerde enviar un correo.

### 2. Todo el flujo vive en el correo de una persona
El proceso completo — coordinar con el proveedor, avisar al cliente, gestionar el retorno del equipo, notificar a bodega y despacho — depende de que un técnico o coordinador lea su bandeja de entrada y actúe manualmente. Si esa persona está en vacaciones, enferma, o simplemente recibe muchos correos ese día, el caso se retrasa o se pierde.

### 3. Sin visibilidad para el cliente ni para la gerencia
No existe un registro consolidado de cuántos equipos están en garantía activa, cuánto tiempo llevan, qué porcentaje se resuelve dentro del tiempo prometido, ni cuáles proveedores responden peor. La gerencia solo se entera del problema cuando el cliente ya está molesto.

---

## Cómo funciona el sistema

### El flujo completo en términos simples

```
                    ANTES                          AHORA
                    ─────                          ────
Falla reportada →  Técnico anota en papel    →  Sistema registra al instante
                   y luego envía correo         con número de caso y serial

Equipo enviado →   Coordinador recuerda       →  Sistema actualiza ubicación
al proveedor       (o no) enviar correo          automáticamente

Sin noticias →     Nadie sabe cuántos          →  Sistema detecta los casos
                   días llevan sin respuesta      sin respuesta y genera
                                                  correo de seguimiento listo
                                                  para aprobar y enviar

Equipo vuelve →    Técnico avisa por correo    →  Sistema recibe el correo
                   a bodega, despacho,            del proveedor, lo clasifica
                   cliente, responsable           y genera los 4 correos
                                                  necesarios automáticamente
```

### El agente de inteligencia artificial

El corazón del sistema es un **agente de IA** que lee los correos entrantes y toma decisiones. Cuando llega un correo de un proveedor diciendo "el equipo fue reparado y despachado hoy", el agente:

1. Identifica de qué equipo se trata (por el serial o el asunto)
2. Actualiza el estado del caso en el sistema
3. Genera automáticamente los correos que deben salir: a bodega para que estén listos, a despacho para coordinar la recepción, al cliente para avisarle, y al responsable del caso
4. Pone esos correos en cola para que un coordinador los revise y apruebe con un clic

**El agente nunca envía correos por su cuenta.** Todo pasa por revisión humana antes de salir — esto garantiza que el tono sea el correcto y que no haya errores.

### Los tres momentos clave del sistema

**1. Cuando entra una falla**
Un técnico puede subir el acta de entrega en PDF. El sistema la lee, extrae el serial del equipo, verifica que esté en garantía, crea el caso y notifica al coordinador responsable. Lo que antes tomaba enviar varios correos y esperar confirmación, ahora toma segundos.

**2. Durante el proceso con el proveedor**
Cada correo que llega del proveedor es procesado por el agente. Si el proveedor confirma recepción, el sistema actualiza el estado. Si el proveedor da un diagnóstico, queda registrado. Si el proveedor no ha respondido en 7 días, el sistema genera automáticamente un correo de seguimiento — sin que nadie tenga que recordarlo.

**3. Cuando el equipo vuelve**
Cuando el proveedor confirma que el equipo fue reparado y despachado, el sistema genera en segundos los correos para todos los involucrados. Nada se olvida, nadie se queda sin avisar.

---

## Qué ve el equipo de Datecsa

El sistema tiene un panel de control accesible desde cualquier navegador:

- **Inicio:** Vista del pipeline en tiempo real — cuántos correos tiene la bandeja, qué tipo son, cómo los está procesando el agente paso a paso
- **Casos activos:** Listado de todas las solicitudes de garantía en curso, con su estado, días transcurridos y alertas para los casos urgentes
- **Correos para aprobar:** Bandeja de borradores generados por el agente, listos para revisar y enviar con un clic
- **Buscar casos similares:** El sistema puede encontrar casos anteriores con fallas parecidas, útil para dar estimados de tiempo al cliente o detectar patrones de falla en un modelo de equipo

---

## Los beneficios concretos

### Para el coordinador de garantías
- No más rastrear casos en hilos de correo interminables
- Las alertas automáticas llegan cuando un proveedor no ha respondido — no hay que hacer seguimiento manual
- Los correos ya están redactados y listos, solo hay que revisarlos y aprobarlos

### Para el cliente corporativo
- Comunicación consistente y proactiva en cada etapa
- Tiempos de respuesta más cortos porque nada queda "entre las grietas"
- Mayor confianza en Datecsa como socio tecnológico

### Para la gerencia
- Visibilidad completa de todos los casos en tiempo real
- Datos para medir el desempeño de cada proveedor (tiempo de diagnóstico, tiempo de reparación, tasa de cumplimiento)
- Evidencia concreta del valor del servicio postventa de Datecsa frente a la competencia

---

## Escala y madurez del sistema

El sistema fue desarrollado como prueba de concepto funcional (POC) con arquitectura diseñada para crecer:

| Capacidad actual | Capacidad futura |
|-----------------|-----------------|
| 5 equipos en base de datos de demostración | Miles de equipos y casos históricos |
| Bandeja de correos simulada | Conexión directa a correo corporativo (OAuth2) |
| Proveedor de IA configurable | Posibilidad de cambiar entre modelos de IA según costo/precisión |
| Un usuario de demostración | Roles diferenciados: coordinador, técnico, aprobador, gerencia |

El sistema corre sobre tecnología estándar del mercado (PostgreSQL, Python, React), no genera dependencia de un proveedor propietario, y puede desplegarse en la infraestructura existente de Datecsa o en la nube.

---

## Por qué este enfoque y no una solución genérica de CRM o ERP

Los CRM y ERP existentes gestionan tickets y casos, pero no entienden el contenido de los correos — alguien siempre tiene que leer el correo del proveedor y actualizar el sistema manualmente. Este sistema hace esa lectura e interpretación automáticamente.

La diferencia es el agente de IA especializado en el vocabulario y los procesos específicos de Datecsa: conoce los modelos de equipo, las marcas que distribuye, los seriales, y las etapas del proceso de garantía. No es un bot genérico — es un asistente entrenado en el negocio de Datecsa.

---

## Próximos pasos sugeridos

1. **Piloto con casos reales:** Correr el sistema en paralelo con el proceso actual durante 4 semanas, comparando tiempo de respuesta y correos perdidos
2. **Conexión al correo corporativo:** Migrar de bandeja simulada a la cuenta de correo real del área de garantías (requiere configuración OAuth2 con el proveedor de correo)
3. **Integración con Gemini en producción:** El sistema ya tiene el proveedor de IA conectado — activar para clasificación real de correos entrantes y generación de correos con el contexto del caso
4. **Dashboard gerencial:** Añadir métricas agregadas: SLA por proveedor, tiempo promedio de resolución, volumen por tipo de equipo
