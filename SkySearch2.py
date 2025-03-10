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
window_size = (1000, 800)
st.set_page_config(layout="wide")
if "mode" not in st.session_state:
    st.session_state.mode = 1
if "avoid_reloop" not in st.session_state:
    st.session_state.avoid_reloop = False
st.title("SkySearch 2")
st.write("A better solution to bypass organizational web censorship")
if st.session_state.mode == 1:
    url_input = st.text_input("Please input a url here (i.e. https://duckduckgo.com): ")
    if url_input and st.button("Load page"):
        #open this in selenium browser
        with st.spinner("Initializing browser..."):
            options = Options()
            options.add_argument("--window_size={window_size[1]},{window_size[2]}")
            options.add_argument('--headless=new')
            browser = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options)
        with st.spinner("Loading page..."):
            browser.get(url_input)
            #wait for the page to fully load
            while browser.execute_script("return document.readyState;") != "complete":
                time.sleep(0.1)
        with st.spinner("Booting up display..."):
            #get a screenshot as PIL image
            temp = io.BytesIO(browser.get_screenshot_as_png())
 
            image = Image.open(temp)
            #resize the image to the proper size, as it may be over- or under-sized
            width = browser.execute_script("return window.innerWidth")#get size of browser, not window
            height = browser.execute_script("return window.innerHeight")
            image = image.resize((width, height))
            st.session_state.display_screenshot = image
            #go into browsing mode
            st.session_state.browser = browser
            st.session_state.mode = 2
            st.rerun()
    if st.button("Load DuckDuckGo"):
        #open this in selenium browser
        with st.spinner("Initializing browser..."):
            options = Options()
            options.add_argument("--window_size={window_size[1]},{window_size[2]}")
            options.add_argument('--headless=new')
            browser = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options)
        with st.spinner("Loading page..."):
            browser.get("https://duckduckgo.com")
            #wait for the page to fully load
            while browser.execute_script("return document.readyState;") != "complete":
                time.sleep(0.1)
        with st.spinner("Booting up display..."):
            #get a screenshot as PIL image
            temp = io.BytesIO(browser.get_screenshot_as_png())
 
            image = Image.open(temp)
            #resize the image to the proper size, as it may be over- or under-sized
            width = browser.execute_script("return window.innerWidth")#get size of browser, not window
            height = browser.execute_script("return window.innerHeight")
            image = image.resize((width, height))
            st.session_state.display_screenshot = image
            #go into browsing mode
            st.session_state.browser = browser
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
    #add back/forward buttons
    nav = st.columns(2)
    with nav[0]:
        if st.button("⇦Back⇦"):
            st.session_state.browser.back()
            reload = True
    with nav[1]:
        if st.button("⇨Forward⇨"):
            st.session_state.browser.forward()
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