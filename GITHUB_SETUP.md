# Setup GitHub Repository - Instrucciones

## Paso 1: Crear Repositorio en GitHub

1. Ve a [github.com/new](https://github.com/new)
2. Nombre: `PID-Controller-Tuner`
3. Descripción: `Computer-Aided Design Tool for PID Control Systems - Automatic tuning using Ziegler-Nichols and Cohen-Coon methods`
4. Privacidad: **Public** (o Private si prefieres)
5. NO marques "Initialize with README" (ya existe)
6. NO marques "Add .gitignore" (ya existe)
7. NO marques "Add License" (ya existe)
8. Click "Create repository"

## Paso 2: Inicializar Git Local

Ejecuta en tu terminal en la carpeta del proyecto:

```powershell
cd "c:\Users\USER\Desktop\Proyectos\Control - Ing\Control 1"

# Inicializar repositorio git
git init

# Configurar usuario (si no está configurado)
git config user.name "Tu Nombre"
git config user.email "tu.email@ejemplo.com"

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "Initial commit: PID Controller Tuner application

- Backend: Transfer function analysis with Ziegler-Nichols and Cohen-Coon tuning
- Frontend: Multi-page Streamlit application
- Features: Step response simulation, metrics calculation, code generation
- Documentation: Complete technical guide and theory"

# Cambiar rama main a master (si es necesario)
git branch -M main
```

## Paso 3: Conectar con GitHub

Reemplaza `TU_USUARIO` con tu usuario de GitHub:

```powershell
# Agregar repositorio remoto
git remote add origin https://github.com/TU_USUARIO/PID-Controller-Tuner.git

# Subir código a GitHub
git branch -M main
git push -u origin main
```

**Alternativa con SSH (si tienes SSH configurado):**

```powershell
git remote add origin git@github.com:TU_USUARIO/PID-Controller-Tuner.git
git push -u origin main
```

## Paso 4: Verificar en GitHub

- Ve a `https://github.com/TU_USUARIO/PID-Controller-Tuner`
- Verifica que todos los archivos estén presentes
- Revisa el README en la página principal

## Paso 5 (Opcional): Configurar GitHub Pages

Si quieres documentación en GitHub Pages:

1. Ve a **Settings** → **Pages**
2. Selecciona source: **main** branch, **/ (root)** folder
3. Espera a que se despliegue

## Comandos Útiles para Futuros Cambios

```powershell
# Ver estado
git status

# Ver cambios
git diff

# Agregar cambios
git add .

# Commit
git commit -m "Descripción del cambio"

# Subir cambios
git push

# Bajar cambios
git pull
```

## Estructura Final en GitHub

```
PID-Controller-Tuner/
├── .github/
├── app/
├── src/
├── .gitignore
├── .gitattributes
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
└── [otros archivos]
```

---

¡Tu repositorio estará listo en GitHub! 🚀
