# Ejercicio 1 · Quitar duplicados conservando el orden
ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]

vistas = set()      # conjunto de control: para preguntar rápido si ya apareció
unicas = []         # lista de resultado: conserva el orden
for ciudad in ciudades:
    if ciudad not in vistas:
        vistas.add(ciudad)
        unicas.append(ciudad)

print(unicas)   # ['Quito', 'Guayaquil', 'Cuenca']




# Ejercicio 2 · Contar con un diccionario
# Con la misma lista, arma un diccionario {"Quito": 2, "Guayaquil": 2, "Cuenca": 1}.
conteo = {}
for ciudad in ciudades:
    conteo[ciudad] = conteo.get(ciudad, 0) + 1     # .get evita el KeyError la primera vez

print(conteo)

# El más repetido:
mas_repetida = max(conteo, key=conteo.get)
print(mas_repetida)



# Ejercicio 3 · Conjuntos en acción
# inscritos_matematica = {"Ana","Luis","Sol","Marco"} y inscritos_ingles = {"Luis","Marco","Ruth"}. 
# Responde con código: ¿quiénes están en las dos?, ¿quiénes solo en matemática?, 
# ¿cuántos estudiantes distintos hay en total?
inscritos_matematica = {"Ana","Luis","Sol","Marco"}
inscritos_ingles = {"Luis","Marco","Ruth"}

ambas       = inscritos_matematica & inscritos_ingles     # {'Luis','Marco'}
solo_mate   = inscritos_matematica - inscritos_ingles     # {'Ana','Sol'}
total       = len(inscritos_matematica | inscritos_ingles)  # 5

print(sorted(ambas), sorted(solo_mate), total)


# Ejercicio 4 · De lista de diccionarios a índice
# Con clientes = [{"id":1,"nombre":"Ana"},{"id":2,"nombre":"Luis"}], 
# crea un diccionario {id: cliente} para acceder por id sin recorrer la lista. 
# Luego imprime el nombre del id 2.
clientes = [{"id":1,"nombre":"Ana"},{"id":2,"nombre":"Luis"}]
indice = {cliente["id"]: cliente for cliente in clientes}
print(indice[2]["nombre"])       # 'Luis'
# Diferencia de costo:
# recorrer la lista  -> revisa hasta N registros
# indice[2]          -> una sola operación, sin importar cuántos haya


# Ejercicio 5 · Tuplas como registros inmutables
# Dada ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)], 
# imprime el mes con mayor venta y el total, usando desempaquetado de tuplas.
ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)]
total = sum(monto for _mes, monto in ventas)

mejor_mes, mejor_monto = max(ventas, key=lambda venta: venta[1])

print(f"Total: {total}")
print(f"Mejor mes: {mejor_mes} con {mejor_monto}")

for mes, monto in ventas:              # desempaquetado en el for
    print(f"{mes:<10} {monto}")


# Ejercicio 6 · Sobre el proyecto
# Agrega al Controlador la función clientes_por_ciudad() 
# que devuelva un diccionario {"Guayaquil": ["Ana", "Luis"], "Quito": ["Sol"]}.
def clientes_por_ciudad():
    gestor = {"Guayaquil": ["Ana", "Luis"], "Quito": ["Sol"]}
    agrupados = {}
    for registro in gestor.leer():
        ciudad = registro.get("ciudad", "").title() or "Sin ciudad"
        # setdefault: si la ciudad no estaba, crea la lista vacía y luego agrega
        agrupados.setdefault(ciudad, []).append(registro["nombre"])
    return agrupados



# Ejercicio 7 · ¿Instancia, de clase o estático?
# Clasifica cada método y justifica: (a) calcular el total de una venta, 
# (b) crear un objeto Producto a partir de un diccionario, (c) saber si un precio es válido, 
# (d) saber si un producto tiene stock bajo, (e) calcular el IVA de cualquier monto.











# Ejercicio 8 · Un modelo nuevo con herencia
# Agrega la clase Proveedor, que hereda de Persona y suma ruc y empresa. 
# Escribe __init__, a_diccionario() y etiqueta() reutilizando al padre.
class Proveedor(Persona):

    def __init__(self, id_registro, nombre, apellido, email, ruc="", empresa=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.ruc = ruc
        self.empresa = empresa

    def a_diccionario(self):
        datos = super().a_diccionario()      # id + nombre + apellido + email
        datos["ruc"] = self.ruc
        datos["empresa"] = self.empresa
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.empresa or 'sin empresa'} · RUC {self.ruc}"


# Y desde_diccionario() ya funciona sin escribir nada:
p = Proveedor.desde_diccionario({"id": 1, "nombre": "Luis", "apellido": "Mora",
                                 "email": "luis@x.com", "ruc": "0912345678001",
                                 "empresa": "Importadora Sur"})
print(p)     # usa __str__ de ModeloBase -> etiqueta() de Proveedor




# Ejercicio 9 · Polimorfismo sin if
# Esta función tiene el olor a “falta polimorfismo”. Reescríbela sin ningún if de tipo.
# def describir(objeto, tipo):
#     if tipo == "cliente":
#         return f"{objeto.nombre} {objeto.apellido} de {objeto.ciudad}"
#     elif tipo == "producto":
#         return f"{objeto.nombre} a ${objeto.precio}"
#     elif tipo == "venta":
#         return f"venta de {objeto.cantidad} unidades"

# Cada clase ya sabe describirse: solo hay que preguntarle.
objeto= 2
def describir(objeto):
    return objeto.etiqueta()

# o directamente:
print(objeto)      # __str__ de ModeloBase llama a etiqueta()




# Ejercicio 10 · Atributo estático nuevo
# Agrega a Producto el atributo estático DESCUENTO_MAYORISTA = 0.10 
# y el método estático precio_mayorista(precio, cantidad), 
# que aplica el descuento solo si la cantidad es 12 o más. 
# Úsalo en el comprobante.
class Producto(ModeloBase):
    DESCUENTO_MAYORISTA = 0.10
    CANTIDAD_MAYORISTA = 12

    @staticmethod
    def precio_mayorista(precio, cantidad):
        if cantidad >= Producto.CANTIDAD_MAYORISTA:
            return round(precio * (1 - Producto.DESCUENTO_MAYORISTA), 2)
        return round(precio, 2)


# En views.crear_venta(), al armar la venta:
precio = Producto.precio_mayorista(producto.precio, int(datos["cantidad"]))
venta = Venta(siguiente_id(gestor_ventas), int(datos["cliente_id"]),
              producto.id, int(datos["cantidad"]), precio)