from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
# Solo dice QUÉ métodos debe tener todo controlador.
# CÓMO se hace cada uno lo escribe cada controlador, de la forma más simple.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE ESTUDIANTES
# =====================================================================
class EstudianteController(CrudBase):

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)

        # Leemos el JSON y convertimos cada diccionario en un objeto Estudiante
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for estudiante in self.lista:
            datos.append(estudiante.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Devuelve un mensaje de error, o None si todo está bien."""
        # Al crear hay que traer los tres obligatorios; al actualizar, solo lo que cambia
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO con los emails de los OTROS estudiantes
            usados = {e.email for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        telefono = str(datos.get("telefono", "")).strip()
        if telefono != "" and not telefono.isdigit():
            return "El teléfono solo puede tener números"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for estudiante in self.lista:
            if (texto in estudiante.nombre.lower()
                    or texto in estudiante.apellido.lower()
                    or texto in estudiante.email
                    or texto in estudiante.telefono
                    or texto in estudiante.carrera.lower()):
                encontrados.append(estudiante)
        return encontrados

    def siguiente(self):
        mayor = 0
        for estudiante in self.lista:
            if estudiante.id > mayor:
                mayor = estudiante.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(self.siguiente(),
                                str(datos["nombre"]).strip().title(),
                                str(datos["apellido"]).strip().title(),
                                str(datos["email"]).strip().lower(),
                                str(datos.get("telefono", "")).strip(),
                                str(datos.get("carrera", "")).strip().title())
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        # DIFERENCIA de conjuntos: campos que no existen en un estudiante
        permitidos = {"nombre", "apellido", "email", "telefono", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        # Se valida ANTES de tocar el objeto: si algo falla, no cambia nada
        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    # --- propio de estudiantes ---
    def carreras(self):
        """CONJUNTO de carreras: sin repetidos. sorted() lo devuelve como lista."""
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


# =====================================================================
# CONTROLADOR DE MATERIAS
# =====================================================================
class MateriaController(CrudBase):

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for materia in self.lista:
            datos.append(materia.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "creditos"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        # es_creditos_valido es el método ESTÁTICO de Materia
        if "creditos" in datos and not Materia.es_creditos_valido(datos["creditos"]):
            return (f"Créditos inválidos: '{datos['creditos']}' "
                    f"(entero entre 1 y {Materia.MAX_CREDITOS})")

        cupo = str(datos.get("cupo", "")).strip()
        if cupo != "" and not cupo.isdigit():
            return "El cupo debe ser un número entero positivo"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otra in self.lista:
                if otra.nombre == nombre and otra.id != id_actual:
                    return f"Ya existe una materia llamada {nombre}"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas

        for materia in self.lista:
            if texto in materia.nombre.lower():
                encontradas.append(materia)
        return encontradas

    def siguiente(self):
        mayor = 0
        for materia in self.lista:
            if materia.id > mayor:
                mayor = materia.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        # Si no escribieron el cupo, empieza en 0
        cupo = str(datos.get("cupo", "")).strip()
        materia = Materia(self.siguiente(),
                          str(datos["nombre"]).strip().title(),
                          int(datos["creditos"]),
                          int(cupo) if cupo != "" else 0)
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "creditos", "cupo"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupo" in datos:
            materia.cupo = int(datos["cupo"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"

        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    # --- propio de materias ---
    def con_cupo_bajo(self):
        bajas = []
        for materia in self.lista:
            if materia.cupo_bajo():
                bajas.append(materia)
        return bajas


# =====================================================================
# CONTROLADOR DE MATRÍCULAS
# =====================================================================
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        # La matrícula USA a los otros dos controladores.
        # Hay que pasarle los MISMOS que usa main.py.
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for matricula in self.lista:
            datos.append(matricula.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números enteros"

        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe un estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe una materia con id {materia_id}"

        # Un estudiante no puede matricularse dos veces en la misma materia
        for m in self.lista:
            if m.estudiante_id == estudiante_id and m.materia_id == materia_id:
                return f"El estudiante ya está matriculado en {materia.nombre}"

        if not materia.hay_cupo():
            return f"No hay cupo disponible en {materia.nombre}"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for matricula in self.lista:
            if matricula.id == id_matricula:
                return matricula
        return None

    def buscar(self, texto):
        # Las matrículas se buscan por fecha, ej: "2026-10"
        texto = texto.strip()
        encontradas = []
        if texto == "":
            return encontradas

        for matricula in self.lista:
            if texto in matricula.fecha:
                encontradas.append(matricula)
        return encontradas

    def siguiente(self):
        mayor = 0
        for matricula in self.lista:
            if matricula.id > mayor:
                mayor = matricula.id
        return mayor + 1

    def crear(self, datos):
        # datos = {"estudiante_id": 1, "materia_id": 2}
        error = self.validar(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))
        matricula = Matricula(self.siguiente(),
                              int(datos["estudiante_id"]),
                              materia.id)

        materia.ocupar_cupo()
        self.materias.guardar()                 # guarda el cupo nuevo en materias.json
        self.lista.append(matricula)
        self.guardar()                          # guarda la matrícula en matriculas.json
        return True, f"Matrícula {matricula.id} registrada en {materia.nombre}"

    def actualizar(self, id_matricula, datos):
        """Lo único que se modifica de una matrícula es su nota."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nota"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        # es_nota_valida es el método ESTÁTICO de Materia
        if not Materia.es_nota_valida(datos["nota"]):
            return False, (f"Nota inválida: '{datos['nota']}' "
                           f"(debe estar entre 0 y {Materia.NOTA_MAXIMA})")

        matricula.calificar(datos["nota"])
        self.guardar()
        return True, f"Nota registrada: {matricula.nota:.2f} ({matricula.estado()})"

    def eliminar(self, id_matricula):
        """Retirar una matrícula: se borra y el cupo vuelve a la materia."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula {id_matricula} retirada y cupo devuelto"

    # --- propio de matrículas ---
    def matriculas_de(self, id_estudiante):
        encontradas = []
        for matricula in self.lista:
            if matricula.estudiante_id == id_estudiante:
                encontradas.append(matricula)
        return encontradas

    def promedio_de(self, id_estudiante):
        """Promedio de las notas ya registradas; None si no tiene ninguna."""
        notas = [m.nota for m in self.matriculas_de(id_estudiante) if m.nota is not None]
        if not notas:
            return None
        return round(sum(notas) / len(notas), 2)

    def promedio_general(self):
        notas = [m.nota for m in self.lista if m.nota is not None]
        if not notas:
            return None
        return round(sum(notas) / len(notas), 2)

    def reporte(self, id_estudiante):
        """Récord académico del estudiante. None si el estudiante no existe."""
        estudiante = self.estudiantes.obtener(id_estudiante)
        if estudiante is None:
            return None

        propias = self.matriculas_de(id_estudiante)
        texto = f"RÉCORD ACADÉMICO — {estudiante.nombre_completo()}\n"
        texto += f"Carrera : {estudiante.carrera or 'sin carrera'}\n"
        texto += "-" * 52 + "\n"

        creditos_aprobados = 0
        if not propias:
            texto += "Sin materias matriculadas\n"
        for m in propias:
            materia = self.materias.obtener(m.materia_id)
            nombre = materia.nombre if materia else "eliminada"
            nota = "  -  " if m.nota is None else f"{m.nota:5.2f}"
            texto += f"{nombre:<26} {nota}  {m.estado()}\n"
            if materia and m.estado() == "Aprobada":
                creditos_aprobados += materia.creditos

        promedio = self.promedio_de(id_estudiante)
        texto += "-" * 52 + "\n"
        texto += f"PROMEDIO: {promedio if promedio is not None else '-'}\n"
        texto += f"CRÉDITOS APROBADOS: {creditos_aprobados}"
        return texto

    def matriculas_por_estudiante(self):
        """DICCIONARIO de LISTAS: {estudiante_id: [matrículas de ese estudiante]}."""
        agrupadas = {}
        for matricula in self.lista:
            if matricula.estudiante_id not in agrupadas:
                agrupadas[matricula.estudiante_id] = []
            agrupadas[matricula.estudiante_id].append(matricula)
        return agrupadas
