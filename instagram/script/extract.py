import os
import json
import time
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver # https://googlechromelabs.github.io/chrome-for-testing/
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
_ = load_dotenv(find_dotenv())   

def web_driver_wait(strategy: function, locator: str):
    return WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((strategy, locator)))

def reject_cookie() -> None:
    """Click on the button to reject all cookies."""
    try:
        web_driver_wait(By.CSS_SELECTOR, 
                        'button[class="_a9-- _ap36 _a9_1"]').click()

        print("Successfully rejected cookies.")
    except Exception as e:
        print("Failed to reject cookies:", str(e))

def reject_notification() -> None:
    """Click on the button to reject turning on the notifications."""
    try:
        web_driver_wait(By.CSS_SELECTOR, 'button[class="_a9-- _a9_1"]').click()

        print("Successfully rejected turning notifications on.")
    except Exception as e:
        print("Failed to reject turning notifications on:", e)

def login() -> None:
    """Login in Instagram using username and password from the .env file.
    TODO: create a condition to show logged in successfully, 
    e.g. wait for a specific button to be available, 
    """
    try:
        username = web_driver_wait(By.CSS_SELECTOR, 'input[name="username"]')
        password = web_driver_wait(By.CSS_SELECTOR, 'input[name="password"]')

        username.clear()
        password.clear()

        username.send_keys(os.environ['INSTAGRAM_USERNAME'])
        time.sleep(1.3)
        password.send_keys(os.environ['INSTAGRAM_PASSWORD'])
        time.sleep(1.3)
        password.send_keys(Keys.RETURN)

        print("Successfully logged in.")
    except Exception as e:
        print("Failed to login: ", str(e))

def scrape_comment(url: str, 
                   get_all_comments: bool=False, 
                   get_n_comment_pages: int=0) -> dict:
    """Return a dict with all the comments from the given url.
    
    Args:
        url: The URL of the post.
        scroll_down: Load more comments

    Returns:
        A dictionary in which the key is a string of the user who posted and 
        the value is a list with the comments. 
    """

    driver.get(url)

    xpath_load_more = '/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div/ul/div[3]/div/div/li/div/button'
    load_more_button = web_driver_wait(By.XPATH, xpath_load_more)

    if get_all_comments: 
        get_all_comments(load_more_button)
    elif not get_all_comments and get_n_comment_pages: 
        get_n_comment_pages(load_more_button, get_n_comment_pages)

    source = driver.page_source
    soup = BeautifulSoup(source, "html.parser")

    try:
        post_user = soup.find('a', class_="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz notranslate _a6hd").text
        post_date = soup.find('time', class_='_aaqe')['datetime']
        post_comments = list()
        outer_divs = soup.select('div.x78zum5.xdt5ytf.x1iyjqo2')
        print("OUTER", outer_divs)

        for div in outer_divs:
            # inside each outer div, find the inner div and extract the text of the span
            inner_div = div.select_one('div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1cy8zhl.x1oa3qoh.x1nhvcw1')
            span = inner_div.select_one('span.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.xvs91rp.xo1l8bm.x5n08af.x10wh9bi.x1wdrske.x8viiok.x18hxmgj')
            
            comment = span.text if span else ""

            time_tag = div.select_one('time.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x1roi4f4.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6')
            comment_date = str(time_tag['datetime']) if time_tag else ""
            
            if comment and comment_date:
                post_comments.append({'comment_date': comment_date, 
                                      'comment': comment})

        post_info = {
            'post_url': url, 
            'post_user': post_user, 
            'post_date': post_date, 
            'post_comments': post_comments
        }

        print("Successfully scraped comments.")

        return post_info
    
    except Exception as e:
        print("Error scraping comments: ", e)
        return None

def get_all_comments(load_more_button) -> None: 
    """Click on the '+' symbol in the comment section until all comments are
    loaded.
    """
    print("Loading all comments...")
    count = 0
    while True:
        time.sleep(1.5)
        if load_more_button:
            load_more_button.click()
            count += 1
            time.sleep(1.5)
        else:
            break
    print(f"Successfully finished loading all [{count}] comment pages.")

def get_n_comment_pages(load_more_button, n: int) -> None: 
    """Click on the '+' symbol in the comment section to load more comments 'n'
    times.
    """
    if n <= 0: raise(ValueError("The parameter 'n' must be greater than 0."))
    
    print(f"Loading more comment pages...")

    for i in range(1, n + 1):
        try:
            time.sleep(1.5)
            if load_more_button:
                load_more_button.click()

                if i > 9 and i % 10 == 0: 
                    print(f"Currently loaded [{i}] pages...")

                time.sleep(0.5)
            else:
                break
        except:
            print("Failed to load more comment pages.")
            break
    print(f"Successfully loaded [{i}] comment pages.")

def get_instagram_post(filename: str) -> list:
    """Transform each post's code in a full instagram URL"""
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError as e:
        print("File not found: ", e)

    print("Successfully loaded all instagram posts.")

    return [line.strip() for line in lines if not line.startswith('#')]

def save_comments_in_json(new_data: dict, 
                          filename: str=f'/home/{os.getlogin()}/Desktop/bachelor_thesis/instagram/data/data.json') -> None:
    print("Saving to [json] file...")

    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump([], f)

    with open(filename, 'r+') as file:
        file_data = json.load(file)

        # if post doesnt exist, immediately append it
        if not has_post(new_data, file_data):
            file_data.append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent=4)
            print("Successfully saved new post to [json] file.")
        # if it exists, add only comments that are not there already
        else:
            print("Appending comments to existing post...")
            try:
                added_coments_count = 0
                for post in file_data:        
                    if post['post_url'] == new_data['post_url']:
                        for comment in new_data['post_comments']:
                            if comment not in post['post_comments']:
                                post['post_comments'].append(comment)
                                added_coments_count += 1
                        print(f"Successfully appended [{added_coments_count}] 
                              comments to [{post['post_url']}].")
                        break
                file.seek(0)
                json.dump(file_data, file, indent=4)
            except Exception as e:
                print("[save_comments_in_json] Error appending comment.", e)

def has_post(new_data: dict, file_data: json) -> bool:
    """Check if a post is already in the json file."""
    for post in file_data:
        if post['post_url'] == new_data['post_url']:
            return True
    return False

def set_link_as_visited(filename: str, link: str, ) -> None:
    with open(filename, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip() == link:
            lines[i] = f"#{lines[i].strip()}\n" 
            break  

    with open(filename, 'w') as f:
        f.writelines(lines)
    
    print(f"Successfully marked [{link}] as read.")

def get_driver():
    user_data_dir = os.environ['GOOGLE_CHROME_PROFILE_PATH']
    chrome_options = Options()
    chrome_options.add_argument(user_data_dir)
    chrome_options.add_argument("--window-size=900x600")
    driver = webdriver.Chrome(options=chrome_options) 
    
    return driver

def main():
    reject_cookie()
    login()

    instagram_posts = get_instagram_post('instagram_posts.txt')

    for idx, post in enumerate(start=1, iterable=instagram_posts):
        if not post:
            print("Skipping to the next post.")
            continue

        print(f"\n### Post: {post} - {idx}/{len(instagram_posts)} ###")
        time.sleep(1.5)
        full_url = "https://www.instagram.com/p/" + post + '/'

        try:
            comments = scrape_comment(full_url)

            if comments: 
                save_comments_in_json(comments)
                set_link_as_visited('instagram_posts.txt', post)                 
            
        except Exception as e:
            print("Error scraping comments in the MAIN: ", e)

if __name__ == '__main__':
    driver = get_driver()
    driver.get("https://www.instagram.com/")
    main()