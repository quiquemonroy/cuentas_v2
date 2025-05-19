# Bot de Gestión de Gastos Familiares en Telegram

## Descripción
Este bot de Telegram ayuda a gestionar los gastos compartidos entre miembros de una familia o grupo. Permite registrar gastos, hacer un seguimiento de quién ha pagado qué, calcular balances y ajustar cuentas cuando se realizan pagos entre miembros.

## Características principales
- 📝 Registrar gastos comunes con concepto e importe
- 💰 Visualizar resumen mensual de gastos
- 📊 Consultar quién debe a quién y qué cantidades
- 🔄 Marcar pagos como realizados cuando se saldan deudas
- 🔔 Notificaciones automáticas entre miembros del grupo

## Requisitos
- Python 3.7+
- Bibliotecas requeridas (ver `requirements.txt`):
  - `python-telegram-bot`
  - `sqlite3`

## Configuración
1. Crear un archivo `secrets.py` con las siguientes variables:
   ```python
   TELEGRAM_TOKEN = "tu_token_de_bot"
   USUARIOS = [id_usuario1, id_usuario2]  # IDs de Telegram autorizados
   ESTI_ID = id_esti  # ID de un miembro
   QUIQUE_ID = id_quique  # ID de otro miembro
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso
Comandos principales:
- `/start` - Inicia el bot y muestra el menú principal
- Menú interactivo con opciones:
  - ℹ️ INFO - Muestra información sobre el bot
  - ⚙️ Panel de control - (en desarrollo)
  - 📝 Registrar Gasto - Añade un nuevo gasto compartido
  - 🎛️ Hacer cuentas - Muestra el balance actual
  - 💰 Apañar cuentas - Marca deudas como pagadas

## Estructura del código
- `DbManagement` - Clase para manejar la base de datos SQLite
- Handlers para cada estado de la conversación
- Funciones para:
  - Registrar nuevos gastos
  - Calcular balances
  - Mostrar resúmenes
  - Gestionar pagos entre miembros

## Base de datos
El bot utiliza SQLite para almacenar:
- Gastos individuales (usuario, concepto, importe, fecha)
- Balances mensuales
- Histórico de pagos

## Notificaciones
El bot envía notificaciones automáticas:
- Cuando un usuario registra un gasto
- Cuando un usuario marca una deuda como pagada

## Ejecución
```bash
python3 main.py
```

## Notas
- Diseñado para uso familiar/grupos pequeños
- Los datos se organizan por meses
- Requiere autorización explícita de usuarios (mediante ID de Telegram)

Hecho con ♥️ por Quique.
