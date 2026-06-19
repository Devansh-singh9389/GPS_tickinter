import os
import gzip
import shutil
import requests
from requests.auth import HTTPBasicAuth
from core.config import DATA_DIR_BRDCS

class BRDCService:

    @staticmethod
    def clear_all_brdcs() -> int:
        """Deletes all BRDC ephemeris files from the data directory."""
        count = 0
        # Look for files starting with 'brdc' and containing 'n' (handles .24n and .24n.gz)
        for file_path in DATA_DIR_BRDCS.glob("brdc*.*n*"):
            try:
                file_path.unlink()  # Deletes the file
                count += 1
            except Exception:
                pass
        return count


    @staticmethod
    def download(username, password, date, on_prog, on_log, on_comp):
        try:
            year, doy, yy = date.strftime("%Y"), date.strftime("%j"), date.strftime("%y")
            gz_name = f"brdc{doy}0.{yy}n.gz"
            nav_name = f"brdc{doy}0.{yy}n"
            url = f"https://cddis.nasa.gov/archive/gnss/data/daily/{year}/{doy}/{yy}n/{gz_name}"
            
            gz_path = DATA_DIR_BRDCS / gz_name
            nav_path = DATA_DIR_BRDCS / nav_name
            
            on_log("info", f"Connecting to {url}")
            session = requests.Session()
            session.auth = HTTPBasicAuth(username, password)
            response = session.get(url, stream=True, timeout=30)
            
            if response.status_code != 200:
                return on_comp(False, f"HTTP Error {response.status_code}")
                
            total_bytes = int(response.headers.get("content-length", 0))
            downloaded = 0
            with open(gz_path, "wb") as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_bytes: on_prog(min(0.8, downloaded / total_bytes))
            
            on_log("info", "Decompressing...")
            with gzip.open(gz_path, "rb") as f_in, open(nav_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(gz_path)
            
            on_prog(1.0)
            on_comp(True, str(nav_path))
        except Exception as e:
            on_comp(False, str(e))