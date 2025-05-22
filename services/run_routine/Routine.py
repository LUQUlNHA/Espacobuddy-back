from datetime import datetime
import json

class Routine:
    """
    Classe responsável por representar uma rotina de alimentação para um alimentador automático.
    Aplica o princípio SRP (Single Responsibility Principle), pois seu único propósito é representar
    e manipular dados de uma rotina.
    """

    def __init__(self, id, routine_name, feeder_id, schedule_time, portion_size, user_id):
        """
        Construtor da classe Routine.
        
        Parâmetros:
        - id: Identificador único da rotina.
        - routine_name: Nome da rotina.
        - feeder_id: ID do alimentador associado.
        - schedule_time: Horário agendado para execução da rotina (objeto datetime).
        - portion_size: Quantidade de porção a ser servida (string, ex: '50g').
        - user_id: ID do usuário que criou a rotina.
        """
        self.id = id
        self.routine_name = routine_name
        self.feeder_id = feeder_id
        self.schedule_time = schedule_time
        self.portion_size = portion_size
        self.user_id = user_id

    def to_dict(self):
        """
        Converte os dados da rotina em um dicionário no formato esperado para transmissão
        (por exemplo, via MQTT). Inclui a data/hora atual no campo 'executed_at'.
        
        Retorna:
        - dict com os dados formatados da rotina.
        
        Princípio aplicado:
        - SRP: Função dedicada apenas à serialização da instância.
        - OCP: Pode ser estendida para incluir novos campos sem modificar o método base.
        """
        now = datetime.now()  # Captura o momento atual da execução
        return {
            "device_id": self.feeder_id,
            "executed_at": now.strftime("%Y-%m-%dT%H:%M"),
            "routine_name": self.routine_name,
            "portion": self.portion_size,
            "schedule_time": self.schedule_time.strftime("%H:%M")
        }

    def already_exists(self, some_list) -> bool:
        """
        Verifica se esta rotina já existe em uma lista fornecida, com base no ID.

        Parâmetros:
        - some_list: Lista de objetos Routine.

        Retorna:
        - True se uma rotina com o mesmo ID for encontrada; False caso contrário.

        Princípio aplicado:
        - SRP: Método focado exclusivamente em verificação de duplicidade.
        """
        for item in some_list:
            if item.id == self.id:
                return True
        return False
