from icrawler.builtin import BingImageCrawler

def download(keyword, folder):
    crawler = BingImageCrawler(storage={"root_dir": f"dataset/{folder}"})
    crawler.crawl(keyword=keyword, max_num=100)

download("driver normal face car", "Normal")
download("driver sleepy eyes closed", "Drowsy")
download("person yawning face", "Yawning")
download("driver using mobile phone car", "Mobile")

print("✅ Dataset ready")