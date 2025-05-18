datos = {'suma_total': 235306.7,
         'gastos_usuarios': {'Sagra': 67.6, 'Eugenia': 189.4, 'Quique': 235049.7},
         'deben': {'Sagra': 78368.0,
                   'Eugenia': 78246.2},
         'se_debe_a': [('Quique', 156614.1)],
         'gasto_esperado': 78435.6
         }
por_usuario = {row: datos["gastos_usuarios"][row] for row in datos["gastos_usuarios"]}
print(por_usuario)
