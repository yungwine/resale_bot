from selenium import webdriver
import time
from cfg import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def buy_product():

    new_window = driver.window_handles[1]
    driver.close()
    driver.switch_to.window(new_window)

    button_buy = driver.find_element(By.XPATH, '//*[@id="__APP"]/div/div[2]/main/div/div/div[2]/div/div[1]/div[6]/div/button')
    button_buy.click()

    time.sleep(2)

    button_confirm = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/button[2]')
    button_confirm.click()

    time.sleep(4)


def sell_product():
    global average_price

    driver.find_element(By.XPATH, '//*[@id="__APP"]/div/div[2]/main/div/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div/div[1]/div').click()

    driver.find_element(By.XPATH, '//*[@id="__APP"]/div/div[2]/main/div/div/div[2]/div/div[1]/div[5]/div/button[1]').click()
    time.sleep(1)
    change_cur1 = driver.find_element(By.XPATH, '//*[@id="__APP"]/div/div[2]/main/div/div/div[4]/div[2]/div/div[2]')
    ActionChains(driver).move_to_element(change_cur1).click().perform()
    time.sleep(1)
    change_cur2 = driver.find_element(By.XPATH, '//*[@id="BUSD"]')
    if change_cur2.is_displayed():
        ActionChains(driver).move_to_element(change_cur2).click().perform()
    else:
        ActionChains(driver).move_to_element(change_cur1).click().perform()
        ActionChains(driver).move_to_element(change_cur2).click().perform()

    price_input = driver.find_element(By.XPATH, '//*[@id="__APP"]/div/div[2]/main/div/div/div[4]/div[2]/div/div[1]/input')
    price_input.clear()
    for c in str(average_price - 1.5):
        price_input.send_keys(c)

    sell = driver.find_element(By.XPATH, '//*[@id="__APP"]/div/div[2]/main/div/div/div[10]/button[2]')
    sell.click()

    accept = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[7]/button[2]')
    accept.click()
    time.sleep(3)


driver = webdriver.Chrome(executable_path=path)

driver.maximize_window()
driver.implicitly_wait(5)


driver.get("https://binance.com/ru/nft")

a = input('Залогинтесь и нажмите Enter: ')

while True:
    try:
        driver.get(url=product_url)
        time.sleep(3)

        i = 1
        product = f'//*[@id="__APP"]/div/div[2]/main/div/div[2]/div[3]/div[2]/div/div[{i}]'
        # скипаем все предметы, которые еще не выставлены и валюта которых не BUSD
        product_price = product + '/div[3]/div[2]/div/div'
        price = driver.find_element(By.XPATH, product_price).get_attribute('innerHTML').split()
        while driver.find_element(By.XPATH, product).get_attribute('innerHTML').find('Скоро') != -1 or price[1] != 'BUSD':
            i += 1
            product = f'//*[@id="__APP"]/div/div[2]/main/div/div[2]/div[3]/div[2]/div/div[{i}]'
            product_price = product + '/div[3]/div[2]/div/div'
            price = driver.find_element(By.XPATH, product_price).get_attribute('innerHTML').split()

        product_type = product + '/div[3]/div[1]'
        type = driver.find_element(By.XPATH, product_type).get_attribute('innerHTML')
        if type.find('Цена') == -1:
            continue
        product_price = product + '/div[3]/div[2]/div/div'
        min_price = float(price[0].replace(',', ''))
        min_product = driver.find_element(By.XPATH, product)
        print('min price =', min_price)
        # Проверяем правильность сортировки
        min_shown_price = float(driver.find_element(By.XPATH, '//*[@id="__APP"]/div/div[2]/main/div/div[2]/div[1]/div[1]/div[2]').get_attribute('innerHTML').split('<!-- -->')[0].replace(',', ''))
        if not(min_shown_price * 0.85 <= min_price <= min_shown_price * 1.05):
            continue

        # считаем среднюю рыночную цену в BUSD
        amount = 0
        j = i + 1
        count = 0
        while count < 5:
            product = f'//*[@id="__APP"]/div/div[2]/main/div/div[2]/div[3]/div[2]/div/div[{j}]'
            product_price = product + '/div[3]/div[2]/div/div'
            price = driver.find_element(By.XPATH, product_price).get_attribute('innerHTML').split()
            if price[1] != "BUSD":
                j += 1
                continue
            product_type = product + '/div[3]/div[1]'
            amount += float(price[0].replace(',', ''))
            j += 1
            count += 1

        average_price = amount / count
        print('average price =', average_price)

        # Если рыночная цена с вычетом комиссии больше профита, покупаем
        if average_price * (1 - comission / 100) - min_price >= profit:
            try:
                min_product.click()
                buy_product()
                print('КУПЛЕНО ПО ЦЕНЕ', min_price)
                time.sleep(4)
                # Выставление на продажу купленного продукта
                while True:
                    try:
                        driver.get('https://www.binance.com/ru/nft/balance?tab=nft')
                        sell_product()
                        break
                    except:
                        continue

                # Проверка, купили ли продукт
                while True:
                    try:
                        while driver.find_element(By.XPATH,
                                                  '//*[@id="__APP"]/div/div[2]/main/div/div/div[2]/div/div[1]').get_attribute(
                                'innerHTML').find('Снять с продажи') != -1:
                            time.sleep(5)
                            driver.refresh()
                        print('УСПЕШНО ПРОДАНО ЗА', average_price - 0.5)
                        break
                    except:
                        continue

            except:
                print('НЕУДАЧНАЯ ПОПЫТКА')
                continue
    except:
        continue

