#!/usr/bin/env python3
"""
Script de prueba para la API SS-4 Form Filler
"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def test_health_check():
    """Probar el endpoint de health check"""
    print("\n🔍 Probando Health Check...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_field_mapping():
    """Probar el endpoint de field mapping"""
    print("\n🔍 Probando Get Field Mapping...")
    try:
        response = requests.get(f"{API_URL}/api/field-mapping")
        print(f"✅ Status: {response.status_code}")
        mapping = response.json()
        print(f"   Total fields: {len(mapping.get('fields', {}))}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_fill_form():
    """Probar el endpoint de llenado de formulario"""
    print("\n🔍 Probando Fill Form...")
    
    # Datos de prueba
    test_data = {
        "legal_name": "TEST COMPANY LLC",
        "trade_name": "Test Company",
        "mailing_address": "123 Test Street",
        "mailing_city_state_zip": "Miami, FL 33101",
        "county_state": "Miami-Dade, Florida",
        "responsible_party_name": "John Doe",
        "responsible_party_ssn": "123-45-6789",
        "is_llc_yes": True,
        "llc_members": "1",
        "llc_in_us_yes": True,
        "started_new_business": True,
        "business_type_specify": "Test Business",
        "date_started": "01/01/2024",
        "closing_month": "December",
        "employees_other": "0",
        "other_activity": True,
        "other_activity_specify": "Testing",
        "principal_line": "Software testing and development",
        "no": True,
        "applicant_phone": "(305) 555-0000",
        "signature_name_title": "John Doe, Owner"
    }
    
    try:
        print("   Enviando datos...")
        response = requests.post(
            f"{API_URL}/api/fill-form",
            json=test_data,
            params={"flatten": False}
        )
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result['success']}")
            print(f"   Message: {result['message']}")
            print(f"   File ID: {result['file_id']}")
            
            # Intentar descargar el PDF
            download_url = f"{API_URL}{result['download_url']}"
            print(f"\n   Descargando PDF de: {download_url}")
            
            time.sleep(1)  # Pequeña pausa
            
            pdf_response = requests.get(download_url)
            if pdf_response.status_code == 200:
                filename = f"test_ss4_{result['file_id'][:8]}.pdf"
                with open(filename, 'wb') as f:
                    f.write(pdf_response.content)
                print(f"   ✅ PDF descargado: {filename}")
                return True
            else:
                print(f"   ❌ Error al descargar PDF: {pdf_response.status_code}")
                return False
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("=" * 70)
    print("🧪 SS-4 Form Filler API - Test Suite")
    print("=" * 70)
    
    results = {
        "health_check": test_health_check(),
        "field_mapping": test_get_field_mapping(),
        "fill_form": test_fill_form()
    }
    
    print("\n" + "=" * 70)
    print("📊 Resultados de las Pruebas")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} pruebas pasaron")
    
    if total_passed == total_tests:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa la salida arriba.")

if __name__ == "__main__":
    # Verificar que la API esté corriendo
    print("\n🔍 Verificando que la API esté corriendo...")
    try:
        requests.get(f"{API_URL}/health", timeout=2)
        print("✅ API está corriendo\n")
        run_all_tests()
    except:
        print(f"❌ La API no está corriendo en {API_URL}")
        print("\nPara iniciar la API, ejecuta:")
        print("  python api_ss4_filler.py")
