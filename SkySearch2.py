import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as Service
from streamlit_image_coordinates import streamlit_image_coordinates
import time
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import io
from selenium.webdriver.common.keys import Keys
from webdriver_manager.core.os_manager import ChromeType
import random
import math
st.set_page_config(layout="wide", page_title='SkySearch2')

dev = False#use dev to make it run locally, turn off when pushing to streamlit
def create_browser():#in streamlit cloud, browser has to be reloaded on each interaction
    window_size = (1000, 2000)
    with st.spinner("Loading Browser..."):
        options = Options()
        options.add_argument('--headless=new')
        #reduce mem usage, with some options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        #reduce detectability as bot with some more options
        options.add_argument("--disable-blink-features=AutomationControlled")#make it not openly admit to being a bot
        custom_ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "#make us not look exactly like a bot, where this would say HeadlessChrome
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/90.0.4430.212 Safari/537.36")
        options.add_argument(f"user-agent={custom_ua}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if not dev:
            browser = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options)
        else:
            browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        browser.set_window_size(window_size[0], window_size[1])
        #a bit more anti-anti-bot
        browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": """
            //remove the webdriver property
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            //fake the languages property
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            //fake the plugins property (just need a non-zero length)
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """}
        )
        
        return browser
def init_brow():
    if "browser" not in st.session_state or not hasattr(st.session_state["browser"], "service"):
        while True:
            try:
                st.session_state.browser = create_browser()
                break
            except:#retry reloading browser, as it failed. Sometimes that happens in the cloud distro
                st.info("Browser boot failed, trying again.")
def capture_screenshot():
    if 'browser' in st.session_state:#properly initialized, complete screenshot
        #get a screenshot as PIL image
        temp = io.BytesIO(st.session_state.browser.get_screenshot_as_png())

        image = Image.open(temp)
        #resize the image to the proper size, as it may be over- or under-sized
        width = st.session_state.browser.execute_script("return window.innerWidth")#get size of browser, not window
        height = st.session_state.browser.execute_script("return window.innerHeight")
        image = image.resize((width, height))
        st.session_state.display_screenshot = image

init_brow()

if "mode" not in st.session_state:
    st.session_state.mode = 1
if 'avoid_reload' not in st.session_state:
    st.session_state.avoid_reload = False
if st.session_state.mode == 1:
    st.title("SkySearch 2")
    st.caption("Version 1.2.1")
    st.write("A better solution to bypass organizational web censorship")
    url_input = st.text_input("Please input a url here (i.e. https://duckduckgo.com): ")
    if url_input and st.button("Load page"):
        init_brow()
        #open this in selenium browser
        with st.spinner("Loading page..."):
            st.session_state.browser.get(url_input)
            #wait for the page to fully load
            while st.session_state.browser.execute_script("return document.readyState;") != "complete":
                time.sleep(0.1)
        with st.spinner("Booting up display..."):
            capture_screenshot()
            #go into browsing mode
            st.session_state.mode = 2
            st.rerun()
    if st.button("Load DuckDuckGo"):
        init_brow()
        #open this in selenium browser
        with st.spinner("Loading page..."):
            st.session_state.browser.get("https://duckduckgo.com")
            #wait for the page to fully load
            while st.session_state.browser.execute_script("return document.readyState;") != "complete":
                time.sleep(0.1)
        with st.spinner("Booting up display..."):
            capture_screenshot()
            #go into browsing mode
            st.session_state.mode = 2
            st.rerun()
else:
    try:
        reload = False
        cols = st.columns(2)
        with cols[0]:
            if st.button("Go back to homepage"):
                st.session_state.mode = 1
                st.session_state.browser.quit()
                del st.session_state['browser']#reload the browser later, close it for now, to save memory, and make sure it is reloaded by removing a reference to it
                st.session_state.avoid_reload = False
                st.rerun()
        with cols[1]:
            if st.button("Reload viewport"):
                reload = True
        #typing, special keys
        with st.form(clear_on_submit = True, key = 'text'):
            text_input = st.text_area("Input anything to type here (returns can also be entered here).")
            submit = st.form_submit_button("Input")
            if submit:
                actions = ActionChains(st.session_state.browser)
                k = list(text_input)
                for item in k:
                    actions.send_keys(item).perform()
                    time.sleep(random.uniform(0.01, 0.04))
                reload = True
        #get some of the special buttons
        buttons = st.columns(3)#esc, backspace, enter
        with buttons[0]:
            if st.button("Escape"):
                actions = ActionChains(st.session_state.browser)
                actions.send_keys(Keys.ESCAPE).perform()
                reload = True
        with buttons[1]:
            if st.button("Backspace"):
                actions = ActionChains(st.session_state.browser)
                actions.send_keys(Keys.BACKSPACE).perform()
                reload = True
        with buttons[2]:
            if st.button("Enter/Return"):
                actions = ActionChains(st.session_state.browser)
                actions.send_keys(Keys.ENTER).perform()
                reload = True
        clicked_coords = streamlit_image_coordinates(st.session_state.display_screenshot)#find any clicked coordinates on the screen
        if clicked_coords and not st.session_state.avoid_reload:
            with st.spinner('Loading click...'):

                #The for loops below are used to move the mouse in an organic way, to make sure no anti-bot measures happen.
                x, y = clicked_coords['x'], clicked_coords['y']
                actions = ActionChains(st.session_state.browser)
                body = st.session_state.browser.find_element("tag name", "body")#should be top left of the window
                actions.move_by_offset(x, y).perform()
                actions.click().perform()
                actions.move_by_offset(-x, -y).perform()#move back
                reload = True


        if reload and not st.session_state.avoid_reload:#an event occured, we need to reload the window
            with st.spinner("Getting browser response..."):
                #wait for the page to fully load
                while st.session_state.browser.execute_script("return document.readyState;") != "complete":
                    time.sleep(0.1)

                capture_screenshot()       
                st.session_state.avoid_reload = True 
                st.rerun()
        if st.session_state.avoid_reload:
            st.session_state.avoid_reload = False
    except:
        init_brow()
        st.error("An error occured. Please try again.")