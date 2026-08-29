import os
import time
import glob
import urllib.request
import json

LOG_DIR = os.environ.get("LOG_DIR", "/var/log/app-logs")
SOVEREIGN_API_URL = os.environ.get("SOVEREIGN_API_URL", "https://a3pme2hx4v.us-east-1.awsapprunner.com")
SOVEREIGN_API_KEY = os.environ.get("SOVEREIGN_API_KEY", "sov_prod_key_999")
POLL_INTERVAL_SEC = int(os.environ.get("POLL_INTERVAL_SEC", "10"))

def compress_file(file_path):
    try:
        boundary = '----SovereignK8sSidecar'
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
            
        if len(file_bytes) == 0:
            return
            
        data = []
        data.append(f'--{boundary}\r\nContent-Disposition: form-data; name="api_key"\r\n\r\n{SOVEREIGN_API_KEY}\r\n'.encode('utf-8'))
        data.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode('utf-8'))
        data.append(file_bytes)
        data.append(f'\r\n--{boundary}--\r\n'.encode('utf-8'))
        payload = b''.join(data)

        req = urllib.request.Request(
            f"{SOVEREIGN_API_URL}/v1/compress",
            data=payload,
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(payload))
            }
        )

        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            
        if res_data.get('status') == 'success':
            download_url = f"{SOVEREIGN_API_URL}{res_data['download_url']}"
            out_compressed_path = f"{file_path}.sov"
            urllib.request.urlretrieve(download_url, out_compressed_path)
            orig_size = len(file_bytes)
            new_size = os.path.getsize(out_compressed_path)
            savings = int((1 - (new_size / orig_size)) * 100)
            print(f"[K8s Sidecar] Compressed {os.path.basename(file_path)}: {orig_size}B -> {new_size}B ({savings}% reduction).")
            # Rotate original log
            os.remove(file_path)
    except Exception as e:
        print(f"[K8s Sidecar Error] Failed to compress {file_path}: {e}")

def main():
    print(f"[K8s Sidecar] Sovereign Log Compression Agent watching {LOG_DIR}...")
    while True:
        log_files = glob.glob(f"{LOG_DIR}/*.log")
        for log_file in log_files:
            compress_file(log_file)
        time.sleep(POLL_INTERVAL_SEC)

if __name__ == "__main__":
    main()
