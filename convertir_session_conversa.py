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
        print(f"❌ Error llegint {ruta_entrada}: {e}")
        return

    # 1. Post Original (Notícia)
    session_data = sessio.get("session", {})
    exp_config = session_data.get("experimental_config", {})
    seed_data = exp_config.get("seed", {})
    
    started_at_str = session_data.get("started_at", "")
    post_timestamp = datetime.fromisoformat(started_at_str.replace("Z", "+00:00")).timestamp() if started_at_str else 0

    post_original = {
        "agency": seed_data.get("source", "SISTEMA"),
        "title": seed_data.get("headline", "Sense títol"),
        "body": seed_data.get("body", ""),
        "author": session_data.get("user_name", "Alex"),
        "timestamp": post_timestamp
    }

    # 2. Processar Missatges
    missatges_raw = sessio.get("messages", [])
    if not missatges_raw:
        events = sessio.get("events", [])
        missatges_raw = [e["data"] for e in events if e.get("event_type") == "message"]
    
    nous_missatges = []
    last_msg_data = None  

    for m in missatges_raw:
        content_raw = m.get("content", "")
        reply_to_user = None
        reply_text = None
        is_mention = False

        # --- LÒGICA DE MENCIÓ (@NOM) ---
        match = re.match(r"^@([\w\u00C0-\u017F]+)[,:\s]*(.*)", content_raw, re.IGNORECASE)
        
        if match:
            target_name = match.group(1)
            content_net = match.group(2)
            is_mention = True
            
            found_parent = next((p for p in reversed(nous_missatges) if p["sender"].lower() == target_name.lower()), None)
            if found_parent:
                reply_to_user = found_parent["sender"]
                reply_text = found_parent["text"]
            else:
                reply_to_user = target_name
                reply_text = "..."
        else:
            content_net = content_raw
            if last_msg_data:
                reply_to_user = last_msg_data["sender"]
                reply_text = last_msg_data["content"]

        nous_missatges.append({
            "id": m.get("message_id"),
            "sender": m.get("sender"),
            "text": content_net.strip(),
            "timestamp": datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")).timestamp() if m.get("timestamp") else 0,
            "reply_to": reply_to_user,
            "reply_text": reply_text,
            "is_mention": is_mention,
            "likes": m.get("likes_count", 0)
        })
        last_msg_data = m

    resultat = {
        "post_original": post_original,
        "num_participants": len(set(m["sender"] for m in missatges_raw)),
        "messages": nous_missatges
    }

    with open(ruta_sortida, 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    fitxers = glob.glob('sessio*.json')
    for f_in in fitxers:
        # Extraiem el número: sessio1.json -> 1
        n = os.path.basename(f_in).replace('sessio', '').replace('.json', '')
        f_out = f'conversa_neta_plataforma{n}.json'
        convertir_sessio_a_conversa_neta(f_in, f_out)
        print(f"✅ Convertit: {f_in} -> {f_out}")