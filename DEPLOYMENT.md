# 🚀 Guía de Deployment en Coolify

Esta guía te ayudará a desplegar el SS-4 Form Filler System en tu servidor Coolify.

---

## 📋 Pre-requisitos

- Servidor con Coolify instalado
- Acceso al panel de Coolify
- Archivo PDF del formulario SS-4 (1_updated_fss4.pdf)
- Repositorio GitHub configurado

---

## 🐳 Opción 1: Deployment con Docker (Recomendado)

### Paso 1: Crear directorios en el servidor

Antes de desplegar, necesitas crear los directorios necesarios y subir el template del formulario:

```bash
# SSH a tu servidor
ssh tu-usuario@tu-servidor

# Crear directorios
mkdir -p /opt/ss4-form-filler/templates
mkdir -p /opt/ss4-form-filler/outputs

# Subir tu PDF template (desde tu máquina local)
# En tu máquina local:
scp 1_updated_fss4.pdf tu-usuario@tu-servidor:/opt/ss4-form-filler/templates/
```

### Paso 2: Configurar en Coolify

1. **Crear nueva aplicación:**
   - En Coolify, ve a "Resources" → "New"
   - Selecciona "Docker Compose"

2. **Configurar el repositorio:**
   - Repository: `https://github.com/camilocuadros/ss4-generator-claude`
   - Branch: `main`
   - Build Pack: Docker Compose

3. **Configurar variables de entorno:**

   En la sección "Environment Variables", agrega:

   ```env
   TEMPLATE_PATH=/app/templates/1_updated_fss4.pdf
   MAPPING_PATH=/app/ss4_field_mapping.json
   OUTPUT_DIR=/app/outputs
   ```

4. **Configurar volúmenes:**

   En la configuración de Docker Compose, asegúrate de tener estos volúmenes:

   ```yaml
   volumes:
     - /opt/ss4-form-filler/templates:/app/templates
     - /opt/ss4-form-filler/outputs:/app/outputs
   ```

5. **Puerto expuesto:**
   - Puerto interno: `8000`
   - Puerto público: El que prefieras (ej: `8080`) o usa el dominio de Coolify

6. **Desplegar:**
   - Click en "Deploy"
   - Espera a que se complete el build

---

## 🌐 Opción 2: Deployment con Dockerfile simple

Si prefieres usar solo el Dockerfile en lugar de docker-compose:

### En Coolify:

1. **Crear nueva aplicación:**
   - Resources → New → Dockerfile

2. **Configurar:**
   - Repository: `https://github.com/camilocuadros/ss4-generator-claude`
   - Dockerfile Location: `./Dockerfile`
   - Port: `8000`

3. **Variables de entorno:**
   ```env
   TEMPLATE_PATH=/app/templates/1_updated_fss4.pdf
   MAPPING_PATH=/app/ss4_field_mapping.json
   OUTPUT_DIR=/app/outputs
   ```

4. **Persistent Storage (Volúmenes):**
   - Source: `/opt/ss4-form-filler/templates`
   - Destination: `/app/templates`
   - Add another:
   - Source: `/opt/ss4-form-filler/outputs`
   - Destination: `/app/outputs`

---

## 🔧 Configuración Post-Deployment

### 1. Verificar el health check

Una vez desplegado, verifica que la API esté funcionando:

```bash
curl https://tu-dominio.com/health
```

Deberías recibir:
```json
{"status": "healthy"}
```

### 2. Probar los endpoints

```bash
# Ver la documentación de la API
https://tu-dominio.com/docs

# Endpoint raíz
curl https://tu-dominio.com/
```

### 3. Configurar dominio (Opcional)

En Coolify, puedes configurar un dominio personalizado:
- Ve a tu aplicación
- Settings → Domains
- Agrega tu dominio: `ss4-api.tudominio.com`
- Coolify configurará automáticamente SSL con Let's Encrypt

---

## 🔐 Configuración de CORS

Si vas a usar un frontend desde otro dominio, actualiza las configuraciones de CORS en el código:

En `api_ss4_filler.py`, cambia:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto por tu dominio frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

A:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tu-frontend.com",
        "https://www.tu-frontend.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoreo y Logs

### Ver logs en Coolify:
1. Ve a tu aplicación
2. Click en "Logs"
3. Verás los logs en tiempo real

### Logs útiles para debug:
```bash
# Dentro del contenedor
docker exec -it ss4-form-filler-api sh
cd /app
ls -la templates/  # Verificar que el template existe
ls -la outputs/    # Ver PDFs generados
```

---

## 🔄 Actualizaciones

Para actualizar la aplicación después de hacer cambios:

1. **Hacer push a GitHub:**
   ```bash
   git add .
   git commit -m "Update: descripción del cambio"
   git push origin main
   ```

2. **En Coolify:**
   - Ve a tu aplicación
   - Click en "Redeploy"
   - Coolify hará pull del código nuevo y reconstruirá

---

## 🐛 Troubleshooting

### Problema: Template PDF not found

**Solución:**
```bash
# Verificar que el archivo existe en el servidor
ssh tu-servidor
ls -la /opt/ss4-form-filler/templates/

# Si no está, súbelo:
scp 1_updated_fss4.pdf usuario@servidor:/opt/ss4-form-filler/templates/
```

### Problema: Permission denied en directorios

**Solución:**
```bash
# En el servidor
sudo chown -R 1000:1000 /opt/ss4-form-filler/
sudo chmod -R 755 /opt/ss4-form-filler/
```

### Problema: pdftk not found

**Solución:**
El Dockerfile ya incluye la instalación de pdftk. Si hay problemas:
1. Verifica que el build se completó correctamente
2. Revisa los logs de build en Coolify

### Problema: API no responde

**Verificaciones:**
1. Check health endpoint: `curl https://tu-dominio.com/health`
2. Revisar logs en Coolify
3. Verificar que el puerto 8000 está expuesto correctamente
4. Verificar variables de entorno

---

## 📈 Escalabilidad

### Para mayor tráfico:

1. **Aumentar recursos en Coolify:**
   - Settings → Resources
   - Aumenta CPU/RAM según necesites

2. **Habilitar múltiples réplicas:**
   ```yaml
   # En docker-compose.yml
   services:
     ss4-api:
       deploy:
         replicas: 3  # Múltiples instancias
   ```

3. **Load Balancer:**
   - Coolify maneja esto automáticamente si usas réplicas

---

## 🔐 Seguridad en Producción

### 1. Variables de entorno sensibles

Si tienes API keys u otros secretos:
- Usa la sección "Secrets" en Coolify
- No los pongas en código

### 2. Rate Limiting

Considera agregar rate limiting para prevenir abuso:

```python
# Instala: pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/fill-form")
@limiter.limit("10/minute")
async def fill_form(...):
    ...
```

### 3. HTTPS

- Coolify configura automáticamente Let's Encrypt SSL
- Asegúrate de que está habilitado en Settings → SSL

---

## 📝 Estructura de archivos en el servidor

```
/opt/ss4-form-filler/
├── templates/
│   └── 1_updated_fss4.pdf       # Template del formulario
└── outputs/
    └── ss4_filled_*.pdf         # PDFs generados (temporal)
```

---

## 🎯 URLs finales

Después del deployment tendrás:

- **API Base**: `https://tu-dominio.com/`
- **Health Check**: `https://tu-dominio.com/health`
- **API Docs (Swagger)**: `https://tu-dominio.com/docs`
- **Fill Form Endpoint**: `POST https://tu-dominio.com/api/fill-form`
- **Download Endpoint**: `GET https://tu-dominio.com/api/download/{file_id}`

---

## ✅ Checklist de Deployment

- [ ] Servidor Coolify listo
- [ ] Repositorio GitHub configurado
- [ ] Directorios creados en el servidor (`/opt/ss4-form-filler/`)
- [ ] Template PDF subido al servidor
- [ ] Aplicación creada en Coolify
- [ ] Variables de entorno configuradas
- [ ] Volúmenes configurados
- [ ] Build completado exitosamente
- [ ] Health check passing
- [ ] Dominio configurado (opcional)
- [ ] SSL habilitado
- [ ] API docs accesible
- [ ] Endpoint de prueba funcionando

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Coolify
2. Verifica este README
3. Consulta la documentación de Coolify: https://coolify.io/docs

---

**Última actualización:** 2024-11-21
**Versión:** 1.0.0
