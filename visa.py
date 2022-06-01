import bs4
import sys
import os
import time
import yagmail
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# Twilio configuration
toNumber = 'your_phonenumber'
fromNumber = 'twilio_phonenumber'
accountSid = 'ssid'
authToken = 'authtoken'
client = Client(accountSid, authToken)

firefox_profile = "firefox profile"
url = 'https://my.uscis.gov/appointmentscheduler-appointment/ca/en/office-search'
ircc_number = -1
os.environ['GH_TOKEN'] = 'GitHub Token'
zipcode = ""

# Yagmail config
yag = yagmail.SMTP('alert email', 'alert email password')
destination_emails = ['email1', 'email2']


def timeSleep(x, driver):
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write('{:2d} seconds'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    driver.refresh()
    sys.stdout.write('\r')
    sys.stdout.write('Page refreshed\n')
    sys.stdout.flush()


def createDriver():
    """Creating driver."""
    options = Options()
    options.headless = True  # Change To False if you want to see Firefox Browser Again.
    profile = webdriver.FirefoxProfile(firefox_profile)
    driver = webdriver.Firefox(profile, options=options, executable_path=GeckoDriverManager().install())
    return driver


def driverWait(driver, find_type, selector):
    """Driver Wait Settings."""
    while True:
        if find_type == 'css':
            try:
                driver.find_element_by_css_selector(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.2)
        elif find_type == 'name':
            try:
                driver.find_element_by_name(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.2)


def driver_input(web_driver, find_type, selector, text):
    """Driver Wait Settings."""
    while True:
        if find_type == 'css':
            try:
                web_driver.find_element_by_css_selector(selector).sendKeys(text)
                break
            except NoSuchElementException:
                web_driver.implicitly_wait(0.2)
        elif find_type == 'name':
            try:
                web_driver.find_element(by=By.NAME, value=selector).send_keys(text)
                break
            except NoSuchElementException:
                web_driver.implicitly_wait(0.2)


def finding_visa_spots(driver, alert_only=True):
    """Scanning all cards."""
    driver.get(url)
    while True:
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')
        wait = WebDriverWait(driver, 15)
        wait2 = WebDriverWait(driver, 2)
        try:
            zip_code_input = soup.find('input',
                                       {'class': 'uscis-input'})
            if zip_code_input:
                # Clicking Find Offices.
                driver.find_element(By.ID, "zip-input").send_keys(zipcode)
                driver.find_element(by=By.NAME, value="get-offices").click()

                # Checking if item is still in cart.
                try:
                    wait.until(
                        EC.presence_of_element_located((By.ID, "available-appts")))
                    driver.find_element(by=By.ID, value="available-appts").click()
                    print("Spotted Available Appointments.")
                except (NoSuchElementException, TimeoutException):
                    print("No available appointments. Retrying..")
                    timeSleep(3, driver)
                    # finding_visa_spots(driver
                    continue

                # Choose time slot.
                print("Attempting to Choose Time.")
                try:
                    wait.until(EC.presence_of_element_located(
                        (By.CLASS_NAME, "available-time-slot")))
                    if alert_only:
                        print("Alerts Only. Sending out alert emails")
                        available_date = driver.find_element(By.CLASS_NAME,
                                                             "active").text + " " + driver.find_element(By.CLASS_NAME,
                                                                                                        "month-name").text
                        available_times = driver.find_elements(By.CLASS_NAME, "available-time-slot")
                        available_times_str = ''
                        for t in available_times:
                            available_times_str += t.text
                            available_times_str += ", "
                        contents = [
                            "This is an automated alert that a visa appointment has opened up",
                            available_date, " ", available_times_str,
                        ]
                        for email in destination_emails:
                            yag.send(email, 'Canada Visa Appointment Has Opened Up', contents)
                        exit(0)
                    else:
                        driver.find_element(By.CLASS_NAME, "available-time-slot").click()
                        print("Choose first available time slot.")
                except (NoSuchElementException, TimeoutException):
                    print("Failed to choose time.")
                    pass

                # Trying IRCC Number
                try:
                    print("\nAttempting IRCC Number.\n")
                    ircc = driver.find_element(By.TAG_NAME, "input")
                    ircc.send_keys(ircc_number)
                    driver.find_element(By.ID, 'to-review').click()
                except (NoSuchElementException, TimeoutException):
                    print("IRCC Not Found")
                    pass

                # Confirm Appointment.
                try:
                    print("\nAttempting To Confirm Appointment.\n")
                    driver.find_element(By.ID, "schedule-appointment").click()
                except (NoSuchElementException, TimeoutException):
                    pass

                # Completed.
                print('Success!')
                for i in range(3):
                    print('\a')
                    time.sleep(1)
                time.sleep(1800)
                driver.quit()
                return
            else:
                pass

        except (NoSuchElementException, TimeoutException):
            pass
        timeSleep(5, driver)


if __name__ == '__main__':
    driver = createDriver()
    finding_visa_spots(driver, True)
