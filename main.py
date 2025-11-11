# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import the global driver
from driver_chrome import driver 
# Import configuration
import config
# Import service functions
import instagram_service as insta

app = FastAPI()

driver.get(config.LOGIN_URL)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/fetch/{username}")
def fetch_instagram(username: str):
    try:
        # Use service functions to perform the steps
        # insta.instagram_login(driver, config.INSTAGRAM_USER, config.INSTAGRAM_PASS)
        # insta.wait_until_logged_in(driver, config.INSTAGRAM_USER, config.INSTAGRAM_PASS)

        profile_url = insta.create_instagram_link(username)
        
        # Use the target URL from config
        html = insta.open_new_tab_and_get_html(
            driver, 
            profile_url, 
            config.INSTAGRAM_USER, 
            config.INSTAGRAM_PASS
        )
        
        data = insta.extract_instagram_data(html)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return {"content": data}
        
    except Exception as e:
        # Provide more specific error details
        raise HTTPException(status_code=500, detail=f"Failed to fetch Instagram data: {str(e)}")
    finally:
        # This code will run whether the try block succeeds or fails
        print("Profile fetch attempt finished.")