import sys
import os.path
import uuid
from glob import glob
from datetime import datetime

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {}
        self.types['.pdf'] = 'application/pdf'
        self.types['.jpg'] = 'image/jpeg'
        self.types['.txt'] = 'text/plain'
        self.types['.html'] = 'text/html'

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n".format(kode, message))
        resp.append("Date: {}\r\n".format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n".format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n".format(kk, headers[kk]))
        resp.append("\r\n")

        response_headers = ''
        for i in resp:
            response_headers = "{}{}".format(response_headers, i)
        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def proses(self, data):
        requests = data.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n != '']

        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            if method == 'GET':
                object_address = j[1].strip()
                return self.http_get(object_address, all_headers)
            if method == 'POST':
                object_address = j[1].strip()
                return self.http_post(object_address, all_headers)
            if method == 'DELETE':
                object_address = j[1].strip()
                return self.http_delete(object_address, all_headers)
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})

    # Daftar file dalam direktori
    def http_list(self, object_address, headers):
        files = glob('./*')
        file_list = "\n".join(files)
        return self.response(200, 'OK', file_list, {'Content-type': 'text/plain'})

    # Mengunggah file
    def http_upload(self, object_address, headers):
        # Mendapatkan panjang konten dari header
        content_length = int(headers.get('Content-Length', 0))
        
        # Membaca data file biner yang dikirimkan
        body = self.rfile.read(content_length)
        filename = object_address.strip('/')
    
        # Menyimpan file yang diterima
        try:
            with open(filename, 'wb') as f:
                f.write(body)
            return self.response(200, 'OK', 'File uploaded successfully', {'Content-type': 'text/plain'})
        except Exception as e:
            return self.response(500, 'Internal Server Error', str(e), {'Content-type': 'text/plain'})


    # Menghapus file
    def http_delete(self, object_address, headers):
        filename = object_address.strip('/')
        try:
            os.remove(filename)
            return self.response(200, 'OK', 'File deleted successfully', {'Content-type': 'text/plain'})
        except FileNotFoundError:
            return self.response(404, 'Not Found', 'File not found', {'Content-type': 'text/plain'})

    # HTTP GET
    def http_get(self, object_address, headers):
        files = glob('./*')
        thedir = './'
        if object_address == '/':
            return self.http_list(object_address, headers)  # Menampilkan daftar file

        if object_address == '/video':
            return self.response(302, 'Found', '', dict(location='https://youtu.be/katoxpnTf04'))
        if object_address == '/santai':
            return self.response(200, 'OK', 'santai saja', dict())

        object_address = object_address[1:]
        if thedir + object_address not in files:
            return self.response(404, 'Not Found', '', {})
        fp = open(thedir + object_address, 'rb')
        isi = fp.read()

        fext = os.path.splitext(thedir + object_address)[1]
        content_type = self.types.get(fext, 'application/octet-stream')

        headers = {}
        headers['Content-type'] = content_type

        return self.response(200, 'OK', isi, headers)

    def http_post(self, object_address, headers):
        headers = {}
        isi = "kosong"
        return self.response(200, 'OK', isi, headers)

# Uji coba server, mengirimkan request
if __name__ == "__main__":
    httpserver = HttpServer()

    # Testing HTTP GET untuk file yang ada
    d = httpserver.proses('GET testing.txt HTTP/1.0')
    print(d)
    
    # Testing HTTP GET untuk file yang ada
    d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
    print(d)
    
    # Testing HTTP GET untuk root (mendapatkan daftar file)
    d = httpserver.proses('GET / HTTP/1.0')
    print(d)
    
    # Testing HTTP DELETE untuk file yang ada
    d = httpserver.proses('DELETE testing.txt HTTP/1.0')
    print(d)
    
    # Testing HTTP POST untuk mengunggah file
    d = httpserver.proses('POST testfile.txt HTTP/1.0')
    print(d)
