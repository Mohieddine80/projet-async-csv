import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
import requests
import os
import time
import csv

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# IP FIXE (Plus de DNS !)
CSHARP_API_URL = 'http://172.20.0.3:5001'

processing_status = {
    'is_processing': False,
    'total_lines': 0,
    'processed_lines': 0,
    'inserted_lines': 0,
    'skipped_lines': 0,
    'percentage': 0
}

def process_csv_async(file_path):
    """Traite le fichier CSV de manière asynchrone et intelligente"""
    global processing_status
    print(f"DEBUG: Début traitement {file_path}", flush=True)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines: raise Exception("Fichier vide")

        # --- AUTO-DÉTECTION INTELLIGENTE ---
        header_line = lines[0].strip()
        # On regarde qui gagne entre ; et ,
        if header_line.count(';') > header_line.count(','):
            sep_header = ';'
        else:
            sep_header = ','
            
        headers = header_line.replace('"', '').split(sep_header)
        print(f"DEBUG: Séparateur détecté: '{sep_header}' - {len(headers)} colonnes.", flush=True)
        # -----------------------------------

        # Nettoyage et Parsing
        data_rows = []
        for i, line in enumerate(lines[1:]):
            clean_line = line.strip().rstrip(';') # On vire les ; de fin inutiles
            if not clean_line: continue
            
            # On tente de lire avec virgule (standard)
            # Si ça ne marche pas bien (trop peu de colonnes), on tentera autre chose si besoin
            reader = csv.reader([clean_line], delimiter=',') 
            row = next(reader)
            
            # Si le fichier est hybride (Header ; et Data ,) on gère, sinon on garde la logique standard
            # Ici on s'assure d'avoir le bon nombre de colonnes
            if len(row) < len(headers):
                # Peut-être que les données sont aussi séparées par des ; ?
                reader_retry = csv.reader([clean_line], delimiter=';')
                row_retry = next(reader_retry)
                if len(row_retry) >= len(headers):
                    row = row_retry
            
            # Alignement final
            if len(row) > len(headers):
                row = row[:len(headers)]
            elif len(row) < len(headers):
                row += [None] * (len(headers) - len(row))
                
            data_rows.append(row)

        df = pd.DataFrame(data_rows, columns=headers)
        
        # Nettoyage des données
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.where(pd.notnull(df), None)

        total_lines = len(df)
        print(f"DEBUG: {total_lines} lignes chargées.", flush=True)
        
        # Mise à jour status
        processing_status['total_lines'] = total_lines
        processing_status['is_processing'] = True
        processing_status['processed_lines'] = 0
        processing_status['inserted_lines'] = 0
        processing_status['skipped_lines'] = 0
        socketio.emit('progress', processing_status)
        
        # Envoi API
        for i, (index, row) in enumerate(df.iterrows()):
            try:
                data = row.to_dict()
                
                # Retry simple
                success = False
                for _ in range(3):
                    try:
                        # Utilisation de l'IP FIXE définie en haut du fichier
                        response = requests.post(f"{CSHARP_API_URL}/api/data/insert", json=data, timeout=5)
                        if response.status_code == 200:
                            if response.json().get('inserted') is True:
                                processing_status['inserted_lines'] += 1
                            else:
                                processing_status['skipped_lines'] += 1
                            success = True
                            break
                    except:
                        time.sleep(0.1)

                if not success: processing_status['skipped_lines'] += 1
                
                processing_status['processed_lines'] += 1
                processing_status['percentage'] = round((processing_status['processed_lines'] / total_lines) * 100, 2)
                
                if processing_status['processed_lines'] % 50 == 0: # Moins de spam socket
                    socketio.emit('progress', processing_status)
                    socketio.sleep(0)

            except Exception:
                processing_status['skipped_lines'] += 1

        processing_status['is_processing'] = False
        socketio.emit('progress', processing_status)
        socketio.emit('complete', {'message': 'Fini'})
        
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as e:
        print(f"ERREUR: {e}", flush=True)
        processing_status['is_processing'] = False
        socketio.emit('error', {'message': str(e)})

@app.route('/')
def index():
    return "Flask Running"

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    
    if processing_status['is_processing']:
        return jsonify({'error': 'Occupé'}), 409
    
    try:
        upload_folder = '/tmp'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        
        socketio.start_background_task(target=process_csv_async, file_path=file_path)
        return jsonify({'message': 'Démarré'}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(processing_status)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)