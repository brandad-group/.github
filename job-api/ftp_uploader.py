from ftplib import FTP_TLS
import os

class FTPUploader:
    user:str = ""
    password:str = ""
    default_server_address:str = ""

    def __init__(self, user = None, password = None, server = None) -> None:
        self.user = user if user is not None else os.getenv("FTP_USER", "")
        self.password = password if password is not None else os.getenv("FTP_PASSWORD", "")
        self.server = server if server is None else os.getenv('FTP_SERVER', '')

    def upload(self, file, target_filename = "jobs.csv", server = None)->bool:
        if server is None:
            server = self.default_server_address
        target_filename = os.path.basename(file)
        try:
            session = FTP_TLS(server,self.user,self.password)
            session.prot_p()
            binary_file = open(file,'rb')                  # file to send
            session.storbinary(f'STOR {target_filename}', binary_file)     # send the file
            binary_file.close()                                    # close file and FTP
            session.quit()
            return True
        except Exception as e:
            print(e)
            return False