from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.config_generator import ConfigGenerator

app = FastAPI()

# Конфигурация
TEMPLATE_PATH = "/etc/openvpn/client-template.txt"
CONFIG_DIR = "/etc/openvpn/client-configs"
EASY_RSA_DIR = "/etc/openvpn/easy-rsa"
TLS_CRYPT_KEY = "/etc/openvpn/tls-crypt.key"

config_generator = ConfigGenerator(TEMPLATE_PATH, CONFIG_DIR, EASY_RSA_DIR, TLS_CRYPT_KEY)

class ClientRequest(BaseModel):
    client_name: str
    server_ip: str

@app.post("/generate-config")
def generate_config(request: ClientRequest):
    try:
        config_path = config_generator.generate_config(request.client_name, request.server_ip)
        return {"status": "success", "config_path": config_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete-config")
def delete_config(client_name: str):
    try:
        if config_generator.delete_config(client_name):
            return {"status": "success", "message": f"Config for {client_name} deleted."}
        else:
            raise HTTPException(status_code=404, detail="Config not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}