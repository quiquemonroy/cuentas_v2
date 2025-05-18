import sqlite3
from datetime import datetime
from secrets import DB_LINK


class DbManagement:
    """
    Clase para la gestión completa de la base de datos de gastos compartidos.

    Responsabilidades:
    - Crea la base de datos y tablas si no existen
    - Registra nuevos gastos
    - Proporciona consultas de gastos por usuario
    - Calcula balances y ajustes entre miembros del grupo
    - Realiza ajustes automáticos de cuentas

    Atributos:
        db: Conexión a la base de datos SQLite
        c: Cursor para ejecutar consultas SQL

    La base de datos sigue esta estructura:
        Tablas: Una por mes (formato 'cuentas_MMYYYY')
        Campos:
            - NOMBRE (TEXT): Nombre del usuario que registra el gasto
            - GASTO (FLOAT): Cantidad del gasto
            - CONCEPTO (TEXT): Descripción del gasto
            - GRUPO (TEXT): Nombre del grupo compartido
    """

    def __init__(self, month, year):
        """
        Inicializa la conexión con la base de datos y crea la tabla del mes actual si no existe.

        La tabla se nombra automáticamente según el mes y año actual (ej.: 'cuentas_052023').
        """
        # conectar a sqlite3
        self.db = DB_LINK
        self.c = self.db.cursor()
        self.c.execute(f'''CREATE TABLE IF NOT EXISTS cuentas_{month}_{year} (
                                                        NOMBRE TEXT,
                                                        GASTO FLOAT,
                                                        CONCEPTO TEXT,
                                                        GRUPO TEXT,
                                                        TIMESTAMP);''')
        self.db.commit()

    def nuevo_gasto(self, nombre, gasto, concepto, month, year, grupo):
        """
        Registra un nuevo gasto en la base de datos.

        Args:
            nombre (str): Nombre de la persona que realizó el gasto
            gasto (float): Cantidad del gasto
            concepto (str): Descripción del gasto
            mes (str): Mes de registro (nombre de tabla)
            grupo (str): Nombre del grupo compartido

        Returns:
            None, pero imprime confirmación del registro
        """
        nombre = nombre.strip().title()  # Normaliza formato del nombre
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.c.execute(
            f'INSERT INTO cuentas_{month}_{year} (NOMBRE,GASTO,CONCEPTO,GRUPO,TIMESTAMP) '
            f'VALUES (?,?,?,?,?)',(nombre,gasto,concepto,grupo,timestamp))
        self.db.commit()
        # print(f"Gasto añadido en el grupo {grupo}, el mes {month} de {year}: {nombre} - {gasto}€ - {concepto}")

    def obtener_datos_por_nombre(self, month, year, usuario, grupo):
        """
        Obtiene todos los gastos registrados por un usuario específico.

        Args:
            month (str): Mes a consultar (nombre de tabla)
            usuario (str): Nombre del usuario a consultar
            grupo (str): Nombre del grupo compartido

        Returns:
            list: Lista de tuplas con todos los gastos del usuario
            :param grupo:
            :param usuario:
            :param month:
            :param year:
        """
        usuario = usuario.strip().title()
        self.c.execute(
            f'SELECT GASTO,CONCEPTO,GRUPO,TIMESTAMP FROM cuentas_{month}_{year} WHERE NOMBRE="{usuario}" and GRUPO="{grupo}"')
        gastos_usuario = self.c.fetchall()
        total = 0
        gastos = {"name": usuario,
                  "mes": month,
                  "año": year,
                  "gastos": [(gasto[0], gasto[1], gasto[3]) for gasto in gastos_usuario],
                  "total gasto": round(sum([gasto[0] for gasto in gastos_usuario]), 1),
                  "grupo": set([grupo[2] for grupo in gastos_usuario])
                  }

        return gastos

    def gasto_total_mensual(self, month, year, usuario, grupo):
        """
        Calcula el gasto total acumulado por un usuario en un mes específico.

        Args:
            mes (str): Mes a consultar
            usuario (str): Nombre del usuario
            grupo (str): Nombre del grupo compartido

        Returns:
            float: Suma total de gastos redondeada a 1 decimal
        """
        usuario = usuario.strip().title()
        self.c.execute(f'SELECT * FROM cuentas_{month}_{year} WHERE NOMBRE="{usuario}" and GRUPO="{grupo}"')
        total_mensual = 0
        for row in self.c.fetchall():
            total_mensual += row[1]
        return round(total_mensual, 1)

    def obtener_datos_gasto(self, month, year, grupo):
        """
        Calcula el balance completo del grupo para un mes específico.

        Args:
            mes (str): Mes a consultar
            grupo (str): Nombre del grupo compartido

        Returns:
            dict or str: Diccionario con balances o mensaje de error si no hay datos.
            Estructura del diccionario:
            { "suma_total": float,  # Suma total de gastos del grupo
                "gastos_usuarios": dict,  # {usuario: gasto_total}
                "deben": dict,  # {usuario: cantidad_debida}
                "se_debe_a": list,  # [(acreedor, cantidad)]
                "gasto_esperado": float  # Gasto promedio por usuario
            }
        """
        self.c.execute(f'SELECT NOMBRE FROM cuentas_{month}_{year} WHERE GRUPO="{grupo}"')
        lista_usuarios = []
        for row in set(self.c.fetchall()):
            lista_usuarios.append(row[0])

        gastos = {}
        suma = 0
        deben = {}
        se_debe_a = []

        # Calcula gasto total por usuario y suma grupal
        for usuario in lista_usuarios:  # gasto total del grupo para el mes dado
            gastos[usuario] = self.gasto_total_mensual(month, year, usuario, grupo)
            suma += self.gasto_total_mensual(month, year, usuario, grupo)

        try:
            gasto_esperado = round(suma / len(lista_usuarios), 1)
        except ZeroDivisionError:
            gasto_esperado = 0

        # Determina balances individuales
        for usuario in lista_usuarios:
            gastos[usuario] = self.gasto_total_mensual(month, year, usuario, grupo)
            if gastos[usuario] < gasto_esperado and gastos[usuario] - gasto_esperado < 0.5:
                deben[usuario] = round(gasto_esperado - gastos[usuario], 1)
            elif gastos[usuario] > gasto_esperado and gastos[usuario] - gasto_esperado > 0.5:
                se_debe_a.append((usuario, round(gastos[usuario] - gasto_esperado, 1)))

        return {
            "suma_total": suma,
            "gastos_usuarios": gastos,
            "deben": deben,
            "se_debe_a": se_debe_a,
            "gasto_esperado": gasto_esperado,
            "usuarios" : lista_usuarios
        }

    def arreglar_cuentas(self, month, year, usuario, grupo):
        """
        Realiza ajustes automáticos de cuentas para equilibrar gastos.

        Si el usuario debe dinero, registra:
        1. Un gasto positivo del deudor por el total adeudado
        2. Gastos negativos para cada acreedor por su parte correspondiente

        Args:
            mes (str): Mes a ajustar
            usuario (str): Usuario que desea ajustar sus cuentas
            grupo (str): Nombre del grupo compartido

        Returns:
            None, pero imprime confirmación o mensaje de error
        """
        usuario = usuario.strip().title()
        datos = self.obtener_datos_gasto(month, year, grupo)

        try:
            if usuario in datos["deben"]:
                cantidad_debida = datos["deben"][usuario]
                por_acreedor = round((cantidad_debida / len(datos["se_debe_a"])), 1) * -1
                concepto = f'INGRESO DE {usuario}'

                # Registra ajustes
                self.nuevo_gasto(usuario, cantidad_debida, "ARREGLAR CUENTAS", month, year, grupo)
                for acreedor in datos["se_debe_a"]:
                    self.nuevo_gasto(acreedor[0], por_acreedor, concepto, month, year, grupo)
                print("Gasto apañado")
            else:
                print(f'{usuario} no debe nada')
        except TypeError:
            print("No hay datos suficientes aún para hacer esto.")


if __name__ == "__main__":
    MONTH, YEAR = datetime.now().strftime("%m"), datetime.now().strftime("%Y")
    GRUPO = "Familia Culopocho"  # Nombre del grupo por defecto
    # conectar a sqlite3
    app = DbManagement(MONTH, YEAR)
    app.db = sqlite3.connect('cuentas.db')
    app.c = app.db.cursor()

    # app.nuevo_gasto("Esti", 123.53, "cosas", month=MONTH, year=YEAR, grupo=GRUPO)
    # print(app.obtener_datos_por_nombre(month=MONTH, year=YEAR, usuario="eugenia", grupo=GRUPO))
    # print(app.gasto_total_mensual(month=MONTH, year=YEAR, usuario="sagra", grupo=GRUPO))
    # print(app.obtener_datos_gasto(month=MONTH,year=YEAR, grupo= GRUPO))
    # app.arreglar_cuentas(month=MONTH,year=YEAR,usuario="Quique",grupo=GRUPO)
    # user = app.obtener_datos_por_nombre(month=MONTH, year=YEAR, usuario="eugenia", grupo=GRUPO)
    # print(user)
    # print(user.get("grupos"))

    app.db.close()
