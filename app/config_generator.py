import os
from pathlib import Path

class ConfigGenerator:
    def __init__(self, template_path, config_dir, easy_rsa_dir, tls_crypt_key):
        self.template_path = template_path
        self.config_dir = config_dir
        self.easy_rsa_dir = easy_rsa_dir
        self.tls_crypt_key = tls_crypt_key

    def generate_config(self, client_name, server_ip):
        self._generate_certificates(client_name)

        config_path = os.path.join(self.config_dir, f"{client_name}.ovpn")
        with open(self.template_path, "r") as template_file:
            config_content = template_file.read()

        config_content = config_content.replace("{SERVER_IP}", server_ip)

        with open(config_path, "w") as config_file:
            config_file.write(config_content)
            self._append_certificates(config_file, client_name)

        return config_path

    def _generate_certificates(self, client_name):
        os.chdir(self.easy_rsa_dir)
        os.system(f"./easyrsa build-client-full {client_name} nopass")

    def _append_certificates(self, config_file, client_name):
        with open(config_file, "a") as f:
            f.write("\n<ca>\n")
            f.write(Path(f"{self.easy_rsa_dir}/pki/ca.crt").read_text())
            f.write("</ca>\n")

            f.write("<cert>\n")
            f.write(Path(f"{self.easy_rsa_dir}/pki/issued/{client_name}.crt").read_text())
            f.write("</cert>\n")

            f.write("<key>\n")
            f.write(Path(f"{self.easy_rsa_dir}/pki/private/{client_name}.key").read_text())
            f.write("</key>\n")

            f.write("<tls-crypt>\n")
            f.write(Path(self.tls_crypt_key).read_text())
            f.write("</tls-crypt>\n")

    def delete_config(self, client_name):
        config_path = os.path.join(self.config_dir, f"{client_name}.ovpn")
        if os.path.exists(config_path):
            os.remove(config_path)
            os.system(f"cd {self.easy_rsa_dir} && ./easyrsa revoke {client_name} && ./easyrsa gen-crl")
            return True
        return False