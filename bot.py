import logging, sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder,
                          ContextTypes,
                          CommandHandler,
                          MessageHandler,
                          filters, CallbackQueryHandler,
                          ConversationHandler
                          )
from secrets import TELEGRAM_TOKEN, USUARIOS
from DB_MANAGEMENT_DOC import DbManagement

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

[START_ROUTES,
 END_ROUTES,
 NUEVO_GASTO,
 ARREGLAR_CUENTAS,
 GET_IMPORTE,
 GET_CONCEPTO_DESDE_GASTO] = range(6)
[ONE,
 TWO,
 THREE,
 FOUR,
 FIVE,
 SIX] = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.replace("/", "")
    logger.info("Muevo MENU de %s (id:%s)", update.message.from_user.first_name, update.message.from_user.id)
    if update.message.from_user.id in USUARIOS:
        keyboard = [
            [
                InlineKeyboardButton("Registrar Gasto", callback_data=str(ONE)),
                InlineKeyboardButton("Ayuda", callback_data=str(TWO)),
                InlineKeyboardButton("Panel de control", callback_data=str(THREE)),
            ],
            [InlineKeyboardButton("Hacer cuentas", callback_data=str(FOUR))],
            [InlineKeyboardButton("Apañar cuentas", callback_data=str(FIVE))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        menu = """💸💸*CUENTAS FAMILIARES*💸💸
    
    \-\-Usa el menú para elegir qué hacer\.\-\-
    
    🔴Si has gastado algo de dinero y quieres apuntarlo, haz click en Registrar gasto\.
    
    🔴Hacer cuentas muestra un resumen de lo que hemos gastado cada una este mes\.
    
    🔴Apañar cuentas sirve para registrar cuando ya has hecho bizum o algo así\.
    
    🔴Ver ayuda muestra la ayuda\.
    
    🔴Panel de control\."""

        await update.message.reply_text(text=menu, parse_mode="MarkdownV2", reply_markup=reply_markup)
        return START_ROUTES
    else:
        await update.message.reply_text(text="Usuario no autorizado", parse_mode="MarkdownV2")


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Registrar Gasto", callback_data=str(ONE)),
            InlineKeyboardButton("Ayuda", callback_data=str(TWO)),
            InlineKeyboardButton("Panel de control", callback_data=str(THREE)),
        ],
        [InlineKeyboardButton("Hacer cuentas", callback_data=str(FOUR))],
        [InlineKeyboardButton("Apañar cuentas", callback_data=str(FIVE))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    menu = """💸💸*CUENTAS FAMILIARES*💸💸

        \-\-Usa el menú para elegir qué hacer\.\-\-

        🔴Si has gastado algo de dinero y quieres apuntarlo, haz click en Registrar gasto\.

        🔴Hacer cuentas muestra un resumen de lo que hemos gastado cada una este mes\.

        🔴Apañar cuentas sirve para registrar cuando ya has hecho bizum o algo así\.

        🔴Ver ayuda muestra la ayuda\.

        🔴Panel de control\."""

    await query.edit_message_text(text=menu, parse_mode="MarkdownV2", reply_markup=reply_markup)
    return START_ROUTES


async def gasto_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Supermercado", callback_data="concepto_Supermercado"),
            InlineKeyboardButton("Comer fuera", callback_data="concepto_Comer Fuera"),
            InlineKeyboardButton("Niños", callback_data="concepto_Niños"),
        ],
        [
            InlineKeyboardButton("Hipoteca", callback_data="concepto_Hipoteca"),
            InlineKeyboardButton("Recibos", callback_data="concepto_Recibos"),
            InlineKeyboardButton("Otros gastos", callback_data="concepto_Otros gastos"),
        ],
        [
            InlineKeyboardButton("Volver al menu", callback_data=str(ONE)),
            InlineKeyboardButton("Salir", callback_data=str(TWO))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = """Vamos a registrar un nuevo gasto\.
        Por favor, selecciona un concepto\."""
    await query.edit_message_text(text=texto, parse_mode="MarkdownV2", reply_markup=reply_markup,
                                  api_kwargs={"concepto": "Supermercado", "importe": "23"})
    return NUEVO_GASTO


async def ayuda_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[
        InlineKeyboardButton("Volver al menu", callback_data=str(ONE)),
        InlineKeyboardButton("Salir", callback_data=str(TWO))
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = """ESTA ES LA AYUDA \(no ayuda mucho, la verdad\)"""
    await query.edit_message_text(text=texto, parse_mode="MarkdownV2", reply_markup=reply_markup)
    return END_ROUTES


async def panel_control_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[
        InlineKeyboardButton("Volver al menu", callback_data=str(ONE)),
        InlineKeyboardButton("Salir", callback_data=str(TWO))
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = """Este es el panel de control, aún está por hacer."""
    await query.edit_message_text(text=texto, reply_markup=reply_markup)
    return END_ROUTES


async def hacer_cuentas_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Arreglar cuentas", callback_data=str(THREE))
        ],
        [
            InlineKeyboardButton("Volver al menu", callback_data=str(ONE)),
            InlineKeyboardButton("Salir", callback_data=str(TWO))
        ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    MONTH, YEAR = datetime.now().strftime("%m"), datetime.now().strftime("%Y")
    GRUPO = "Familia Culopocho"
    db = DbManagement(MONTH, YEAR)
    datos_gasto = db.obtener_datos_gasto(MONTH, YEAR, GRUPO)
    # print(datos)
    gastos_por_usuario = {row: f'{datos_gasto["gastos_usuarios"][row]}€' for row in datos_gasto["gastos_usuarios"]}
    gastos_str = ""
    for row in datos_gasto["gastos_usuarios"]:
        gastos_str += f'Total {row} : {datos_gasto["gastos_usuarios"][row]}€\n'
    se_debe_str = ""
    for row in datos_gasto["se_debe_a"]:
        se_debe_str += f'{row[0]} ({row[1]}€)\n'
    deben_str = ""
    deudas = db.calcular_deudas_detalladas(MONTH,YEAR, GRUPO)
    print(deudas)
    for row in deudas["deudas"]:
        deben_str += f'{row[0]} debe a {row[1]} {row[2]}€\n'
    tabla_gastos = ""  # Inicio del bloque de código monoespaciado
    for usuario in datos_gasto["usuarios"]:
        datos = db.obtener_datos_por_nombre(MONTH, YEAR, usuario, GRUPO)
        tabla_gastos += f'{datos["name"]}\n'
        tabla_gastos += '  {:<8} {:<20} {:<10}\n'.format('GASTO', 'CONCEPTO', 'FECHA')
        for gasto in datos["gastos"]:
            # Formatear cada línea con espacios fijos
            fecha_formateada = str(gasto[2])[:-14]  # Asumiendo que gasto[2] es la fecha
            tabla_gastos += '  {:<8} {:<20} {:<10}\n'.format(
                f'{gasto[0]}€',
                gasto[1],
                fecha_formateada
            )
    tabla_gastos += "=" * 10 + "\n"  # Línea separadora
    texto = f"""{tabla_gastos}\nResumen de {MONTH}-{YEAR}: 
{gastos_str}
Gasto esperado por cada persona: {datos_gasto['gasto_esperado']}€
Se bebe a:
{se_debe_str}
Debe:
{deben_str}"""

    await query.edit_message_text(text=texto, reply_markup=reply_markup)
    return ARREGLAR_CUENTAS


async def arreglar_cuentas_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    MONTH, YEAR = datetime.now().strftime("%m"), datetime.now().strftime("%Y")
    GRUPO = "Familia Culopocho"
    nombre = update.effective_user.first_name
    db = DbManagement(MONTH, YEAR)
    datos_gasto = db.calcular_deudas_detalladas(MONTH,YEAR,GRUPO)
    debes = ""
    print(datos_gasto)
    for row in datos_gasto["deudas"]:
        if row[0] == nombre:
            debes += f'{row[2]}€ a {row[1]}\n'
    if debes:
        texto = f'Debes:\n{debes}\n¿Quieres apañar las cuentas?, dale a sí, sólo si ya has hecho BIZUM, transferencia o lo que sea '
        keyboard = [[
            InlineKeyboardButton("Sip, ya he hecho BIZUM", callback_data=str(THREE))
        ],
            [
                InlineKeyboardButton("Nop", callback_data=str(ONE)),
                InlineKeyboardButton("Salir", callback_data=str(TWO)),
            ],
        ]
    else:
        texto = "No debes nada!"
        keyboard = [
            [
                InlineKeyboardButton("Menu", callback_data=str(ONE)),
                InlineKeyboardButton("Salir", callback_data=str(TWO)),
            ],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=texto, reply_markup=reply_markup)
    return END_ROUTES


async def confirmar_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[
        InlineKeyboardButton("Eso he hecho, justo.", callback_data=str(THREE))
    ],
        [
            InlineKeyboardButton("Nop", callback_data=str(ONE)),
            InlineKeyboardButton("Salir", callback_data=str(TWO)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = """Quieres apañar las cuentas, dale a sí, sólo si ya has hecho BIZUM, transferencia o lo que sea"""
    await query.edit_message_text(text=texto, parse_mode="MarkdownV2", reply_markup=reply_markup)
    return END_ROUTES


async def obtener_importe_desde_concepto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['concepto'] = update.callback_query.data.replace("concepto_", "")
    keyboard = [
        [
            InlineKeyboardButton("Volver al menu", callback_data=str(ONE)),
            InlineKeyboardButton("Salir", callback_data=str(TWO)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = f"""Ok, ¿cuánto te has gastado?"""
    await query.edit_message_text(text=texto)
    # context.user_data['concepto'] = None
    return GET_IMPORTE


async def grabar_importe_concepto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        MONTH, YEAR = datetime.now().strftime("%m"), datetime.now().strftime("%Y")
        GRUPO = "Familia Culopocho"
        importe = float(update.message.text.replace(",", "."))
        concepto = context.user_data.get("concepto", "concepto desconocido")
        db = DbManagement(MONTH, YEAR)
        db.nuevo_gasto(nombre=update.message.from_user.first_name, gasto=importe, concepto=concepto, month=MONTH,
                       year=YEAR, grupo=GRUPO)
        await update.message.reply_text(f"✅ Gasto registrado:\nConcepto: {concepto}\nImporte: {importe}€")
        context.user_data["concepto"] = None
        logger.info("Nuevo gasto registrado de %s (id:%s): %s %s€", update.message.from_user.first_name,
                    update.message.from_user.id, concepto, importe)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text(f"Por favor, introduce un numero válido")


async def grabar_concepto_desde_importe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    MONTH, YEAR = datetime.now().strftime("%m"), datetime.now().strftime("%Y")
    GRUPO = "Familia Culopocho"
    importe = context.user_data.get("importe")
    concepto = update.callback_query.data.replace("concepto_", "")
    db = DbManagement(MONTH, YEAR)
    db.nuevo_gasto(nombre=update.effective_user.first_name, gasto=importe, concepto=concepto, month=MONTH, year=YEAR,
                   grupo=GRUPO)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"✅ Gasto registrado:\nConcepto: {concepto}\nImporte: {importe}€")
    logger.info("Nuevo gasto registrado de %s (id:%s): %s %s€", update.effective_user.first_name,
                update.effective_user.id, concepto, importe)

    context.user_data["importe"] = None
    return ConversationHandler.END


async def obtener_concepto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        importe = float(update.message.text.replace(",", "."))
        if importe > 0:
            context.user_data['importe'] = importe
            keyboard = [
                [
                    InlineKeyboardButton("Supermercado", callback_data="concepto_Supermercado"),
                    InlineKeyboardButton("Comer fuera", callback_data="concepto_Comer fuera"),
                    InlineKeyboardButton("Niños", callback_data="concepto_Niños"),
                ],
                [
                    InlineKeyboardButton("Hipoteca", callback_data="concepto_Hipoteca"),
                    InlineKeyboardButton("Recibos", callback_data="concepto_Recibos"),
                    InlineKeyboardButton("Otros gastos", callback_data="concepto_Otros gastos"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            texto = f"""Vamos a registrar un importe de {importe}.
Por favor, elige el concepto."""
            await update.message.reply_text(texto, reply_markup=reply_markup)
            return GET_CONCEPTO_DESDE_GASTO
        else:
            keyboard = [
                [
                    InlineKeyboardButton("Sip", callback_data=str(ONE)),
                    InlineKeyboardButton("Nop", callback_data=str(TWO))
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text="No te entiendo, ¿quieres ir al menú?", reply_markup=reply_markup)
            return GET_CONCEPTO_DESDE_GASTO
    except ValueError:
        keyboard = [
            [
                InlineKeyboardButton("Sip", callback_data=str(ONE)),
                InlineKeyboardButton("Nop", callback_data=str(TWO))
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text="No te entiendo, ¿quieres ir al menú?", reply_markup=reply_markup)
        return GET_CONCEPTO_DESDE_GASTO


async def salir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      MessageHandler(filters=filters.TEXT & (~filters.COMMAND), callback=obtener_concepto)
                      ],
        states={
            START_ROUTES: [
                CallbackQueryHandler(gasto_1, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(ayuda_2, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(panel_control_3, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(hacer_cuentas_4, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(arreglar_cuentas_5, pattern="^" + str(FIVE) + "$"),
                MessageHandler(filters=filters.TEXT & (~filters.COMMAND), callback=obtener_concepto)
            ],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salir, pattern="^" + str(TWO) + "$"),
            ],
            NUEVO_GASTO: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salir, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(obtener_importe_desde_concepto, pattern="^concepto_")
            ],
            ARREGLAR_CUENTAS: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salir, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(arreglar_cuentas_5, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(arreglar_cuentas_5, pattern="^" + str(FOUR) + "$")
            ],
            GET_IMPORTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, grabar_importe_concepto)
            ],
            GET_CONCEPTO_DESDE_GASTO: [
                CallbackQueryHandler(grabar_concepto_desde_importe, "^concepto_"),
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salir, pattern="^" + str(TWO) + "$"),

            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
