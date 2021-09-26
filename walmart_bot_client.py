import time, json, socket, argparse, smtplib

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

MESSAGE_LENGTH = 1024

class StockClient:
    def __init__(self, address, skus):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(address)
        jsonStock = json.dumps(skus)
        size = MESSAGE_LENGTH
        self.s.send(jsonStock.encode())
        print("Now connected to server at '" + address[0] + ":" + str(address[1]) + "'")

    def get_stock(self):
        data = self.s.recv(MESSAGE_LENGTH)
        if not data:
            return None
        jsonData = data.decode()
        return json.loads(jsonData)

class Customer:
    def __init__(self, file_name):
        with open(file_name, encoding='utf-8') as f:
            data = json.load(f)

            shippingInfo = data['shipping']
            self.firstName = shippingInfo['firstName']
            self.lastName = shippingInfo['lastName']
            self.address = shippingInfo['address']
            self.city = shippingInfo['city']
            self.province = shippingInfo['province']
            self.postalCode = shippingInfo['postalCode']
            self.phone = shippingInfo['phone']
            self.email = shippingInfo['email']

            billingInfo = data['billing']
            self.cardNumber = billingInfo['cardNumber']
            self.expirationMonth = billingInfo['expirationMonth']
            self.expirationYear = billingInfo['expirationYear']
            self.securityCode = billingInfo['securityCode']

class WalmartOrderBot:
    
    def __init__(self, sku, customer):
        url = "https://www.walmart.ca/en/ip/" + sku

        self.customer = customer

        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--incognito")
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(url)

    def click_button(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath).click()
            return True
        except Exception:
            return False

    def select_option(self, select, value):
        try:
            select = Select(self.driver.find_element(By.XPATH, select))
            select.select_by_value(value)
            return True
        except Exception:
            return False

    def fill_input(self, input, value):
        try:
            element = self.driver.find_element(By.XPATH, input)
            element.clear()
            element.send_keys(value)
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

    def add_to_cart_and_checkout(self):
        addToCart = '//div/div/button[@data-automation="cta-button"]'
        ageConfirm = '//*[@data-automation="age-modal-confirm-confirmBtn"]'
        checkOut = '//*[@data-automation="checkout"]'
        checkOutConfirm = '//*[@data-automation="checkout-btn"]'
        continueWithoutAccount = ('//*[@data-automation="checkout-as-guest-button"]')

        done = False
        while(not done):
            self.driver.execute_script("window.scrollTo(0, 500)") 
            found = self.click_button(addToCart)
            found |= self.click_button(ageConfirm)
            found |= self.click_button(checkOut)
            found |= self.click_button(checkOutConfirm)
            done = self.click_button(continueWithoutAccount)
            if not found and not done:
                self.are_you_a_robot_check()

    def fill_shipping_info(self):
        shippingButton = '//*[@data-automation="shipping-tab-tab"]'

        firstName ='//*[@data-automation="first-name"]'
        lastName = '//*[@data-automation="last-name"]'
        address = '//*[@data-automation="address1"]'
        city = '//*[@data-automation="city"]'
        province = '//*[@data-automation="province"]'
        postalCode = '//*[@data-automation="postal-code"]'
        phone = '//*[@data-automation="phone-number"]'
        email = '//*[@data-automation="email"]'

        confirmInfo = '//*[@data-automation="btn-save"]'
        confirmInfo2 = '//*[@data-automation="next-button"]'

        done = False
        while(not done):
            self.are_you_a_robot_check()
            done = self.click_button(shippingButton)
        
        done = False
        while(not done):
            self.are_you_a_robot_check()
            done = self.fill_input(firstName, self.customer.firstName)
            done &= self.fill_input(lastName, self.customer.lastName)
            done &= self.fill_input(address, self.customer.address)
            done &= self.fill_input(city, self.customer.city)
            done &= self.select_option(province, self.customer.province)
            done &= self.fill_input(postalCode, self.customer.postalCode)
            done &= self.fill_input(phone, self.customer.phone)
            done &= self.fill_input(email, self.customer.email)

        done = False
        while(not done):
            self.are_you_a_robot_check()
            done = self.click_button(confirmInfo)

        done = False
        while(not done):
            self.are_you_a_robot_check()
            done = self.click_button(confirmInfo2)

    def fill_out_payment(self):
        newCard = '//*[@data-automation="payment-nocc-add-card"]'
        cardNumber = '//*[@id="cardNumber"]'
        expirationMonth = '//*[@id="expiryMonth"]'
        expirationYear = '//*[@id="expiryYear"]'
        securityCode = '//*[@id="securityCode"]'
        applyCard = '//*[@data-automation="apply-button"]'

        done = False
        while(not done):
            self.are_you_a_robot_check()
            done = self.click_button(newCard)

        done = False
        while(not done):
            self.are_you_a_robot_check()
            done = self.fill_input(cardNumber, self.customer.cardNumber)
            done &= self.fill_input(expirationMonth, self.customer.expirationMonth)
            done &= self.fill_input(expirationYear, self.customer.expirationYear)
            done &= self.fill_input(securityCode, self.customer.securityCode)

        done = False
        while(not done):
            self.are_you_a_robot_check()
            done = self.click_button(applyCard)

    def order(self):
        order = '//*[@data-automation="place-order-button"]'

        done = False
        while(not done):
            self.are_you_a_robot_check()
            done = self.click_button(order)

        # What happens next i dont know, never tried
        time.sleep(10)
        self.are_you_a_robot_check()

    def kill(self):
        self.driver.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a','--address', help='The server ip address', required=True)
    parser.add_argument('-p','--port', help='The server port', required=True, type=int)
    parser.add_argument('-s','--skus', help='The walmart skus to watch',  nargs='+', required=True)
    args = parser.parse_args()

    customer = Customer("customer.json")

    boughtItems = []
    client = StockClient((args.address, args.port), args.skus)
    while len(boughtItems) is not len(args.skus):
        stock = client.get_stock()
        for sku in stock:
            if stock[sku] is True and sku not in boughtItems:
                print("Item '" + sku + "' available, proceeding to checkout")
                bot = WalmartOrderBot(sku, customer)
                bot.add_to_cart_and_checkout()
                bot.fill_shipping_info()
                bot.fill_out_payment()
                bot.order()
                bot.kill()
                boughtItems.append(sku)
                print("Client successfully bought item " + "https://www.walmart.ca/en/ip/" + sku)

    print("Successfully bought all items, client will now terminate")