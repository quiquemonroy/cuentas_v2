import sqlite3
from datetime import datetime
from secrets import DB_LINK

NOW = f'cuentas_{datetime.now().strftime("%m%Y")}'
GRUPO = "Familia Culopocho"


class DbManagement:
    """
    Clase que hace la gestión de toda la base de datos.
    Si no existe la base de datos cuentas, crea la base de datos.

    Contiene todas las funciones necesarias para usar el programa.
    No edita ni borra datos, pero hace.
         - Crea la base de datos.
         - Crea una tabla con el nombre del mes en curso, hay que darle esta variable.
         - Escribe entradas en la base de datos.
         - Lee los datos.
         - Apaña las cuantas.

    """
    def __init__(self, month):
        # conectar a sqlite3
        self.db = DB_LINK
        self.c = self.db.cursor()
        self.c.execute(f'''CREATE TABLE IF NOT EXISTS {month} (
                                                        NOMBRE TEXT,
                                                        GASTO FLOAT,
                                                        CONCEPTO TEXT,
                                                        GRUPO TEXT);''')
        self.db.commit()

    # añadir gasto
    def nuevo_gasto(self, nombre, gasto, concepto, mes, grupo):
        nombre = nombre.strip().title()
        self.c.execute(
            f'INSERT INTO {mes} (NOMBRE,GASTO,CONCEPTO,GRUPO) VALUES ("{nombre}", {gasto}, "{concepto}", "{grupo}")')
        self.db.commit()
        print(f"Gasto añadido en el grupo {grupo}, el mes {mes[8:10]} de {mes[10:]}: {nombre} - {gasto}€ - {concepto}")

    def obtener_gastos_por_nombre(self, mes, usuario, grupo):
        usuario = usuario.strip().title()
        self.c.execute(f'SELECT * FROM {mes} WHERE NOMBRE="{usuario}" and GRUPO="{grupo}"')
        return self.c.fetchall()

    def gasto_total_mensual(self, mes, usuario, grupo):
        usuario = usuario.strip().title()
        self.c.execute(f'SELECT * FROM {mes} WHERE NOMBRE="{usuario}" and GRUPO="{grupo}"')
        total_mensual = 0
        for row in self.c.fetchall():
            total_mensual += row[1]
        return round(total_mensual, 1)

    def obtener_datos_gasto(self, mes, grupo):
        self.c.execute(f'SELECT NOMBRE FROM {mes} WHERE GRUPO="{grupo}"')
        lista_usuarios = []
        for row in set(self.c.fetchall()):
            lista_usuarios.append(row[0])
        gastos = {}
        suma = 0
        deben = {}
        se_debe_a = []
        for usuario in lista_usuarios:  # calcula el gasto total mensual
            gastos[usuario] = self.gasto_total_mensual(mes, usuario, grupo)
            suma += self.gasto_total_mensual(mes, usuario, grupo)
        try:
            gasto_esperado = round(suma / len(lista_usuarios), 1)
        except ZeroDivisionError:
            return "No hay datos suficientes aún para hacer esto."
        for usuario in lista_usuarios:  # calcula quien debe y a quien se debe
            gastos[usuario] = self.gasto_total_mensual(mes, usuario, grupo)
            if gastos[usuario] < gasto_esperado and gastos[usuario] - gasto_esperado < 0.5:
                deben[usuario] = round(gasto_esperado - gastos[usuario], 1)
            elif gastos[usuario] > gasto_esperado and gastos[usuario] - gasto_esperado > 0.5:
                se_debe_a.append((usuario, round(gastos[usuario] - gasto_esperado, 1)))
        return {"suma_total": suma,
                "gastos_usuarios": gastos,
                "deben": deben,
                "se_debe_a": se_debe_a,
                "gasto_esperado": gasto_esperado}

        # return f'''
        # Suma de gasto total mensual: {suma}
        # Gastos = {gastos}
        # {deben} y {deben} deben {deben[0][1]+deben[1][1]} a esta gente = {se_debe_a}
        # Gasto esperado por cada usuario= {gasto_esperado}'''

    def arreglar_cuentas(self, mes, usuario, grupo):
        usuario = usuario.strip().title()
        datos = self.obtener_datos_gasto(mes, grupo)
        try:
            if usuario in datos["deben"]:
                cantidad_debida = datos["deben"][usuario]
                por_acreedor = round((cantidad_debida / len(datos["se_debe_a"])), 1) * -1
                concepto = f'INGRESO DE {usuario}'
                self.nuevo_gasto(usuario, cantidad_debida, "ARREGLAR CUENTAS", mes, grupo)
                for acreedor in datos["se_debe_a"]:
                    self.nuevo_gasto(acreedor[0], por_acreedor, concepto, mes, grupo)
                print("Gasto apañado")
            else:
                print(f'{usuario} no debe nada')
        except TypeError:
            print("No hay datos suficientes aún para hacer esto.")


if __name__ == "__main__":
    # conectar a sqlite3
    app = DbManagement("tabla5")
    app.db = sqlite3.connect('cuentas.db')
    app.c = app.db.cursor()

    # app.nuevo_gasto("eugenia",13.53,"noseque",NOW, GRUPO)
    # print(app.obtener_gastos_por_nombre(NOW, "sagra",GRUPO))
    # print(app.gasto_total_mensual(NOW, "eugenia", GRUPO))
    # print(app.obtener_datos_gasto(NOW, GRUPO))
    # app.arreglar_cuentas(NOW,"Quique",GRUPO)

    app.db.close()
