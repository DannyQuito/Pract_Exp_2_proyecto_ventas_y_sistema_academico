from datetime import date


# =====================================================================
# CLASE BASE: lo que los tres modelos comparten
# =====================================================================
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento común."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    # ---- ÚNICO MÉTODO DE CLASE DEL PROYECTO ----
    @classmethod
    def desde_diccionario(cls, datos):
        """Diccionario -> objeto. Escrito UNA vez y usado por los tres modelos.
        cls es la clase que llamó: Estudiante, Materia o Matricula."""
        datos = dict(datos)                 # copia, para no tocar el original
        id_registro = datos.pop("id")       # saco el id
        return cls(id_registro, **datos)    # el resto son los campos del modelo

    # ---- MÉTODOS DE INSTANCIA ----
    def a_diccionario(self):
        # Objeto -> diccionario. Cada hijo agrega sus campos.
        return {"id": self.id}

    def etiqueta(self):
        # POLIMORFISMO: cada hijo la reescribe a su manera
        return f"registro {self.id}"

    def __str__(self):
        # Lo que se ve al hacer print(objeto). Llama a etiqueta(),
        # así que cada modelo se imprime distinto sin cambiar esta línea.
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona es la base de Estudiante (y mañana, de Profesor)
# =====================================================================
class Persona(ModeloBase):
    """Todo lo que tiene una persona del sistema."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)      # el padre guarda el id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()    # {"id": ...} que arma el padre
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona, con teléfono y carrera."""

    def __init__(self, id_registro, nombre, apellido, email, telefono="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.telefono = telefono
        self.carrera = carrera

    def a_diccionario(self):
        datos = super().a_diccionario()    # reutiliza lo de Persona
        datos["telefono"] = self.telefono
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        # Sobrescribe y EXTIENDE la del padre
        return f"{super().etiqueta()} · {self.email} · {self.carrera or 'sin carrera'}"


# =====================================================================
# ÚNICA CLASE CON ATRIBUTOS Y MÉTODOS ESTÁTICOS
# =====================================================================
class Materia(ModeloBase):
    """Materia ES UN ModeloBase. Aquí viven los ejemplos de lo estático."""

    # ATRIBUTOS ESTÁTICOS (de clase): existen una sola vez, no por objeto
    CUPO_MINIMO = 5           # con 5 cupos o menos se avisa "cupo bajo"
    NOTA_MAXIMA = 10          # escala de 0 a 10
    NOTA_APROBACION = 7       # nota mínima para aprobar
    MAX_CREDITOS = 10
    total_creadas = 0         # contador compartido

    def __init__(self, id_registro, nombre, creditos, cupo=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.creditos = int(creditos)
        self.cupo = int(cupo)              # cupos DISPONIBLES
        Materia.total_creadas += 1         # se modifica en la CLASE, no en self

    # MÉTODOS ESTÁTICOS: reglas que no necesitan ninguna materia concreta
    @staticmethod
    def es_creditos_valido(valor):
        try:
            return 1 <= int(valor) <= Materia.MAX_CREDITOS
        except (TypeError, ValueError):
            return False

    @staticmethod
    def es_nota_valida(valor):
        try:
            return 0 <= float(valor) <= Materia.NOTA_MAXIMA
        except (TypeError, ValueError):
            return False

    @staticmethod
    def esta_aprobada(nota):
        return nota >= Materia.NOTA_APROBACION

    # MÉTODOS DE INSTANCIA: necesitan los datos de ESTA materia
    def cupo_bajo(self):
        return self.cupo <= Materia.CUPO_MINIMO

    def hay_cupo(self):
        return self.cupo > 0

    def ocupar_cupo(self):
        self.cupo -= 1

    def liberar_cupo(self):
        self.cupo += 1

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["creditos"] = self.creditos
        datos["cupo"] = self.cupo
        return datos

    def etiqueta(self):
        alerta = " ⚠ cupo bajo" if self.cupo_bajo() else ""
        return f"{self.nombre} · {self.creditos} créditos · cupo {self.cupo}{alerta}"


# =====================================================================
class Matricula(ModeloBase):
    """Matrícula: un estudiante inscrito en una materia, con su nota."""

    def __init__(self, id_registro, estudiante_id, materia_id, fecha="", nota=None):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.fecha = fecha or date.today().isoformat()
        # None = todavía sin calificar
        self.nota = None if nota is None else float(nota)

    def calificar(self, nota):
        self.nota = float(nota)

    def estado(self):
        # Se calcula cada vez; NO se guarda, para que nunca quede desactualizado
        if self.nota is None:
            return "En curso"
        return "Aprobada" if Materia.esta_aprobada(self.nota) else "Reprobada"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["fecha"] = self.fecha
        datos["nota"] = self.nota
        return datos

    def etiqueta(self):
        nota = "sin nota" if self.nota is None else f"{self.nota:.2f}"
        return (f"{self.fecha} · estudiante {self.estudiante_id} · "
                f"materia {self.materia_id} · {nota} ({self.estado()})")
