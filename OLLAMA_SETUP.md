# 🦙 Configuración de Ollama para AI Study Assistant

## 📋 Requisitos Previos

1. **Instalar Ollama** en tu sistema
   - Windows: Descarga desde [ollama.ai](https://ollama.ai/download)
   - Después de instalar, Ollama se ejecutará automáticamente en segundo plano

## 🚀 Pasos para Configurar Ollama

### 1️⃣ Descargar Modelos

Abre una terminal (PowerShell o CMD) y ejecuta:

```powershell
# Descargar el modelo LLM principal (elige uno)
ollama pull llama3.2          # Recomendado - Rápido y eficiente (3B parámetros)
# o
ollama pull llama3.2:1b       # Más rápido, menos memoria
# o
ollama pull mistral           # Alternativa potente
# o
ollama pull llama3.1:8b       # Mayor calidad, requiere más recursos

# Descargar el modelo de embeddings (REQUERIDO)
ollama pull nomic-embed-text  # Para convertir texto en vectores
```

### 2️⃣ Verificar que Ollama está Funcionando

```powershell
# Ver modelos instalados
ollama list

# Probar un modelo
ollama run llama3.2
# Escribe algo y presiona Enter para probar
# Escribe /bye para salir
```

### 3️⃣ Configurar la Aplicación

Edita `src/config/settings.py` si necesitas cambiar el modelo:

```python
# Cambiar el modelo LLM (usa el que descargaste)
OLLAMA_MODEL_NAME = "llama3.2"  # o "mistral", "llama3.1:8b", etc.

# Cambiar URL si Ollama está en otro servidor
OLLAMA_BASE_URL = "http://localhost:11434"

# Modelo de embeddings (debe coincidir con lo descargado)
OLLAMA_EMBEDDINGS_MODEL = "nomic-embed-text"
```

### 4️⃣ Usar Ollama en la Aplicación

1. **Ejecuta la aplicación:**
   ```powershell
   # Activa el entorno virtual
   .venv\Scripts\Activate.ps1
   
   # Ejecuta Streamlit
   streamlit run app.py
   ```

2. **Selecciona "ollama" en el menú de modelos** en la pestaña "AI Chat Assistant"

3. **¡Listo!** Ahora puedes hacer preguntas sobre tus documentos usando Ollama localmente

## 🔧 Configuración Avanzada

### Usar Solo Ollama (Sin Google/OpenAI)

Si quieres usar SOLO Ollama y no necesitas las APIs de Google o OpenAI:

1. **Modifica `.streamlit/secrets.toml`** (o créalo si no existe):
   ```toml
   # Deja vacío o comenta las API keys
   # GOOGLE_API_KEY = ""
   # OPENAI_API_KEY = ""
   ```

2. La aplicación automáticamente detectará y mostrará solo "ollama" como opción

### Usar Embeddings de Ollama

Para usar embeddings de Ollama en lugar de Google (recomendado para uso totalmente local):

**Edita `src/services/vector_store.py`:**

```python
# Busca estas líneas (aparecen 2 veces en el archivo):
embeddings = LLMService.load_embeddings()

# Cámbiala a:
embeddings = LLMService.load_embeddings(use_ollama=True)
```

## 📊 Modelos Recomendados

| Modelo | Tamaño | Memoria RAM | Velocidad | Calidad |
|--------|--------|-------------|-----------|---------|
| llama3.2:1b | 1.3 GB | 4 GB | ⚡⚡⚡ | ⭐⭐ |
| llama3.2 | 2 GB | 8 GB | ⚡⚡ | ⭐⭐⭐ |
| mistral | 4 GB | 8 GB | ⚡⚡ | ⭐⭐⭐⭐ |
| llama3.1:8b | 4.7 GB | 16 GB | ⚡ | ⭐⭐⭐⭐⭐ |

## ❓ Solución de Problemas

### Error: "Connection refused" o "Cannot connect to Ollama"

**Solución:**
1. Verifica que Ollama esté corriendo:
   ```powershell
   # En Windows, busca "Ollama" en la bandeja del sistema (system tray)
   # O ejecuta:
   ollama serve
   ```

2. Prueba la conexión:
   ```powershell
   curl http://localhost:11434
   # Debe devolver "Ollama is running"
   ```

### Error: "Model not found"

**Solución:**
1. Verifica que el modelo esté descargado:
   ```powershell
   ollama list
   ```

2. Si no está, descárgalo:
   ```powershell
   ollama pull llama3.2
   ```

### La Aplicación es Muy Lenta

**Soluciones:**
1. Usa un modelo más pequeño: `llama3.2:1b`
2. Reduce el número de documentos
3. Cierra otras aplicaciones para liberar RAM
4. Considera usar embeddings de Google (más rápido para procesar PDFs)

### Error al Crear Embeddings

Si usas embeddings de Ollama y falla:

1. Verifica que `nomic-embed-text` esté instalado:
   ```powershell
   ollama list
   # Debe aparecer nomic-embed-text
   ```

2. Si no está:
   ```powershell
   ollama pull nomic-embed-text
   ```

## 🎯 Ventajas de Usar Ollama

✅ **Totalmente Gratis** - Sin costos de API  
✅ **Privacidad Total** - Tus datos nunca salen de tu computadora  
✅ **Sin Límites** - Usa cuanto quieras sin restricciones  
✅ **Funciona Sin Internet** - Una vez descargados los modelos  
✅ **Rápido** - Respuestas instantáneas con modelos pequeños

## 🔗 Recursos Adicionales

- [Documentación oficial de Ollama](https://github.com/ollama/ollama)
- [Lista de modelos disponibles](https://ollama.ai/library)
- [Ollama Discord Community](https://discord.gg/ollama)

---

**¿Necesitas ayuda?** Abre un issue en el repositorio o consulta la documentación de Ollama.
