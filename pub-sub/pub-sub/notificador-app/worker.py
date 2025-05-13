import smtplib, ssl
from email.message import EmailMessage
from confluent_kafka import Consumer, KafkaException, KafkaError
import json


def send_email(corpo):
    message = EmailMessage()
    message.set_content(corpo)
    message['Subject'] = 'Notificação da Imagem'
    message['Destinatario'] = 'INSERIR EMAIL DE DESTINO'
    message['Remetente'] = 'INSERIR EMAIL DE ORIGEM'
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('INSERIR EMAIL DE DESTINO', 'INSERIR SENHA DE APP PARA O EMAIL')
        smtp.send_message(message)
        
consumer = Consumer({
    'bootstrap.servers': 'kafka1:19091,kafka2:19092,kafka3:19093',
    'group.id': 'notificador-group',
    'client.id': 'client-1',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
})
        
consumer.subscribe(['notificador'])
      
      
try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"Fim da partição: {msg.partition}")
                else:
                    raise KafkaException(msg.error())
            else:
                mensagem = msg.value().decode('utf-8')
                print(f"Mensagem recebida: {mensagem}")

                try:
                    data = json.loads(mensagem)
                    corpo = data.get('body', 'Nenhum corpo de mensagem encontrado.')

                    send_email(corpo)

                except Exception as e:
                    print(f"Erro ao processar a mensagem: {e}")
finally:
        consumer.close()
