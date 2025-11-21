# Templates Directory

Este directorio debe contener el template del formulario SS-4.

## Archivo requerido:

- `1_updated_fss4.pdf` - Template oficial del formulario SS-4 del IRS

## Dónde obtener el template:

1. Descarga el formulario oficial SS-4 desde el sitio del IRS:
   https://www.irs.gov/forms-pubs/about-form-ss-4

2. O usa tu versión actualizada del formulario

## Para desarrollo local:

```bash
# Copia tu template a este directorio
cp /ruta/a/tu/1_updated_fss4.pdf ./templates/
```

## Para deployment en servidor:

```bash
# Sube el template al servidor
scp 1_updated_fss4.pdf usuario@servidor:/opt/ss4-form-filler/templates/
```

**Nota:** El archivo debe tener campos editables para que el sistema pueda llenarlos automáticamente.
