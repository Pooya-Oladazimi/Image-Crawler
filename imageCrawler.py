class Crawler:
    def __init__(self, socket, target, ssl, limit):
        self.socket = socket
        self.ssl = ssl
        self.context = context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.url = target
        self.http_prefix = b"GET /"
        self.http_postfix = b" HTTP/1.1\r\nHost:"
        self.output_image = "images/img"
        self.image_type = [".png", ".jpg"]
        self.port = [80, 443]
        self.domain_name = self.get_domain_name(self.url)
        self.path_name = self.get_domain_path(self.url, self.domain_name)
        self.request = ""
        self.image_urls = []
        self.limit = limit

    def clean_url(self, url):
        if "https" not in url and "http" not in url:
            return "http://" + url
        return url

    def get_image_type(self, url):
        if ".png" in url:
            return self.image_type[0]
        elif ".jpg" in url:
            return self.image_type[1]
        return False

    def get_domain_name(self, url):
        temp = url.split('://')
        domain = ""
        if len(temp) > 1:
            domain = temp[1].split('/')
        else:
            domain = temp[0].split('/')

        return domain[0].split('?')[0]

    def get_domain_path(self, url, domain):
        path = ""
        if "http://" in url:
             path = url.split("http://")[1].split(domain + "/", 1)
        elif "https://" in url:
             path = url.split("https://")[1].split(domain + "/", 1)

        if len(path) > 1 and path[1] != '':
            return path[1]
        return ""

    def check_protocol(self, url):
        if "https" in url:
            return "https"
        elif "http" in url:
            return "http"
        else:
            return False

    def file_to_string(self, file_name):
        file = open(file_name, "r")
        string = ""
        for item in file:
            string += item
        file.close()
        return string

    def separate_content(self, output):
        try:
            content = open(output, "wb")
            Input_file = open("temp/Temp.html", "rb")
            flag = 0
            for line in Input_file:
                if line.isspace() and flag == 0:
                    flag = 1

                elif flag == 1:
                    content.write(line)
                    content.flush()

            content.close()
            Input_file.close()

        except Exception as ex:
            print("header_seperator : ", ex)

    def get_image_urls(self):
        result = []
        content = self.file_to_string("temp/content.html")
        temp = content.split("<img")
        for img in temp[1:]:
            if "src='" in img:
                link = img.split('>')[0]
                link = link.split("src='")
                link = link[len(link) - 1]
                link = link.split("'")[0]
                result.append(link)
            elif 'src="' in img:
                link = img.split('>')[0]
                link = link.split('src="')
                link = link[len(link) - 1]
                link = link.split('"')[0]
                result.append(link)

        for url in result:
            if self.check_protocol(url):
                self.image_urls.append(url)
            elif self.domain_name in url:
                temp = url.split(self.domain_name, 1)
                self.image_urls.append(self.clean_url(self.domain_name + temp[1]))


    def send_request(self, domain, path, protocol):
        socket = ""
        port = 0
        if protocol == "http":
            socket = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
            port = self.port[0]
        else:
            socket = self.context.wrap_socket(self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM), server_hostname=domain)
            port = self.port[1]

        try:
            socket.connect((domain, port))
        except Exception as ex:
            print("cannot connect to the domain!")
            print(ex)

        if path == "":
            self.request = self.http_prefix + self.http_postfix + domain.encode() + b"\r\n\r\n"
        elif path != "":
            self.request = self.http_prefix + path.encode() + b" HTTP/1.1\r\nHost:" + domain.encode() + b"\r\n\r\n"

        try:
            socket.sendall(self.request)
        except Exception as ex:
            print("cannot send a request to the domain!")
            print(ex)

        try:
            answer = socket.recv(8196)
            answer_file = open("temp/Temp.html", "wb")
            while answer:
                answer_file.write(answer)
                answer_file.flush()
                answer = socket.recv(8196)
            answer_file.flush()
            answer_file.close()
            socket.close()

        except Exception as ex:
            print("cannot get answer from the domain!")
            print(ex)

    def download_images(self):
        Id = 1
        for link in self.image_urls:
            if Id > self.limit:
                break
            image_type = self.get_image_type(link)
            if not image_type:
                continue
            image_name = self.output_image + str(Id) + image_type
            domain = self.get_domain_name(link)
            path = self.get_domain_path(link, domain)
            self.send_request(domain, path, self.check_protocol(link))
            self.separate_content(image_name)
            Id += 1

    def main(self):
        protocol = self.check_protocol(self.url)
        if not protocol:
            raise Exception("the target Protocol could not be detected. It should be http or https.")

        self.send_request(self.domain_name, self.path_name, protocol)
        self.separate_content("temp/content.html")
        self.get_image_urls()
        self.download_images()
        return True

