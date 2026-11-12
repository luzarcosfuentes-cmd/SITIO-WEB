# ⚡ NeonBudget - Gestor de Gastos con Flask y SQLite

Aplicación web moderna y visualmente vibrante desarrollada en **Python (Flask)** y **SQLite** para el control personal de gastos, con sistema de autenticación y generación de reportes descargables.

## 🚀 Características Principales
- **Acceso Seguro:** Sistema de login con validación de sesión (`Usuario: admin` | `Clave: 123`).
- **Registro Ágil:** Almacenamiento persistente en SQLite con fecha, descripción y monto.
- **Cálculo en Tiempo Real:** Suma automática del total de gastos acumulados.
- **Generación de Reportes:** Exportación directa a formato **CSV (Excel)** y vista optimizada para **Impresión / PDF**.

## 📸 Capturas de la Aplicación

### 1. Pantalla de Inicio de Sesión
![Pantalla de Login](capturas/login.png)

### 2. Panel Principal y Reportes
![Dashboard de Gastos](capturas/dashboard.png)

## ⚙️ Funcionamiento e Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/luzarcosfuentes-cmd/SITIO-WEB.git
   cd SITIO-WEB
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

4. **Abrir en el navegador:**
   Ingresa a `http://127.0.0.1:5000` e inicia sesión con:
   - **Usuario:** `admin`
   - **Contraseña:** `123`
