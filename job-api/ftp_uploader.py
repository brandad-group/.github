from ftplib import FTP_TLS
import os

class FTPUploader:
    user:str|None
    password:str|None
    server_address:str|None

    def __init__(self, server = None, user = None, password = None) -> None:
        self.user = user
        self.password = password
        self.server_address = server

        if not all([self.user, self.password, self.server_address]):
            raise ValueError('Check your .env variables!')

    def upload(self, file, target_filename = "jobs.csv", server = None)->bool:
        if server is None:
            server = self.server_address
        target_filename = os.path.basename(file)
        try:
            session = FTP_TLS(server,str(self.user),str(self.password))
            session.prot_p()
            with open(file,'rb') as binary_file:                  # file to send
                session.storbinary(f'STOR {target_filename}', binary_file)     # send the file
            session.quit()
            return True
        except Exception as e:
            print(f'FTP-ERROR: {e}')
            return False