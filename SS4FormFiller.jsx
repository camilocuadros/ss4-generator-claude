import React, { useState } from 'react';
import axios from 'axios';

const SS4FormFiller = () => {
  const [formData, setFormData] = useState({
    // Información básica
    legal_name: '',
    trade_name: '',
    mailing_address: '',
    mailing_city_state_zip: '',
    street_address: '',
    street_city_state_zip: '',
    county_state: '',
    
    // Parte responsable
    responsible_party_name: '',
    responsible_party_ssn: '',
    
    // LLC
    is_llc_yes: false,
    is_llc_no: false,
    llc_members: '',
    llc_in_us_yes: false,
    llc_in_us_no: false,
    
    // Razón de la solicitud
    started_new_business: false,
    business_type_specify: '',
    
    // Fechas y negocio
    date_started: '',
    closing_month: '',
    employees_other: '',
    
    // Actividad principal
    other_activity: false,
    other_activity_specify: '',
    principal_line: '',
    
    // EIN previo
    no: false,
    previous_ein: '',
    
    // Contacto
    applicant_phone: '',
    signature_name_title: '',
  });

  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setDownloadUrl(null);

    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      
      const response = await axios.post(`${API_URL}/api/fill-form`, formData, {
        params: { flatten: false }
      });

      if (response.data.success) {
        const downloadUrl = `${API_URL}${response.data.download_url}`;
        setDownloadUrl(downloadUrl);
        alert('Formulario generado exitosamente!');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al generar el formulario');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold mb-6 text-center text-blue-600">
        Formulario SS-4 - Solicitud de EIN
      </h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Información Básica */}
        <section className="border-b pb-6">
          <h2 className="text-xl font-semibold mb-4">Información Básica</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block mb-2 font-medium">
                Nombre Legal de la Entidad *
              </label>
              <input
                type="text"
                name="legal_name"
                value={formData.legal_name}
                onChange={handleChange}
                required
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block mb-2 font-medium">
                Nombre Comercial
              </label>
              <input
                type="text"
                name="trade_name"
                value={formData.trade_name}
                onChange={handleChange}
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </section>

        {/* Direcciones */}
        <section className="border-b pb-6">
          <h2 className="text-xl font-semibold mb-4">Direcciones</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block mb-2 font-medium">
                Dirección Postal *
              </label>
              <input
                type="text"
                name="mailing_address"
                value={formData.mailing_address}
                onChange={handleChange}
                required
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="Calle, número, suite"
              />
            </div>
            
            <div>
              <label className="block mb-2 font-medium">
                Ciudad, Estado, ZIP *
              </label>
              <input
                type="text"
                name="mailing_city_state_zip"
                value={formData.mailing_city_state_zip}
                onChange={handleChange}
                required
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="Miami, FL 33101"
              />
            </div>
            
            <div>
              <label className="block mb-2 font-medium">
                Condado y Estado *
              </label>
              <input
                type="text"
                name="county_state"
                value={formData.county_state}
                onChange={handleChange}
                required
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="Miami-Dade, Florida"
              />
            </div>
          </div>
        </section>

        {/* Parte Responsable */}
        <section className="border-b pb-6">
          <h2 className="text-xl font-semibold mb-4">Parte Responsable</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block mb-2 font-medium">
                Nombre *
              </label>
              <input
                type="text"
                name="responsible_party_name"
                value={formData.responsible_party_name}
                onChange={handleChange}
                required
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block mb-2 font-medium">
                SSN/ITIN/EIN *
              </label>
              <input
                type="text"
                name="responsible_party_ssn"
                value={formData.responsible_party_ssn}
                onChange={handleChange}
                required
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="XXX-XX-XXXX"
              />
            </div>
          </div>
        </section>

        {/* LLC */}
        <section className="border-b pb-6">
          <h2 className="text-xl font-semibold mb-4">Información LLC</h2>
          
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_llc_yes"
                  checked={formData.is_llc_yes}
                  onChange={handleChange}
                  className="mr-2"
                />
                <span>¿Es una LLC?</span>
              </label>
            </div>
            
            {formData.is_llc_yes && (
              <>
                <div>
                  <label className="block mb-2 font-medium">
                    Número de Miembros
                  </label>
                  <input
                    type="text"
                    name="llc_members"
                    value={formData.llc_members}
                    onChange={handleChange}
                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div className="flex items-center">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="llc_in_us_yes"
                      checked={formData.llc_in_us_yes}
                      onChange={handleChange}
                      className="mr-2"
                    />
                    <span>¿LLC organizada en USA?</span>
                  </label>
                </div>
              </>
            )}
          </div>
        </section>

        {/* Información del Negocio */}
        <section className="border-b pb-6">
          <h2 className="text-xl font-semibold mb-4">Información del Negocio</h2>
          
          <div className="space-y-4">
            <div className="flex items-center">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="started_new_business"
                  checked={formData.started_new_business}
                  onChange={handleChange}
                  className="mr-2"
                />
                <span>Comenzó un nuevo negocio</span>
              </label>
            </div>
            
            {formData.started_new_business && (
              <div>
                <label className="block mb-2 font-medium">
                  Tipo de Negocio
                </label>
                <input
                  type="text"
                  name="business_type_specify"
                  value={formData.business_type_specify}
                  onChange={handleChange}
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej: Servicios de Marketing Digital"
                />
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block mb-2 font-medium">
                  Fecha de Inicio *
                </label>
                <input
                  type="text"
                  name="date_started"
                  value={formData.date_started}
                  onChange={handleChange}
                  required
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="MM/DD/YYYY"
                />
              </div>
              
              <div>
                <label className="block mb-2 font-medium">
                  Mes de Cierre Contable *
                </label>
                <input
                  type="text"
                  name="closing_month"
                  value={formData.closing_month}
                  onChange={handleChange}
                  required
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="Diciembre"
                />
              </div>
            </div>
            
            <div>
              <label className="block mb-2 font-medium">
                Número de Empleados
              </label>
              <input
                type="text"
                name="employees_other"
                value={formData.employees_other}
                onChange={handleChange}
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="0"
              />
            </div>
            
            <div>
              <label className="block mb-2 font-medium">
                Descripción de Servicios/Productos *
              </label>
              <textarea
                name="principal_line"
                value={formData.principal_line}
                onChange={handleChange}
                required
                rows="3"
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="Describe los servicios o productos principales"
              />
            </div>
          </div>
        </section>

        {/* Actividad Principal */}
        <section className="border-b pb-6">
          <h2 className="text-xl font-semibold mb-4">Actividad Principal</h2>
          
          <div className="space-y-4">
            <div className="flex items-center">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="other_activity"
                  checked={formData.other_activity}
                  onChange={handleChange}
                  className="mr-2"
                />
                <span>Otra actividad</span>
              </label>
            </div>
            
            {formData.other_activity && (
              <div>
                <label className="block mb-2 font-medium">
                  Especificar actividad
                </label>
                <input
                  type="text"
                  name="other_activity_specify"
                  value={formData.other_activity_specify}
                  onChange={handleChange}
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej: Servicios Profesionales"
                />
              </div>
            )}
          </div>
        </section>

        {/* EIN Previo */}
        <section className="border-b pb-6">
          <h2 className="text-xl font-semibold mb-4">EIN Previo</h2>
          
          <div className="flex items-center">
            <label className="flex items-center">
              <input
                type="checkbox"
                name="no"
                checked={formData.no}
                onChange={handleChange}
                className="mr-2"
              />
              <span>No he solicitado EIN anteriormente</span>
            </label>
          </div>
        </section>

        {/* Información de Contacto */}
        <section className="border-b pb-6">
          <h2 className="text-xl font-semibold mb-4">Información de Contacto</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block mb-2 font-medium">
                Teléfono *
              </label>
              <input
                type="tel"
                name="applicant_phone"
                value={formData.applicant_phone}
                onChange={handleChange}
                required
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="(XXX) XXX-XXXX"
              />
            </div>
            
            <div>
              <label className="block mb-2 font-medium">
                Nombre y Título del Firmante *
              </label>
              <input
                type="text"
                name="signature_name_title"
                value={formData.signature_name_title}
                onChange={handleChange}
                required
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="Nombre Completo, Título"
              />
            </div>
          </div>
        </section>

        {/* Botones */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => setFormData({})}
            className="px-6 py-2 border rounded hover:bg-gray-100"
          >
            Limpiar
          </button>
          
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Generando...' : 'Generar Formulario'}
          </button>
        </div>
      </form>

      {/* Mensajes de Error */}
      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Botón de Descarga */}
      {downloadUrl && (
        <div className="mt-6 p-4 bg-green-100 border border-green-400 rounded">
          <p className="text-green-700 mb-2">¡Formulario generado exitosamente!</p>
          <a
            href={downloadUrl}
            download
            className="inline-block px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Descargar Formulario SS-4
          </a>
        </div>
      )}
    </div>
  );
};

export default SS4FormFiller;
