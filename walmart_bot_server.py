import socket, threading, time, json, argparse

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

MESSAGE_LENGTH = 1024

class WalmartStockBot:
    def __init__(self):
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--incognito")
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)

    def check_stock(self, sku):
        url = "https://www.walmart.ca/en/ip/" + sku
        self.driver.get(url)
        addToCartStock = '//div/div/button[@data-automation="cta-button"][text()="Add to cart"]'
        addToCartNoStock= '//div/div/button[@data-automation="cta-button"][text()="Out of stock"]'

        while(True):
            self.are_you_a_robot_check()
            self.driver.execute_script("window.scrollTo(0, 500)")
            stockExist = self.element_exist(addToCartStock)
            noStockExist = self.element_exist(addToCartNoStock)
            if stockExist:
                return True
            elif noStockExist:
                return False

    def element_exist(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath);
            return True
        except Exception:
            return False
        
    def are_you_a_robot_check(self):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, "#px-captcha")
            action = ActionChains(self.driver)
            action.move_to_element_with_offset(element, 10, 25).click_and_hold()
            action.perform()
            time.sleep(10)
            action.release(element)
            action.perform()
            time.sleep(0.2)
            action.release(element)
            return True
        except Exception:
            return False

    def kill(self):
        self.driver.close()

class StockServer:
    def __init__(self, args):
        self.args = args
        self.host = args.address
        self.port = args.port
        self.clients = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))

    def listen(self):
        self.s.listen(self.args.max_connection)
        threading.Thread(target = self.send_to_clients_loop, args = (self.clients, self.args.interval)).start()
        while True:
            client, address = self.s.accept()
            client.settimeout(self.args.timeout)
            skus = self.get_client_skus(client)
            self.clients.append((client, skus))
            print("New client just connected")

    def send_to_clients_loop(self, clients, interval):
        # IDK if this is thread safe
        clientsCopy = clients.copy()
        stockTable = {}
        bot = WalmartStockBot()
        for x in clientsCopy:
            for x in x[1]:
                if x not in stockTable:
                    stockTable[x] = bot.check_stock(x)
        
        bot.kill()
        for x in clientsCopy:
            clientData = {}
            for y in x[1]:
                clientData[y] = stockTable[y]

            jsonData = json.dumps(clientData)
            size = MESSAGE_LENGTH
            try:
                x[0].send(jsonData.encode())
            except:
                print("Lost connection with client")
                x[0].close()
                clients.remove(x)

        threading.Timer(interval, self.send_to_clients_loop, (clients, interval)).start()

    def get_client_skus(self, client):
        data = client.recv(MESSAGE_LENGTH)
        if not data:
            return []
        jsonData = data.decode()
        return json.loads(jsonData)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--interval', help='The stock update interval (sec)', required=True, type=int)
    parser.add_argument('-a','--address', help='The server ip address', required=True)
    parser.add_argument('-p','--port', help='The server port', required=True, type=int)
    parser.add_argument('-c','--max-connection', help='The maximum number of connections', required=False, default=5, type=int)
    parser.add_argument('-t','--timeout', help='Time until client timeout (sec)', required=False, default=60, type=int)

    args = parser.parse_args()

    server = StockServer(args)
    server.listen()