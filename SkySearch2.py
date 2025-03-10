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
st.set_page_config(layout="wide", page_title='SkySearch2')


dev = False#use dev to make it run locally, turn off when pushing to streamlit

def create_browser():#in streamlit cloud, browser has to be reloaded on each interaction
    with st.spinner("Loading Browser..."):
        options = Options()
        options.add_argument("--window_size={window_size[1]},{window_size[2]}")
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
        if not dev:
            browser = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options)
        else:
            browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return browser
def init_brow():
    if "browser" not in st.session_state or not hasattr(st.session_state["browser"], "service"):
        st.session_state.browser = create_browser()

init_brow()


window_size = (1000, 800)
if "mode" not in st.session_state:
    st.session_state.mode = 1
if "avoid_reloop" not in st.session_state:
    st.session_state.avoid_reloop = False
st.title("SkySearch 2")
st.write("A better solution to bypass organizational web censorship")
if st.session_state.mode == 1:
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
            #get a screenshot as PIL image
            temp = io.BytesIO(st.session_state.browser.get_screenshot_as_png())
 
            image = Image.open(temp)
            #resize the image to the proper size, as it may be over- or under-sized
            width = st.session_state.browser.execute_script("return window.innerWidth")#get size of browser, not window
            height = st.session_state.browser.execute_script("return window.innerHeight")
            image = image.resize((width, height))
            st.session_state.display_screenshot = image
            #go into browsing mode
            st.session_state.mode = 2
            st.rerun()
    if st.button("Load DuckDuckGo"):
        init_brow()
        with st.spinner("Loading page..."):
            st.session_state.browser.get("https://duckduckgo.com")
            #wait for the page to fully load
            while st.session_state.browser.execute_script("return document.readyState;") != "complete":
                time.sleep(0.1)
        with st.spinner("Booting up display..."):
            #get a screenshot as PIL image
            temp = io.BytesIO(st.session_state.browser.get_screenshot_as_png())
 
            image = Image.open(temp)
            #resize the image to the proper size, as it may be over- or under-sized
            width = st.session_state.browser.execute_script("return window.innerWidth")#get size of browser, not window
            height = st.session_state.browser.execute_script("return window.innerHeight")
            image = image.resize((width, height))
            st.session_state.display_screenshot = image
            #go into browsing mode
            st.session_state.mode = 2
            st.rerun()
else:
    reload = False
    cols = st.columns(2)
    with cols[0]:
        if st.button("Go back to homepage"):
            st.session_state.mode = 1
            st.session_state.browser.quit()
            st.rerun()
    with cols[1]:
        if st.button("Reload viewport"):
            reload = True
    #typing, special keys
    text_input = st.text_area("Input anything to type here (returns can also be entered here)")
    if text_input:
        actions = ActionChains(st.session_state.browser)
        actions.send_keys(text_input).perform()
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
    if clicked_coords:
        with st.spinner('Loading click...'):

            x, y = clicked_coords['x'], clicked_coords['y']
            actions = ActionChains(st.session_state.browser)
            body = st.session_state.browser.find_element("tag name", "body")#should be top left of the window
            actions.move_by_offset(x, y).perform()
            actions.click().perform()
            actions.move_by_offset(-x, -y).perform()#move back
            reload = True


    if reload and not st.session_state.avoid_reloop:#an event occured, we need to reload the window
        with st.spinner("Getting browser response..."):
            #wait for the page to fully load
            while st.session_state.browser.execute_script("return document.readyState;") != "complete":
                time.sleep(0.1)
            #get a screenshot as PIL image
            temp = io.BytesIO(st.session_state.browser.get_screenshot_as_png())

            image = Image.open(temp)
            #resize the image to the proper size, as it may be over- or under-sized
            width = st.session_state.browser.execute_script("return window.innerWidth")#get size of browser, not window
            height = st.session_state.browser.execute_script("return window.innerHeight")
            image = image.resize((width, height))
            st.session_state.display_screenshot = image
            st.session_state.avoid_reloop = True
            st.rerun()
    if st.session_state.avoid_reloop:#sometimes, reloops happen, where this else statement gets called over and over. This prevents it.
        st.session_state.avoid_reloop = False