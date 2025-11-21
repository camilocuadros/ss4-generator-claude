# 🚀 Guía de Deployment en Coolify

Esta guía te ayudará a desplegar el SS-4 Form Filler System en tu servidor Coolify **sin necesidad de almacenamiento persistente** en el servidor.

---

## ✨ Nueva Arquitectura: Sin Almacenamiento

**¿Cómo funciona ahora?**

El sistema genera los PDFs en memoria temporal (`/tmp`) y los envía **directamente al usuario** sin guardarlos permanentemente. Esto significa:

- ✅ **No necesitas configurar storage en la nube** (S3, R2, etc.)
- ✅ **No se almacenan archivos sensibles** en el servidor
- ✅ **Totalmente gratis** - sin costos de almacenamiento
- ✅ **Más seguro** - los PDFs se eliminan automáticamente
- ✅ **Más simple** - menos configuración

---

## 📋 Pre-requisitos

- Servidor con Coolify instalado
- Acceso al panel de Coolify
- Archivo PDF del formulario SS-4 template (solo este archivo)

---

## 🐳 Opción 1: Deployment Directo en Coolify (Recomendado)

### Paso 1: Preparar el template en el servidor

Solo necesitas subir el template del formulario SS-4:

```bash
# SSH a tu servidor
ssh tu-usuario@tu-servidor

# Crear directorio para el template
mkdir -p /opt/ss4-form-filler/templates

# Subir tu PDF template (desde tu máquina local)
scp 1_updated_fss4.pdf tu-usuario@servidor:/opt/ss4-form-filler/templates/
```

### Paso 2: Configurar en Coolify

1. **Crear nueva aplicación:**
   - En Coolify, ve a "Resources" → "New"
   - Selecciona "Public Repository"
   - O conecta tu cuenta de GitHub

2. **Configurar el repositorio:**
   - Repository URL: `https://github.com/camilocuadros/ss4-generator-claude`
   - Branch: `main`
   - Build Pack: **Dockerfile** o **Docker Compose**

3. **Configurar variables de entorno:**

   En la sección "Environment Variables":

   ```env
   TEMPLATE_PATH=/app/templates/1_updated_fss4.pdf
   MAPPING_PATH=/app/ss4_field_mapping.json
   ```

4. **Configurar volumen (solo para el template):**

   En "Persistent Storage" o "Volumes":

   - Source (en el servidor): `/opt/ss4-form-filler/templates`
   - Destination (en el container): `/app/templates`
   - Read Only: ✅ **Sí** (más seguro)

5. **Puerto:**
   - Internal Port: `8000`
   - Public: Coolify lo asignará automáticamente

6. **Desplegar:**
   - Click en "Deploy"
   - Espera a que se complete el build (~2-3 minutos)

---

## 🌐 Opción 2: Almacenar Template en el Repositorio (Aún más simple)

Si prefieres no configurar volúmenes en el servidor:

### Paso 1: Agregar el template al repositorio

```bash
# En tu máquina local, dentro del proyecto
cp /ruta/a/tu/1_updated_fss4.pdf ./templates/

# Commit y push
git add templates/1_updated_fss4.pdf
git commit -m "Add SS-4 template PDF"
git push origin main
```

### Paso 2: Configurar en Coolify

1. **Crear aplicación** como en la opción 1
2. **NO configurar volúmenes** - el PDF ya está en el repo
3. **Variables de entorno:**
   ```env
   TEMPLATE_PATH=/app/templates/1_updated_fss4.pdf
   MAPPING_PATH=/app/ss4_field_mapping.json
   ```
4. **Deploy!**

**Ventaja:** Cero configuración de storage
**Desventaja:** El PDF queda en el repositorio público (si es público)

---

## 🔧 Configuración Post-Deployment

### 1. Verificar el health check

Una vez desplegado, verifica que la API esté funcionando:

```bash
curl https://tu-dominio.coolify.io/health
```

Deberías recibir:
```json
{"status": "healthy"}
```

### 2. Probar el endpoint

```bash
# Ver la documentación interactiva
https://tu-dominio.coolify.io/docs

# Endpoint raíz
curl https://tu-dominio.coolify.io/
```

### 3. Probar generación de PDF

```bash
# Desde Swagger UI (https://tu-dominio.coolify.io/docs)
# O con curl:
curl -X POST "https://tu-dominio.coolify.io/api/fill-form" \
  -H "Content-Type: application/json" \
  -d '{
    "legal_name": "TEST LLC",
    "mailing_address": "123 Test St",
    "mailing_city_state_zip": "Miami, FL 33101",
    "county_state": "Miami-Dade, Florida",
    "responsible_party_name": "John Doe",
    "responsible_party_ssn": "123-45-6789",
    "date_started": "01/15/2024",
    "closing_month": "December",
    "principal_line": "Testing services",
    "applicant_phone": "(305) 555-0123",
    "signature_name_title": "John Doe, Manager",
    "no": true
  }' \
  --output test_ss4.pdf
```

El PDF se descargará directamente! 🎉

### 4. Configurar dominio personalizado (Opcional)

En Coolify:
- Ve a tu aplicación → Settings → Domains
- Agrega tu dominio: `ss4-api.tudominio.com`
- Coolify configurará automáticamente SSL con Let's Encrypt

---

## 🔐 Configuración de CORS

Si vas a usar un frontend desde otro dominio:

### Opción A: Actualizar el código (recomendado para producción)

En [api_ss4_filler.py:28](api_ss4_filler.py#L28), cambia:

```python
allow_origins=["*"],  # Permitir todos
```

A:

```python
allow_origins=[
    "https://tu-frontend.com",
    "https://www.tu-frontend.com"
],
```

### Opción B: Usar variable de entorno

Agrega en Coolify:
```env
CORS_ORIGINS=https://tu-frontend.com,https://www.tu-frontend.com
```

(Requiere modificar el código para leer esta variable)

---

## 📊 Monitoreo y Logs

### Ver logs en Coolify:
1. Ve a tu aplicación
2. Click en "Logs"
3. Verás los logs en tiempo real

### Verificar funcionamiento:
```bash
# Health check
curl https://tu-dominio.coolify.io/health

# Ver docs interactivas
https://tu-dominio.coolify.io/docs
```

---

## 🔄 Actualizaciones

Para actualizar la aplicación después de hacer cambios:

### 1. Push a GitHub:
```bash
git add .
git commit -m "Update: descripción del cambio"
git push origin main
```

### 2. En Coolify:
- Ve a tu aplicación
- Click en "Redeploy" o "Restart"
- Coolify hará pull del código nuevo y reconstruirá automáticamente

**Tip:** Puedes habilitar "Auto Deploy" en Coolify para que se actualice automáticamente con cada push.

---

## 🐛 Troubleshooting

### Problema: Template PDF not found

**Causa:** El archivo template no está en `/app/templates/`

**Solución 1** - Verificar el volumen:
```bash
# SSH al servidor
ssh tu-servidor
ls -la /opt/ss4-form-filler/templates/

# Si no está, súbelo:
scp 1_updated_fss4.pdf usuario@servidor:/opt/ss4-form-filler/templates/
```

**Solución 2** - Usar repositorio (ver Opción 2 arriba)

---

### Problema: Permission denied

**Solución:**
```bash
# En el servidor
sudo chown -R 1000:1000 /opt/ss4-form-filler/
sudo chmod -R 755 /opt/ss4-form-filler/
```

---

### Problema: pdftk not found

**Solución:**
El Dockerfile ya incluye pdftk. Verifica:
1. Que el build se completó correctamente en Coolify
2. Revisa los logs de build
3. Intenta "Force Rebuild" en Coolify

---

### Problema: API no responde

**Verificaciones:**
1. ✅ Health check: `curl https://tu-dominio.coolify.io/health`
2. ✅ Revisar logs en Coolify
3. ✅ Verificar que el puerto 8000 está configurado
4. ✅ Verificar variables de entorno
5. ✅ Verificar que el dominio apunta correctamente

---

### Problema: CORS error desde el frontend

**Solución:**
Actualiza el código en `api_ss4_filler.py` para permitir tu dominio frontend (ver sección CORS arriba).

---

## 📈 Optimización y Escalabilidad

### Para mayor tráfico:

#### 1. **Aumentar recursos:**
En Coolify → Settings → Resources:
- CPU: Aumenta según necesidad
- RAM: Mínimo 512MB, recomendado 1GB

#### 2. **Habilitar múltiples réplicas:**

En `docker-compose.yml`:
```yaml
services:
  ss4-api:
    deploy:
      replicas: 3  # Múltiples instancias
```

Coolify manejará el load balancing automáticamente.

#### 3. **Cachear el template:**

Para mejor performance, el template se carga una sola vez al iniciar (ya implementado).

---

## 🔐 Seguridad en Producción

### ✅ Ya implementado:

- Template montado como read-only (`:ro`)
- PDFs temporales se auto-eliminan
- No se almacenan datos sensibles
- Health checks configurados

### 🔒 Recomendaciones adicionales:

#### 1. Rate Limiting

Agrega rate limiting para prevenir abuso:

```python
# En requirements.txt
slowapi==0.1.9

# En api_ss4_filler.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/fill-form")
@limiter.limit("10/minute")  # 10 requests por minuto
async def fill_form(...):
    ...
```

#### 2. Autenticación (si es necesario)

Si quieres proteger la API:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/api/fill-form")
async def fill_form(
    form_data: SS4FormData,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verificar token
    if credentials.credentials != "tu-api-key-secreta":
        raise HTTPException(status_code=401)
    ...
```

#### 3. HTTPS

- Coolify configura automáticamente Let's Encrypt SSL ✅
- Asegúrate de que está habilitado en Settings → SSL

---

## 🎯 URLs finales

Después del deployment tendrás:

- **API Base**: `https://tu-dominio.coolify.io/`
- **Health Check**: `https://tu-dominio.coolify.io/health`
- **API Docs (Swagger)**: `https://tu-dominio.coolify.io/docs`
- **Redoc Docs**: `https://tu-dominio.coolify.io/redoc`
- **Fill Form Endpoint**: `POST https://tu-dominio.coolify.io/api/fill-form`
  - ⚠️ Ahora devuelve el PDF **directamente**
  - No hay endpoint de descarga separado

---

## ✅ Checklist de Deployment

- [ ] Servidor Coolify accesible
- [ ] Repositorio GitHub configurado
- [ ] Template PDF preparado
- [ ] **Opción 1**: Directorio `/opt/ss4-form-filler/templates` creado en servidor
  - [ ] Template subido al servidor
- [ ] **Opción 2**: Template agregado al repositorio Git
- [ ] Aplicación creada en Coolify
- [ ] Variables de entorno configuradas
- [ ] Volumen configurado (si usas Opción 1)
- [ ] Build completado exitosamente
- [ ] Health check passing (`/health` retorna 200)
- [ ] Swagger docs accesible (`/docs`)
- [ ] Endpoint de prueba funcionando
- [ ] Dominio configurado (opcional)
- [ ] SSL habilitado (automático con Coolify)

---

## 💡 Ventajas de esta Arquitectura

### Sin almacenamiento:
- ✅ **Gratis** - no pagas por storage
- ✅ **Seguro** - no quedan archivos sensibles
- ✅ **Simple** - menos configuración
- ✅ **Escalable** - usa la memoria del container
- ✅ **Rápido** - acceso directo desde /tmp

### Comparado con almacenamiento persistente:
- ❌ No puedes recuperar PDFs antiguos
- ✅ Pero tampoco necesitas limpiar archivos viejos
- ✅ Cumple con GDPR (no almacenas datos de usuarios)

---

## 🆚 Alternativas de Storage (si las necesitas)

Si en el futuro necesitas almacenar los PDFs:

### Cloudflare R2 (10GB gratis/mes)
```env
R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY=tu-access-key
R2_SECRET_KEY=tu-secret-key
R2_BUCKET=ss4-forms
```

### Backblaze B2 (10GB gratis)
```env
B2_ENDPOINT=https://s3.us-west-004.backblazeb2.com
B2_KEY_ID=tu-key-id
B2_APP_KEY=tu-app-key
B2_BUCKET=ss4-forms
```

**Nota:** Requiere modificar el código para usar boto3.

---

## 📞 Soporte

Si tienes problemas:
1. ✅ Revisa los logs en Coolify
2. ✅ Verifica este README
3. ✅ Prueba el health endpoint
4. ✅ Consulta Swagger docs: `/docs`
5. ✅ Documentación de Coolify: https://coolify.io/docs

---

## 🎉 Resumen Rápido

```bash
# 1. Sube el template al servidor
scp 1_updated_fss4.pdf user@server:/opt/ss4-form-filler/templates/

# 2. En Coolify:
#    - New Resource → Public Repository
#    - URL: https://github.com/camilocuadros/ss4-generator-claude
#    - Add Volume: /opt/ss4-form-filler/templates → /app/templates
#    - Deploy!

# 3. Verifica
curl https://tu-dominio.coolify.io/health

# 4. Prueba
# Visita: https://tu-dominio.coolify.io/docs
```

---

**Última actualización:** 2024-11-21
**Versión:** 2.0.0 (Sin almacenamiento persistente)
