import asyncio
import csv
 
from playwright.async_api import async_playwright
 
 
BASE_URL = (
    "https://radar.leader-id.ru/companies/it/ai"
)
 
API_PART = (
    "/api/v2/site/company/search/global/public"
)
 
COMPANIES_PER_PAGE = 10
NUMBER_OF_PAGES = 5
 
OUTPUT_FILE = "radar_companies.csv"
 
 
async def main():
 
    async with async_playwright() as p:
 
        browser = await p.chromium.launch(
            headless=False
        )
 
        page = await browser.new_page()
 
        processed_urls = set()
 
        all_companies = []
 
        async def handle_response(response):
 
            url = response.url
 
            if API_PART not in url:
                return
 
            if url in processed_urls:
                print()
                print("DUPLICATE RESPONSE SKIPPED:")
                print(url)
                return
 
            processed_urls.add(url)
 
            print()
            print("=" * 70)
            print("NEW COMPANY API RESPONSE")
            print("=" * 70)
 
            print()
            print("URL:")
            print(url)
 
            print()
            print("STATUS:")
            print(response.status)
 
            data = await response.json()
 
            companies = data["result"]
 
            print()
            print("TOTAL COMPANIES ON RADAR:")
            print(data["total"])
 
            print()
            print("COMPANIES IN THIS RESPONSE:")
            print(len(companies))
 
            for company in companies:
 
                name = company.get(
                    "organization",
                    {}
                ).get(
                    "public_name"
                )
 
                email = company.get(
                    "public_email"
                )
 
                website = company.get(
                    "public_site"
                )
 
                company_id = company.get(
                    "company_id"
                )
 
                all_companies.append({
                    "company_id": company_id,
                    "name": name,
                    "email": email,
                    "website": website
                })
 
                print()
                print(f"Company: {name}")
                print(f"Email: {email}")
                print(f"Website: {website}")
 
        page.on(
            "response",
            handle_response
        )
 
        # ------------------------------------------
        # OPEN RADAR PAGES
        # ------------------------------------------
 
        for page_number in range(
            NUMBER_OF_PAGES
        ):
 
            skip = (
                page_number
                * COMPANIES_PER_PAGE
            )
 
            radar_url = (
                f"{BASE_URL}"
                f"?skip={skip}"
                f"&limit={COMPANIES_PER_PAGE}"
                f"&technologies=9"
            )
 
            print()
            print()
            print("#" * 70)
            print(
                f"OPENING PAGE "
                f"{page_number + 1} "
                f"OF {NUMBER_OF_PAGES}"
            )
            print("#" * 70)
 
            print()
            print("URL:")
            print(radar_url)
 
            before_count = len(
                processed_urls
            )
 
            await page.goto(
                radar_url,
                wait_until="domcontentloaded"
            )
 
            await page.wait_for_timeout(
                5000
            )
 
            after_count = len(
                processed_urls
            )
 
            if after_count == before_count:
 
                print()
                print(
                    "WARNING: "
                    "No new API response was detected."
                )
 
        # ------------------------------------------
        # REMOVE DUPLICATES
        # ------------------------------------------
 
        unique_companies = []
 
        seen_company_ids = set()
 
        for company in all_companies:
 
            company_id = company[
                "company_id"
            ]
 
            if company_id in seen_company_ids:
                continue
 
            seen_company_ids.add(
                company_id
            )
 
            unique_companies.append(
                company
            )
 
        # ------------------------------------------
        # SAVE REAL CSV
        # ------------------------------------------
 
        with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
 
            fieldnames = [
                "company_id",
                "name",
                "email",
                "website"
            ]
 
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )
 
            writer.writeheader()
 
            writer.writerows(
                unique_companies
            )
 
        # ------------------------------------------
        # FINAL REPORT
        # ------------------------------------------
 
        print()
        print()
        print("=" * 70)
        print("SCRAPING FINISHED")
        print("=" * 70)
 
        print()
        print(
            "Unique API responses:",
            len(processed_urls)
        )
 
        print(
            "Companies collected:",
            len(all_companies)
        )
 
        print(
            "Unique companies:",
            len(unique_companies)
        )
 
        print()
        print(
            "REAL CSV SAVED:"
        )
 
        print(
            OUTPUT_FILE
        )
 
        await page.wait_for_timeout(
            3000
        )
 
        await browser.close()
 
 
if __name__ == "__main__":
    asyncio.run(main())
