import httpx
from typing import List, Optional
from models.search_result import SearchResult
from .base import DataSourceAdapter
from bs4 import BeautifulSoup

class CalibreWebAdapter(DataSourceAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.username = config.get("username")
        self.password = config.get("password")
        self._is_logged_in = False
        # Re-enable follow_redirects=True for the client
        # This allows it to automatically follow redirects during login and search
        self.client = httpx.AsyncClient(base_url=self.web_base_url, follow_redirects=True, timeout=10)

    async def _login(self):
        if self._is_logged_in:
            return

        login_url = f"{self.web_base_url}/login"

        try:
            get_response = await self.client.get(login_url)
            get_response.raise_for_status()

            soup = BeautifulSoup(get_response.text, 'html.parser')
            csrf_token_field = soup.find('input', {'name': 'csrf_token'})
            csrf_token = csrf_token_field['value'] if csrf_token_field else None

            login_data = {
                "username": self.username,
                "password": self.password,
            }
            if csrf_token:
                login_data["csrf_token"] = csrf_token

            response = await self.client.post(
                login_url,
                data=login_data
            )
            
            if str(response.url) == f"{self.web_base_url}/":
                self._is_logged_in = True
            elif "Incorrect username or password" in response.text:
                self._is_logged_in = False
            else:
                self._is_logged_in = False

        except httpx.RequestError as e:
            print(f"Error: {e}")
            self._is_logged_in = False
        except Exception as e:
            print(f"Error: {e}")
            self._is_logged_in = False

        if not self._is_logged_in:
            raise Exception("CalibreWebAdapter: Failed to log in. Check credentials, CSRF token, and server status.")


    async def search(self, query: str) -> List[SearchResult]:
        if not self.enabled: return []
        results = []
        try:
            if not self.web_base_url:
                print("CalibreWebAdapter: web_base_url is not set for the adapter.")
                return results

            await self._login()

            search_url = f"{self.web_base_url}/search"

            headers = {
                "Referer": self.web_base_url + "/"
            }

            response = await self.client.get(
                search_url,
                params={"query": query},
                headers=headers
            )
            response.raise_for_status()

            if 'text/html' not in response.headers.get('Content-Type', ''):
                return results

            soup = BeautifulSoup(response.text, 'html.parser')

            discover_div = soup.find('div', class_='discover')
            if not discover_div:
                return results

            book_divs = discover_div.find_all('div', class_=['book', 'session'])

            if not book_divs:
                row_div = discover_div.find('div', class_='row display-flex')

            for book_div in book_divs:
                title_tag = book_div.find('p', class_='title')
                title = title_tag.get('title', '').strip() if title_tag else "Untitled Book"

                detail_link_tag = book_div.find('a', href=True)
                book_id = None
                if detail_link_tag and '/book/' in detail_link_tag['href']:
                    try:
                        book_id = detail_link_tag['href'].split('/book/')[-1].split('?')[0].split('#')[0]
                    except Exception as e:
                        print(f"--- CalibreWebAdapter Debug: Could not parse book_id from URL: {detail_link_tag['href']}, Error: {e} ---")

                img_tag = book_div.find('img', src=True)
                # Extract the base cover path and the 'c' parameter
                relative_cover_path = None
                if img_tag and 'src' in img_tag.attrs:
                    relative_cover_path = img_tag['src'] # This will be like /cover/4396/og?c=1748679572

                # *** NEW LOGIC FOR thumbnail_url ***
                # Point to your backend's proxy endpoint, passing the book_id and cover_path
                # The frontend will request this URL from your backend, which will then fetch it from Calibre-Web
                thumbnail_url = None
                # if book_id and relative_cover_path:
                #     # Encode the 'c' parameter for URL safety if it exists, or just pass the full path.
                #     # For simplicity, let's just pass the whole relative path.
                #     # This assumes your backend will parse the relative path to reconstruct the full Calibre-Web URL
                #     # Let's refine this: the backend proxy endpoint will need the *exact* path and query params.
                #     # So we send the full relative path, and the proxy will append it to calibreweb_base_url
                #     thumbnail_url = f"/api/calibreweb/cover_proxy?path={httpx.URL(relative_cover_path).path}&query_params={httpx.URL(relative_cover_path).query}"
                #     # Or, more robustly, just pass the book_id and a size parameter, and reconstruct on the backend.
                #     # Given the "og" for original size, let's just pass book_id and assume original size for now.
                #     thumbnail_url = f"/api/calibreweb/cover_proxy/{book_id}" # Simplified for now, we'll get the actual size logic in proxy
                #     # For precise path with 'c' parameter, it's better to pass the entire relative path as a single encoded query param.
                #     thumbnail_url = f"/api/calibreweb/cover_proxy?relative_path={relative_cover_path}"
                #     # Make sure the relative_path is URL-encoded when added as a query param.
                #     import urllib.parse
                #     encoded_relative_path = urllib.parse.quote_plus(relative_cover_path)
                #     thumbnail_url = f"/api/calibreweb/cover_proxy?relative_path={encoded_relative_path}"
                
                author_tag = book_div.find('p', class_='author')
                author = author_tag.find('a', class_='author-name').text.strip() if author_tag and author_tag.find('a', class_='author-name') else "Unknown Author"

                description = None

                if book_id:
                    results.append(SearchResult(
                        id=book_id,
                        source="CalibreWeb",
                        title=title,
                        description=description,
                        thumbnail_url=thumbnail_url, # This will be the new proxied URL
                        detail_url=self._build_detail_url(book_id),
                        type="Book",
                        author=author
                    ))
                else:
                    print(f"--- CalibreWebAdapter Debug: Skipping book due to missing ID: {title} ---")

        except httpx.HTTPStatusError as e:
            print(f"CalibreWebAdapter error: HTTP Error {e.response.status_code} during search. Response: {e.response.text[:500]}")
        except Exception as e:
            print(f"CalibreWebAdapter error during search: {e}")
        return results

    def _build_detail_url(self, book_id: str) -> Optional[str]:
        if self.web_base_url and book_id:
            return f"{self.web_base_url}/book/{book_id}"
        return None