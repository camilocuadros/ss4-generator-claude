# 🚀 Guía de Inicio Rápido - SS-4 Form Filler

## ⚡ Setup en 5 Minutos

### 1️⃣ Instalar pdftk (requerido)

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install pdftk

# macOS
brew install pdftk-java

# Verificar instalación
pdftk --version
```

### 2️⃣ Configurar Backend

```bash
# Instalar dependencias Python
pip install fastapi uvicorn python-multipart pydantic pypdf

# O usar requirements.txt
pip install -r requirements.txt
```

### 3️⃣ Estructura de Archivos Necesaria

```
tu-proyecto/
├── api_ss4_filler.py           # API FastAPI
├── ss4_form_filler_pdftk.py    # Llenador de formularios
├── ss4_field_mapping.json      # Mapeo de campos
├── 1_updated_fss4.pdf          # Template del formulario
└── requirements.txt
```

### 4️⃣ Iniciar el Backend

```bash
# Opción A: Directamente con uvicorn
uvicorn api_ss4_filler:app --reload --host 0.0.0.0 --port 8000

# Opción B: Con el script
python api_ss4_filler.py
```

La API estará disponible en: **http://localhost:8000**

### 5️⃣ Probar la API

```bash
# Ejecutar script de prueba
python test_api.py
```

O prueba manualmente:

```bash
# Health check
curl http://localhost:8000/health

# Documentación interactiva
# Abre en tu navegador: http://localhost:8000/docs
```

---

## 📝 Ejemplo de Uso Rápido

### Python Script

```python
from ss4_form_filler_pdftk import SS4FormFillerPDFTK

# Tus datos
data = {
    "legal_name": "MI EMPRESA LLC",
    "responsible_party_name": "Tu Nombre",
    "responsible_party_ssn": "123-45-6789",
    "mailing_address": "123 Main St",
    "mailing_city_state_zip": "Miami, FL 33101",
    "county_state": "Miami-Dade, Florida",
    "date_started": "01/15/2024",
    "closing_month": "December",
    "principal_line": "Servicios profesionales",
    "applicant_phone": "(305) 555-0123",
    "signature_name_title": "Tu Nombre, Owner"
}

# Llenar formulario
filler = SS4FormFillerPDFTK(
    template_path="1_updated_fss4.pdf",
    mapping_path="ss4_field_mapping.json"
)

filler.fill_form(data, "mi_ss4_llenado.pdf")
```

### API Request (cURL)

```bash
curl -X POST "http://localhost:8000/api/fill-form" \
  -H "Content-Type: application/json" \
  -d '{
    "legal_name": "MI EMPRESA LLC",
    "responsible_party_name": "Tu Nombre",
    "responsible_party_ssn": "123-45-6789",
    "mailing_address": "123 Main St",
    "mailing_city_state_zip": "Miami, FL 33101",
    "county_state": "Miami-Dade, Florida",
    "date_started": "01/15/2024",
    "closing_month": "December",
    "principal_line": "Servicios profesionales",
    "applicant_phone": "(305) 555-0123",
    "signature_name_title": "Tu Nombre, Owner",
    "is_llc_yes": true,
    "llc_members": "1",
    "llc_in_us_yes": true,
    "started_new_business": true,
    "no": true
  }'
```

### JavaScript/React

```javascript
import axios from 'axios';

const fillForm = async (formData) => {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/fill-form',
      formData
    );
    
    // Descargar el PDF
    const downloadUrl = `http://localhost:8000${response.data.download_url}`;
    window.open(downloadUrl, '_blank');
    
  } catch (error) {
    console.error('Error:', error);
  }
};
```

---

## 🔧 Troubleshooting Rápido

### ❌ "pdftk: command not found"
**Solución:** Instalar pdftk (ver paso 1)

### ❌ "File not found: 1_updated_fss4.pdf"
**Solución:** Asegúrate de tener el archivo template en el mismo directorio

### ❌ "CORS error" en el frontend
**Solución:** En `api_ss4_filler.py`, verifica la configuración de CORS:
```python
allow_origins=["http://localhost:3000"]  # Tu dominio frontend
```

### ❌ Campos no se llenan
**Solución:** Verifica que el PDF tenga campos editables:
```bash
pdftk tu_formulario.pdf dump_data_fields
```

---

## 📚 Campos Mínimos Requeridos

Para generar un formulario SS-4 válido, necesitas al menos:

```python
{
    "legal_name": "Nombre de la entidad",
    "mailing_address": "Dirección",
    "mailing_city_state_zip": "Ciudad, Estado, ZIP",
    "county_state": "Condado, Estado",
    "responsible_party_name": "Nombre responsable",
    "responsible_party_ssn": "XXX-XX-XXXX",
    "date_started": "MM/DD/YYYY",
    "closing_month": "Mes",
    "principal_line": "Descripción del negocio",
    "applicant_phone": "Teléfono",
    "signature_name_title": "Nombre, Título"
}
```

---

## 🎯 Siguiente Paso

1. **Para desarrollo local**: Usa el componente React en `SS4FormFiller.jsx`
2. **Para integración**: Lee `README.md` completo
3. **Para producción**: Revisa la sección de despliegue en `README.md`

---

## 💡 Tips

- **Documentación Interactiva**: http://localhost:8000/docs (Swagger UI)
- **Mapeo de Campos**: GET http://localhost:8000/api/field-mapping
- **Aplanar PDF**: Usa `?flatten=true` en la API para hacer el PDF no editable

---

## 📞 ¿Necesitas ayuda?

- Ver el `README.md` completo para documentación detallada
- Ejecutar `python test_api.py` para diagnosticar problemas
- Revisar logs de la API en la consola

---

**¡Listo para comenzar! 🚀**
