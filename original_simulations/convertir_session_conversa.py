import json
import re
import glob
import os
from datetime import datetime

def convertir_sessio_a_conversa_neta(ruta_entrada, ruta_sortida):
    try:
        with open(ruta_entrada, 'r', encoding='utf-8') as f:
            sessio = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo {ruta_entrada}: {e}")
        return

    # 1. Datos del Post Original
    session_data = sessio.get("session", {})
    exp_config = session_data.get("experimental_config", {})
    seed_data = exp_config.get("seed", {})
    
    started_at_str = session_data.get("started_at", "")
    post_timestamp = datetime.fromisoformat(started_at_str.replace("Z", "+00:00")).timestamp() if started_at_str else 0

    post_original = {
        "agency": seed_data.get("source", "SISTEMA"),
        "title": seed_data.get("headline", "Sin título"),
        "body": seed_data.get("body", ""),
        "author": session_data.get("user_name", "Alex"),
        "timestamp": post_timestamp
    }

    # 2. Procesar Mensajes
    missatges_raw = sessio.get("messages", [])
    if not missatges_raw:
        events = sessio.get("events", [])
        missatges_raw = [e["data"] for e in events if e.get("event_type") == "message"]
    
    nous_missatges = []
    mensajes_por_id = {} # Diccionario para buscar por ID de mensaje
    last_msg_data = None  

    for m in missatges_raw:
        msg_id = m.get("message_id")
        content_raw = m.get("content", "")
        reply_id = m.get("reply_to")        # El ID al que responde (ej: "9bdf...")
        quoted_text = m.get("quoted_text")   # El texto citado
        
        reply_to_user = None
        reply_text = quoted_text
        is_mention = False

        # --- LÓGICA DE DETECCIÓN DE CITA (RECUADRO) ---
        
        # 1. Si el JSON original ya tiene un reply_to (ID) o quoted_text, ES una mención/cita
        if reply_id or quoted_text:
            is_mention = True
            # Intentamos buscar el autor original por el ID
            if reply_id in mensajes_por_id:
                parent = mensajes_por_id[reply_id]
                reply_to_user = parent["sender"]
                if not reply_text:
                    reply_text = parent["text"]
        
        # 2. Si no lo tiene, comprobamos si hay un @Nombre manual en el texto
        match = re.match(r"^@([\w\u00C0-\u017F]+)[,:\s]*(.*)", content_raw, re.IGNORECASE)
        if match:
            target_name = match.group(1)
            content_net = match.group(2)
            is_mention = True
            
            # Si no hemos encontrado el autor por ID, lo buscamos por nombre
            if not reply_to_user:
                found_parent = next((p for p in reversed(nous_missatges) if p["sender"].lower() == target_name.lower()), None)
                if found_parent:
                    reply_to_user = found_parent["sender"]
                    if not reply_text: reply_text = found_parent["text"]
                else:
                    reply_to_user = target_name
        else:
            content_net = content_raw

        # 3. Si no es mención (is_mention sigue siendo False), es una respuesta lineal
        # Mantenemos los datos de reply_to para la lógica interna de la web, pero sin activar el recuadro
        if not is_mention and last_msg_data:
            reply_to_user = last_msg_data["sender"]
            reply_text = last_msg_data["text"]

        # Creamos el objeto procesado
        obj_msg = {
            "id": msg_id,
            "sender": m.get("sender"),
            "text": content_net.strip(),
            "timestamp": datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")).timestamp() if m.get("timestamp") else 0,
            "reply_to": reply_to_user,
            "reply_text": reply_text,
            "is_mention": is_mention, # <--- AQUÍ está la clave
            "likes": m.get("likes_count", 0)
        }
        
        nous_missatges.append(obj_msg)
        mensajes_por_id[msg_id] = obj_msg # Guardamos para futuras referencias
        last_msg_data = obj_msg

    # 3. Guardar el JSON final
    conversa_neta = {
        "post_original": post_original,
        "num_participants": len(set(m["sender"] for m in missatges_raw)),
        "messages": nous_missatges
    }

    with open(ruta_sortida, 'w', encoding='utf-8') as f:
        json.dump(conversa_neta, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    fitxers = glob.glob('sessio8.json')
    for f_in in fitxers:
        n = os.path.basename(f_in).replace('sessio', '').replace('.json', '')
        f_out = f'conversa_neta_plataforma{n}.json'
        convertir_sessio_a_conversa_neta(f_in, f_out)
        print(f"✅ Procesado: {f_in} -> {f_out}")