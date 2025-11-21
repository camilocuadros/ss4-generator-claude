#!/usr/bin/env python3
"""
SS-4 Form Filler usando pdftk
pdftk es la herramienta más confiable para llenar formularios PDF
"""

import json
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile


class SS4FormFillerPDFTK:
    """Clase para llenar el formulario SS-4 del IRS usando pdftk"""
    
    def __init__(self, template_path: str, mapping_path: str):
        """
        Inicializa el llenador de formularios
        
        Args:
            template_path: Ruta al PDF del formulario SS-4 vacío
            mapping_path: Ruta al archivo JSON con el mapeo de campos
        """
        self.template_path = template_path
        
        # Cargar el mapeo de campos
        with open(mapping_path, 'r', encoding='utf-8') as f:
            self.mapping = json.load(f)
    
    def _get_field_name(self, field_key: str) -> Optional[str]:
        """
        Obtiene el nombre técnico del campo a partir de la clave legible
        """
        fields = self.mapping.get('fields', {})
        
        # Buscar en campos simples
        if field_key in fields:
            field_info = fields[field_key]
            if isinstance(field_info, dict) and 'field_name' in field_info:
                return field_info['field_name']
        
        # Buscar en campos anidados
        for parent_key, parent_value in fields.items():
            if isinstance(parent_value, dict):
                if field_key in parent_value:
                    nested_field = parent_value[field_key]
                    if isinstance(nested_field, dict) and 'field_name' in nested_field:
                        return nested_field['field_name']
        
        return None
    
    def _create_fdf_data(self, data: Dict[str, Any]) -> str:
        """
        Crea el contenido FDF (Forms Data Format) para llenar el PDF
        
        Args:
            data: Diccionario con los datos del formulario
        
        Returns:
            String con el contenido FDF
        """
        fdf_data_lines = []
        
        for key, value in data.items():
            if value is None or value == '':
                continue
            
            field_name = self._get_field_name(key)
            if field_name:
                # Para checkboxes
                if isinstance(value, bool):
                    fdf_value = 'Yes' if value else 'Off'
                else:
                    # Escapar caracteres especiales
                    fdf_value = str(value).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
                
                fdf_data_lines.append(f"<< /T ({field_name}) /V ({fdf_value}) >>")
        
        # Crear el archivo FDF completo
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
        """
        Llena el formulario con los datos proporcionados usando pdftk
        
        Args:
            data: Diccionario con los datos del formulario
            output_path: Ruta donde guardar el PDF llenado
            flatten: Si True, aplana el formulario (lo hace no editable)
        
        Returns:
            True si se llenó exitosamente
        """
        try:
            # Crear archivo FDF temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fdf', delete=False, encoding='utf-8') as fdf_file:
                fdf_content = self._create_fdf_data(data)
                fdf_file.write(fdf_content)
                fdf_path = fdf_file.name
            
            # Construir comando pdftk
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
            
            # Ejecutar pdftk
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Limpiar archivo FDF temporal
            Path(fdf_path).unlink()
            
            if result.returncode == 0:
                # Contar cuántos campos se llenaron
                field_count = sum(1 for k, v in data.items() 
                                if v is not None and v != '' and self._get_field_name(k))
                print(f"✅ {field_count} campos procesados exitosamente")
                print(f"📄 Formulario guardado: {output_path}")
                return True
            else:
                print(f"❌ Error de pdftk: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


# Ejemplo de uso
if __name__ == "__main__":
    
    # Datos de ejemplo para KINTO LLC
    kinto_data = {
        # Información básica
        "legal_name": "KINTO LLC",
        "trade_name": "Kinto Growth Partners",
        "mailing_address": "1234 Main Street, Suite 100",
        "mailing_city_state_zip": "Miami, FL 33101",
        "street_address": "1234 Main Street, Suite 100",
        "street_city_state_zip": "Miami, FL 33101",
        "county_state": "Miami-Dade, Florida",
        
        # Responsible party
        "responsible_party_name": "Camilo Rodriguez",
        "responsible_party_ssn": "123-45-6789",
        
        # LLC information
        "is_llc_yes": True,
        "llc_members": "1",
        "llc_in_us_yes": True,
        
        # Reason for applying
        "started_new_business": True,
        "business_type_specify": "Digital Marketing & Business Consulting",
        
        # Dates and business info
        "date_started": "01/15/2024",
        "closing_month": "December",
        "employees_other": "5",
        
        # Principal activity
        "other_activity": True,
        "other_activity_specify": "Professional Services",
        "principal_line": "Digital marketing, consulting, e-commerce optimization",
        
        # Previous EIN
        "no": True,
        
        # Contact info
        "applicant_phone": "(305) 555-0123",
        "signature_name_title": "Camilo Rodriguez, Managing Member",
    }
    
    print("=" * 70)
    print("🎯 SS-4 Form Filler - Using pdftk")
    print("=" * 70)
    print()
    
    # Crear instancia y llenar formulario
    filler = SS4FormFillerPDFTK(
        template_path="/mnt/user-data/uploads/1_updated_fss4.pdf",
        mapping_path="/home/claude/ss4_field_mapping.json"
    )
    
    print("📝 Llenando formulario con pdftk...")
    success = filler.fill_form(
        data=kinto_data,
        output_path="/home/claude/ss4_filled_pdftk.pdf",
        flatten=False  # Cambia a True para hacer el PDF no editable
    )
    
    if success:
        print("\n" + "=" * 70)
        print("✅ ¡Formulario llenado exitosamente!")
        print("=" * 70)
        print("\n📦 Archivo generado:")
        print("   • ss4_filled_pdftk.pdf")
        print("\n💡 Tip: Usa flatten=True para hacer el formulario no editable")
    else:
        print("\n❌ Hubo un error al llenar el formulario")
