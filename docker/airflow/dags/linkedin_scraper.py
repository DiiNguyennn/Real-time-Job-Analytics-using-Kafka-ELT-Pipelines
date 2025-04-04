from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

def scrape_jobs(keyword, location, max_pages):
    # Đường dẫn ChromeDriver trên Ubuntu
    chrome_driver_path = "/usr/bin/chromedriver"

    # Cấu hình Chrome để tránh bị phát hiện là bot
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    # Khởi tạo trình duyệt
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    jobs = []
    # Truy cập trang tìm kiếm việc làm trên LinkedIn
    for page in range(1, max_pages + 1):
        url = f"https://www.linkedin.com/jobs/search?keywords={keyword}&location={location}&geoId=102267004&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum={page}"
        driver.get(url)
        time.sleep(5)  # Đợi trang tải xong
        # Cuộn trang xuống để tải thêm dữ liệu
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        # Lấy danh sách công việc
        job_listings = driver.find_elements(By.XPATH, '//*[@id="main-content"]/section[2]/ul/li')
        print(f"Số công việc tìm thấy trên trang {page}:{len(job_listings)}")

        for listing in job_listings:
            try:
                # Cuộn tới từng job để tránh lazy loading
                ActionChains(driver).move_to_element(listing).perform()
                time.sleep(1)

                # Lấy tiêu đề công việc
                try:
                    job_title = listing.find_element(By.CLASS_NAME, 'base-search-card__title').text
                except:
                    job_title = None

                # Lấy tên công ty
                try:
                    company_name = listing.find_element(By.CLASS_NAME, 'base-search-card__subtitle').text
                except:
                    company_name = None

                # Lấy địa chỉ
                try:
                    address = listing.find_element(By.CLASS_NAME, 'job-search-card__location').text
                except:
                    address = None

                # Lấy thời gian đăng tuyển
                try:
                    posted_time = listing.find_element(By.CLASS_NAME, 'job-search-card__listdate').text
                except:
                    posted_time = None

                # Lấy đường dẫn chi tiết công việc
                try:
                    job_link = listing.find_element(By.CLASS_NAME, 'base-card__full-link').get_attribute('href')
                except:
                    job_link = None

                job_data = {
                    "job_title": job_title,
                    "company_name": company_name,
                    "address": address,
                    "posted_time": posted_time,
                    "job_link": job_link,
                }

                jobs.append(job_data)

            except Exception as e:
                print("Lỗi khi lấy dữ liệu:", e)

    # Đóng trình duyệt
    driver.quit()
    return jobs