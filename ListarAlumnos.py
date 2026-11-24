import json
import os

import boto3
import pymysql

def lambda_handler(event, context):
    connection = None

    try:
        # Recuperar las credenciales desde Secrets Manager.
        sm = boto3.client('secretsmanager')
        response = sm.get_secret_value(SecretId=os.environ['DB_SECRET_ID'])
        secret = json.loads(response['SecretString'])

        # Conexion directa dentro del handler, sin funcion auxiliar.
        connection = pymysql.connect(
            host=secret['host'],
            port=int(secret.get('port', 3306)),
            user=secret['username'],
            password=secret['password'],
            database=secret['dbname'],
            connect_timeout=5,
        )

        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM alumnos;')
            results = cursor.fetchall()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(results, default=str, ensure_ascii=False),
        }

    except Exception as error:
        # Registrar solo el tipo de error, sin contrasenas ni mensajes SQL.
        print('Error al listar alumnos:', type(error).__name__)

        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'No se pudo consultar alumnos'}),
        }

    finally:
        if connection is not None:
            connection.close()
