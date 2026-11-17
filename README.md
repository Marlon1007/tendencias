# Taller Docker: Flask y PostgreSQL

Aplicación educativa que guarda textos en PostgreSQL y los muestra del más reciente al más antiguo. Cada envío agrega un registro. Conserva la página original e incorpora un formulario sin JavaScript.

## Desplegar en el servidor de clase

Requisitos: Docker Engine y el plugin Docker Compose. Copia el proyecto al servidor y ejecuta los comandos desde su directorio.

1. Prepara la configuración:

   ```bash
   cp .env.example .env
   ```

   Edita `.env` y asigna una contraseña propia a `POSTGRES_PASSWORD`. No subas este archivo a Git ni lo compartas. `POSTGRES_DB` y `POSTGRES_USER` identifican la base de datos y el usuario que inicializa PostgreSQL. La contraseña es obligatoria; Compose rechazará una configuración vacía.

2. Valida y despliega:

   ```bash
   docker compose -f dockercompose.yml config --quiet
   docker compose -f dockercompose.yml up --build -d
   ```

3. Comprueba los servicios y consulta sus logs:

   ```bash
   docker compose -f dockercompose.yml ps
   docker compose -f dockercompose.yml logs --tail=100 app db
   ```

4. Abre `http://IP_DEL_SERVIDOR:5000`. El puerto 5000 debe estar disponible y permitido en el firewall del servidor. Si está ocupado, cambia únicamente el puerto del anfitrión, por ejemplo `5001:5000`, y abre el puerto 5001.

El contenedor de la app espera al healthcheck de PostgreSQL y crea la tabla `messages` si todavía no existe. El comando de la imagen ejecuta `python app.py`, como en el taller original; usa el servidor integrado de Flask. La app no incluye autenticación: quienes accedan pueden ver y guardar textos. Un despliegue de producción requeriría un servidor WSGI y las medidas de acceso correspondientes.

## Red y volumen

- `app` y `db` comparten la red `app_network` de tipo `bridge`. Compose crea la red automáticamente.
- La app usa `DB_HOST=db` y `DB_PORT=5432`: `db` es el nombre DNS del servicio dentro de esa red. `localhost` apuntaría al propio contenedor de la app.
- Solo la app publica un puerto: `5000:5000`. PostgreSQL no publica el 5432 en el servidor.
- El volumen nombrado `postgres_data` se monta exclusivamente en `/var/lib/postgresql/data` de `db` (imagen `postgres:17`). La app no tiene volúmenes ni montajes del código.
- Compose normalmente antepone el nombre del proyecto a red y volumen. Mantén el mismo directorio o nombre de proyecto al recrear los servicios para reutilizar el volumen.

La app recibe las credenciales por variables de entorno y usa consultas SQL parametrizadas. PostgreSQL inicializa sus credenciales solamente cuando el volumen está vacío: editar `.env` después no cambia la contraseña de una base ya existente.

## Detener y comprobar persistencia

1. Guarda dos textos desde la página y recárgala.
2. Elimina los contenedores y la red, conservando el volumen:

   ```bash
   docker compose -f dockercompose.yml down
   ```

3. Vuelve a crearlos:

   ```bash
   docker compose -f dockercompose.yml up --build -d
   ```

4. Abre la página y confirma que siguen apareciendo ambos textos.

**`down -v` elimina también el volumen y sus datos.** No lo uses para detener el taller si deseas conservar los registros. No cambies la versión mayor de PostgreSQL sobre un volumen existente sin preparar la migración.

## Pruebas sin desplegar

Con Python 3.14 y un entorno virtual:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Las pruebas simulan únicamente la conexión a PostgreSQL: verifican listado y escape HTML, guardado parametrizado con redirección, rechazo de vacíos y errores controlados. No necesitan contenedores ni una base de datos local. La construcción de imágenes, comunicación real y persistencia se comprueban durante el despliegue en el servidor siguiendo los pasos anteriores.
