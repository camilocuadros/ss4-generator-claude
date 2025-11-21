#!/usr/bin/env python3
"""
API REST para llenar formularios SS-4 del IRS
FastAPI + pdftk
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import subprocess
import tempfile
import json
from pathlib import Path
import uuid
import os


app = FastAPI(
    title="SS-4 Form Filler API",
    description="API para llenar formularios SS-4 del IRS",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos de datos
class SS4FormData(BaseModel):
    """Modelo para los datos del formulario SS-4"""
    
    # Información básica
    legal_name: str = Field(..., description="Nombre legal de la entidad")
    trade_name: Optional[str] = Field(None, description="Nombre comercial")
    executor_name: Optional[str] = None
    
    # Direcciones
    mailing_address: str
    mailing_city_state_zip: str
    street_address: Optional[str] = None
    street_city_state_zip: Optional[str] = None
    county_state: str
    
    # Parte responsable
    responsible_party_name: str
    responsible_party_ssn: str = Field(..., description="SSN/ITIN/EIN (XXX-XX-XXXX)")
    
    # LLC
    is_llc_yes: bool = False
    is_llc_no: bool = False
    llc_members: Optional[str] = None
    llc_in_us_yes: bool = False
    llc_in_us_no: bool = False
    
    # Tipo de entidad (solo uno debe ser True)
    sole_proprietor: bool = False
    partnership: bool = False
    corporation: bool = False
    personal_service_corp: bool = False
    church: bool = False
    other_nonprofit: bool = False
    other: bool = False
    estate: bool = False
    plan_administrator: bool = False
    trust: bool = False
    military: bool = False
    state_local_gov: bool = False
    farmers_coop: bool = False
    remic: bool = False
    federal_gov: bool = False
    indian_tribal: bool = False
    
    # Campos adicionales línea 9
    corporation_form_number: Optional[str] = None
    trust_tin: Optional[str] = None
    plan_admin_tin: Optional[str] = None
    other_specify: Optional[str] = None
    nonprofit_specify: Optional[str] = None
    group_exemption_number: Optional[str] = None
    state_incorporated: Optional[str] = None
    foreign_country: Optional[str] = None
    
    # Razón de la solicitud (solo una debe ser True)
    started_new_business: bool = False
    hired_employees: bool = False
    compliance_withholding: bool = False
    banking_purpose: bool = False
    changed_org_type: bool = False
    purchased_business: bool = False
    created_trust: bool = False
    created_pension: bool = False
    other_reason: bool = False
    
    # Especificaciones línea 10
    business_type_specify: Optional[str] = None
    new_org_type: Optional[str] = None
    trust_type: Optional[str] = None
    banking_purpose_specify: Optional[str] = None
    pension_type: Optional[str] = None
    other_reason_specify: Optional[str] = None
    
    # Fechas y empleados
    date_started: str = Field(..., description="Fecha de inicio (MM/DD/YYYY)")
    closing_month: str = Field(..., description="Mes de cierre contable")
    employees_agricultural: Optional[str] = None
    employees_household: Optional[str] = None
    employees_other: Optional[str] = None
    file_form_944: bool = False
    first_wages_date: Optional[str] = None
    
    # Actividad principal (solo una debe ser True)
    construction: bool = False
    real_estate: bool = False
    rental_leasing: bool = False
    manufacturing: bool = False
    finance_insurance: bool = False
    health_care: bool = False
    accommodation_food: bool = False
    wholesale_agent: bool = False
    transportation: bool = False
    wholesale_other: bool = False
    retail: bool = False
    other_activity: bool = False
    other_activity_specify: Optional[str] = None
    
    principal_line: str = Field(..., description="Descripción de productos/servicios")
    
    # EIN previo
    yes: bool = False  # ¿Ha solicitado EIN antes?
    no: bool = False
    previous_ein: Optional[str] = None
    
    # Designado de terceros
    designee_name: Optional[str] = None
    designee_phone: Optional[str] = None
    designee_address: Optional[str] = None
    designee_fax: Optional[str] = None
    
    # Firma
    signature_name_title: str
    applicant_phone: str
    applicant_fax: Optional[str] = None


class FormFillerService:
    """Servicio para llenar formularios SS-4"""
    
    def __init__(self, template_path: str, mapping_path: str):
        self.template_path = template_path
        with open(mapping_path, 'r', encoding='utf-8') as f:
            self.mapping = json.load(f)
    
    def _get_field_name(self, field_key: str) -> Optional[str]:
        """Obtiene el nombre técnico del campo"""
        fields = self.mapping.get('fields', {})
        
        if field_key in fields:
            field_info = fields[field_key]
            if isinstance(field_info, dict) and 'field_name' in field_info:
                return field_info['field_name']
        
        for parent_key, parent_value in fields.items():
            if isinstance(parent_value, dict):
                if field_key in parent_value:
                    nested_field = parent_value[field_key]
                    if isinstance(nested_field, dict) and 'field_name' in nested_field:
                        return nested_field['field_name']
        
        return None
    
    def _create_fdf_data(self, data: Dict[str, Any]) -> str:
        """Crea el contenido FDF"""
        fdf_data_lines = []
        
        for key, value in data.items():
            if value is None or value == '':
                continue
            
            field_name = self._get_field_name(key)
            if field_name:
                if isinstance(value, bool):
                    fdf_value = 'Yes' if value else 'Off'
                else:
                    fdf_value = str(value).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
                
                fdf_data_lines.append(f"<< /T ({field_name}) /V ({fdf_value}) >>")
        
        fdf_content = f"""%FDF-1.2
%âãÏÓ
1 0 obj
<<
/FDF
<<
/Fields [
{chr(10).join(fdf_data_lines)}
]
>>
>>
endobj
trailer
<<
/Root 1 0 R
>>
%%EOF"""
        
        return fdf_content
    
    def fill_form(self, data: Dict[str, Any], output_path: str, flatten: bool = False) -> bool:
        """Llena el formulario usando pdftk"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fdf', delete=False, encoding='utf-8') as fdf_file:
                fdf_content = self._create_fdf_data(data)
                fdf_file.write(fdf_content)
                fdf_path = fdf_file.name
            
            cmd = [
                'pdftk',
                self.template_path,
                'fill_form',
                fdf_path,
                'output',
                output_path
            ]
            
            if flatten:
                cmd.append('flatten')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            Path(fdf_path).unlink()
            
            return result.returncode == 0
                
        except Exception as e:
            print(f"Error: {e}")
            return False


# Configuración usando variables de entorno (compatibles con Docker y Coolify)
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "/app/templates/1_updated_fss4.pdf")
MAPPING_PATH = os.getenv("MAPPING_PATH", "/app/ss4_field_mapping.json")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/app/outputs"))
OUTPUT_DIR.mkdir(exist_ok=True)

# Validar que el template existe
if not Path(TEMPLATE_PATH).exists():
    print(f"⚠️  WARNING: Template PDF not found at {TEMPLATE_PATH}")
    print("   Please upload your SS-4 template PDF to the templates directory")

form_service = FormFillerService(TEMPLATE_PATH, MAPPING_PATH)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "SS-4 Form Filler API",
        "version": "1.0.0",
        "endpoints": {
            "fill_form": "POST /api/fill-form",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/fill-form")
async def fill_form(form_data: SS4FormData, flatten: bool = False):
    """
    Llena el formulario SS-4 con los datos proporcionados
    
    - **form_data**: Datos del formulario
    - **flatten**: Si True, hace el PDF no editable (default: False)
    
    Retorna un enlace de descarga del PDF llenado
    """
    try:
        # Generar ID único para el archivo
        file_id = str(uuid.uuid4())
        output_filename = f"ss4_filled_{file_id}.pdf"
        output_path = OUTPUT_DIR / output_filename
        
        # Convertir el modelo a diccionario
        data_dict = form_data.model_dump(exclude_none=False)
        
        # Llenar el formulario
        success = form_service.fill_form(
            data=data_dict,
            output_path=str(output_path),
            flatten=flatten
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Error al llenar el formulario")
        
        return {
            "success": True,
            "message": "Formulario llenado exitosamente",
            "download_url": f"/api/download/{file_id}",
            "file_id": file_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{file_id}")
async def download_form(file_id: str):
    """
    Descarga el formulario llenado
    
    - **file_id**: ID del archivo generado
    """
    output_filename = f"ss4_filled_{file_id}.pdf"
    output_path = OUTPUT_DIR / output_filename
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=str(output_path),
        filename=f"SS-4_Filled_{file_id[:8]}.pdf",
        media_type="application/pdf"
    )


@app.get("/api/field-mapping")
async def get_field_mapping():
    """
    Retorna el mapeo de campos del formulario
    Útil para la documentación del frontend
    """
    with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    return mapping


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
