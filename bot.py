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

START_ROUTES, END_ROUTES, NUEVO_GASTO, ARREGLAR_CUENTAS, GET_IMPORTE = range(5)
[ONE, TWO, THREE, FOUR, FIVE, SIX] = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("start")
    mensaje = update.message.text.replace("/", "")
    logger.info("Muevo comando de %s (id:%s)", update.message.from_user.first_name, update.message.from_user.id)
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
    print("start over")
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


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print("echo")
#     logger.info("Muevo mensaje de %s (id:%s): %s", update.message.from_user.first_name, update.message.from_user.id,
#                 update.message.text)
#     if update.message.text == "m":
#         await context.bot.send_message(chat_id=update.effective_chat.id,
#                                        text="/start")
#     try:
#         importe_gasto = float(update.message.text.strip().replace(",", "."))
#         await gasto(update, context, importe_gasto=importe_gasto)
#         return GET_CONCEPT
#     except ValueError:
#         await context.bot.send_message(chat_id=update.effective_chat.id,
#                                        text=f'{update.message.from_user.first_name} dijo:\n  {update.message.text} ')


async def gasto_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("gasto_1")
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
    await query.edit_message_text(text=texto, parse_mode="MarkdownV2", reply_markup=reply_markup, api_kwargs={"concepto": "Supermercado", "importe": "23"})
    return NUEVO_GASTO


async def ayuda_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("ayuda")
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
    print("panel de control")
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
    print("hacer cuentas")
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
    texto = """Estas son las cuentas: debes dinero"""
    await query.edit_message_text(text=texto, parse_mode="MarkdownV2", reply_markup=reply_markup)
    return ARREGLAR_CUENTAS


async def arreglar_cuentas_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("arreglar cuentas")
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Volver al menu", callback_data=str(ONE)),
            InlineKeyboardButton("Salir", callback_data=str(TWO)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = """Quieres arreglar las cuentas??"""
    await query.edit_message_text(text=texto, parse_mode="MarkdownV2", reply_markup=reply_markup)
    return END_ROUTES


async def append(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['concepto'] = update.callback_query.data.replace("concepto_","")
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


async def obtener_importe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        importe = float(update.message.text.replace(",","."))
        concepto = context.user_data.get("concepto", "concepto desconocido")
        await update.message.reply_text(f"✅ Gasto registrado:\nConcepto: {concepto}\nImporte: {importe}€")
        context.user_data["concepto"] = None
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text(f"Por favor, introduce un numero válido")


async def salir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("salir")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     # print(json.dumps(json.loads(query.to_json()), indent=4))  # print a json schema with query data
#     if query.data == "registrar_gasto":
#         print("hay que resistrar un gasto")
#         keyboard = [
#             [
#                 InlineKeyboardButton("Supermercado", callback_data="Supermercado"),
#                 InlineKeyboardButton("Comer fuera", callback_data="Comer fuera"),
#                 InlineKeyboardButton("Niños", callback_data="Niños"),
#             ],
#             [
#                 InlineKeyboardButton("Hipoteca", callback_data="Hipoteca"),
#                 InlineKeyboardButton("Recibos", callback_data="Recibos"),
#                 InlineKeyboardButton("Otros gastos", callback_data="Otros gastos"),
#             ]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         texto = """Vamos a registrar un nuevo gasto\.
#                 Por favor, selecciona un concepto\."""
#         await query.edit_message_text(text=texto, parse_mode="MarkdownV2", reply_markup=reply_markup)
#
#     elif query.data == "ayuda":
#         print("hay que mostrar la ayuda")
#     elif query.data == "panel_control":
#         print("hay que mostrar el panel de control")
#     elif query.data == "hacer_cuentas":
#         print("hay que hacer cuentas")
#     elif query.data == "arreglar_cuentas":
#         print("hay que arreglar cuentas")
#     elif query.data == "Supermercado":
#         print("registrar un gasto de supermercado")


def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(gasto_1, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(ayuda_2, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(panel_control_3, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(hacer_cuentas_4, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(arreglar_cuentas_5, pattern="^" + str(FIVE) + "$")
            ],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salir, pattern="^" + str(TWO) + "$"),
            ],
            NUEVO_GASTO: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salir, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(append, pattern="^concepto_")
            ],
            ARREGLAR_CUENTAS: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salir, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(arreglar_cuentas_5, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(arreglar_cuentas_5, pattern="^" + str(FOUR) + "$")
            ],
            GET_IMPORTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_importe)
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # application.add_handler(CommandHandler(command='start', callback=start))
    application.add_handler(conv_handler)
    # application.add_handler(MessageHandler(filters=filters.TEXT & (~filters.COMMAND), callback=echo))

    application.run_polling()


if __name__ == '__main__':
    main()
