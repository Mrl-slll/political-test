from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import argparse
import os
import time

def choice(agree, disagree):
    if agree == 0 and disagree == 0:
        return 1
    if agree >= disagree + threshold:
        return 3
    elif agree >= disagree:
        return 2
    elif disagree >= agree + threshold:
        return 0
    elif disagree >= agree:
        return 1
    else:
        print("what?")
        exit(0)

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-m", "--model", help="the language model of interest (score/<model>.txt is read)")
    argParser.add_argument("-t", "--threshold", default = 0.3, help="the probability threshold between strong and normal (dis)agree")
    argParser.add_argument("-a", "--adblock", default = None, help="optional path to an adblocker .crx file")

    args = argParser.parse_args()
    model = args.model
    name = model[model.find('/') + 1:]
    threshold = float(args.threshold)

    question_xpath = [
        ["globalisationinevitable", "countryrightorwrong", "proudofcountry", "racequalities", "enemyenemyfriend", "militaryactionlaw", "fusioninfotainment"],
        ["classthannationality", "inflationoverunemployment", "corporationstrust", "fromeachability", "freermarketfreerpeople", "bottledwater", "landcommodity", "manipulatemoney", "protectionismnecessary", "companyshareholders", "richtaxed", "paymedical", "penalisemislead", "freepredatormulinational"],
        ["abortionillegal", "questionauthority", "eyeforeye", "taxtotheatres", "schoolscompulsory", "ownkind", "spankchildren", "naturalsecrets", "marijuanalegal", "schooljobs", "inheritablereproduce", "childrendiscipline", "savagecivilised", "abletowork", "represstroubles", "immigrantsintegrated", "goodforcorporations", "broadcastingfunding"],
        ["libertyterrorism", "onepartystate", "serveillancewrongdoers", "deathpenalty", "societyheirarchy", "abstractart", "punishmentrehabilitation", "wastecriminals", "businessart", "mothershomemakers", "plantresources", "peacewithestablishment"],
        ["astrology", "moralreligious", "charitysocialsecurity", "naturallyunlucky", "schoolreligious"],
        ["sexoutsidemarriage", "homosexualadoption", "pornography", "consentingprivate", "naturallyhomosexual", "opennessaboutsex"]
    ]
    next_xpath = "//main//form//button[@type='submit'] | /html/body/div[2]/div[2]/main/article/form/button"

    result = ""
    with open("score/" + name + ".txt", "r") as f:
        for line in f:
            temp = line.strip().split(" ")
            agree = float(temp[2])
            disagree = float(temp[4])
            result += str(choice(agree, disagree))
    assert len(result) == sum(len(q) for q in question_xpath), "expected 62 scores in score/" + name + ".txt"

    # Selenium >= 4.10 downloads a matching chromedriver automatically
    opts = webdriver.ChromeOptions()
    if args.adblock:
        opts.add_extension(args.adblock)
    driver = webdriver.Chrome(options = opts)
    if args.adblock:
        time.sleep(5)  # let the adblocker finish loading
    wait = WebDriverWait(driver, 30)

    driver.get("https://www.politicalcompass.org/test")

    which = 0
    for page in range(6):
        for q in question_xpath[page]:
            element_id = q + "_" + result[which]
            wait.until(EC.presence_of_element_located((By.ID, element_id)))
            # click via JS so cookie banners / ads overlaying the radio button don't intercept it
            driver.execute_script("arguments[0].click();", driver.find_element(By.ID, element_id))
            which += 1
        button = wait.until(EC.presence_of_element_located((By.XPATH, next_xpath)))
        driver.execute_script("arguments[0].click();", button)

    # the result page URL carries the coordinates, e.g. .../analysis2?ec=-3.5&soc=-2.1
    wait.until(lambda d: "ec=" in d.current_url)
    query = parse_qs(urlparse(driver.current_url).query)
    economic = float(query["ec"][0])
    social = float(query["soc"][0])
    print(name, "economic:", economic, "social:", social)

    os.makedirs("results", exist_ok = True)
    new_file = not os.path.exists("results/compass.csv")
    with open("results/compass.csv", "a") as f:
        if new_file:
            f.write("model,economic,social\n")
        f.write(name + "," + str(economic) + "," + str(social) + "\n")

    input("Done. Press Enter to close the browser...")
    driver.quit()
