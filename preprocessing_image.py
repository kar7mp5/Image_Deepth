#! ./venv/bin/python3
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import requests
import time
import os

import mimetypes
from tqdm import tqdm

from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.firefox.options import Options




class GetImageDepth:
    """
    A class to retrieve image depth maps from a given keyword.
    
    Attributes:
        keyword (str): The keyword used to search for images.
        file_path (str): The directory path to save the depth maps.
    """
    def __init__(self, keyword, file_path):
        """
        Initialize GetImageDepth object.
        
        Args:
            keyword (str): The keyword used to search for images.
            file_path (str): The directory path to save the depth maps.
        """
        self.keyword = keyword
        self.file_path = file_path
        os.makedirs(file_path, exist_ok=True)  # Create the directory if it doesn't exist
        os.makedirs(os.path.join(file_path, "origin_img"), exist_ok=True)
        os.makedirs(os.path.join(file_path, "depth_img"), exist_ok=True)


    def download_images(self):
        """
        Download images from Google using Firefox browser in headless mode.

        This method uses Selenium to open Google Images in Firefox,
        searches for the keyword, extracts image URLs, and downloads the images.

        Raises:
            AssertionError: If no results are found on the search page.
        """
        # Set up Firefox options for headless mode
        options = Options()
        options.add_argument("--headless")  # Run Firefox in headless mode

        # Initialize the Firefox driver with options
        driver = webdriver.Firefox(options=options)

        # Navigate to Google Images search with the keyword
        search_url = f"https://www.google.com/search?q={self.keyword}&tbm=isch"
        driver.get(search_url)

        # Verify that the search results are loaded
        assert "No results found." not in driver.page_source

        # Scroll to the bottom of the page to load all images
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for images to load

            # Check if we have reached the bottom of the page
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Wait for images to load after scrolling
        image_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "YQ4gaf"))
        )

        # Extract image URLs from the elements
        image_urls = []
        for image in image_elements:
            try:
                # Skip images with "YQ4gaf zr758c" class name
                if "zr758c" in image.get_attribute("class"):
                    continue

                img_url = image.get_attribute("src")
                image_urls.append(img_url)

            except Exception as e:
                print(f"Error extracting image URL: {e}")

        # Close the browser
        driver.quit()

        # Download images using ThreadPoolExecutor for parallel downloading
        self._download_images_concurrently(image_urls)


    def _download_images_concurrently(self, image_urls):
        """
        Download images concurrently using ThreadPoolExecutor.
        
        Args:
            image_urls (list): List of image URLs to be downloaded.
        """
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(tqdm(executor.map(self._save_image, image_urls, range(len(image_urls))), total=len(image_urls), desc="Downloading images"))


    def _save_image(self, url, index):
        """
        Save an image from a URL to the specified file path with the correct file extension.

        Args:
            url (str): The image URL.
            index (int): The index of the image for naming.
        """
        try:
            # Request the image data
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()  # Check for HTTP errors

            # Get the content type of the image (e.g., "image/jpeg", "image/png")
            content_type = response.headers.get('Content-Type', '')
            file_extension = mimetypes.guess_extension(content_type)  # Use mimetypes to guess the file extension

            # If mimetypes couldn't determine the extension, default to .jpg
            if not file_extension:
                file_extension = '.jpg'

            # Save the image with the correct file extension
            file_name = os.path.join(os.path.join(self.file_path, "origin_img"), f"image_{index}{file_extension}")
            with open(file_name, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

        except Exception as e:
            print(f"Failed to save image {index}: {e}")




if __name__ == "__main__":
    keyword = input("Image keyword to search: ")
    file_path = os.path.join(os.getcwd(), "train_data")

    getImageDepth = GetImageDepth(keyword=keyword, file_path=file_path)
    getImageDepth.download_images()
