import requests
import csv
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Set, Tuple
from copy import deepcopy


class MovieDataFetcher:
    BASE_URL = "https://api.themoviedb.org/3"
    MOVIE_URL = BASE_URL + "/discover/movie"
    GENRE_URL = BASE_URL + "/genre/movie/list?language=en"

    def __init__(self, pages: int):
        self.pages = pages
        self.headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8"
        }
        self.movies = []
        self.genres = self._fetch_genres()

    def _fetch_genres(self) -> Dict[int, str]:
        response = requests.get(self.GENRE_URL, headers=self.headers)
        return {genre['id']: genre['name'] for genre in response.json().get('genres', [])}

    def fetch_data(self):
        for page in range(1, self.pages + 1):
            params = {
                "include_adult": "false",
                "include_video": "false",
                "sort_by": "popularity.desc",
                "page": page
            }
            response = requests.get(self.MOVIE_URL, headers=self.headers, params=params)
            self.movies.extend(response.json().get("results", []))

    def get_movies_step(self) -> List[Dict]:
        return self.movies[3:20:4]

    def most_popular_title(self) -> str:
        if not self.movies:
            return ""
        return max(self.movies, key=lambda x: x.get("popularity", 0)).get("title", "")

    def find_by_keywords(self, *keywords: str) -> List[str]:
        result = []
        for movie in self.movies:
            overview = movie.get("overview", "").lower()
            if any(keyword.lower() in overview for keyword in keywords):
                result.append(movie.get("title", ""))
        return result

    def get_unique_genres(self) -> frozenset:
        genre_ids = set()
        for movie in self.movies:
            genre_ids.update(movie.get("genre_ids", []))
        genre_names = {self.genres.get(gid) for gid in genre_ids if self.genres.get(gid)}
        return frozenset(genre_names)

    def delete_by_genre(self, genre_name: str):
        genre_id = next((gid for gid, name in self.genres.items() if name == genre_name), None)
        if genre_id is not None:
            self.movies = [m for m in self.movies if genre_id not in m.get("genre_ids", [])]

    def most_common_genres(self) -> Dict[str, int]:
        counter = defaultdict(int)
        for movie in self.movies:
            for gid in movie.get("genre_ids", []):
                genre_name = self.genres.get(gid)
                if genre_name:
                    counter[genre_name] += 1
        return dict(sorted(counter.items(), key=lambda item: item[1], reverse=True))

    def group_movies_by_common_genre(self) -> frozenset:
        pairs = set()
        for i in range(len(self.movies)):
            for j in range(i + 1, len(self.movies)):
                genres_i = set(self.movies[i].get("genre_ids", []))
                genres_j = set(self.movies[j].get("genre_ids", []))
                if genres_i & genres_j:
                    title_i = self.movies[i].get("title", "")
                    title_j = self.movies[j].get("title", "")
                    if title_i and title_j:
                        pairs.add(tuple(sorted([title_i, title_j])))
        return frozenset(pairs)

    def get_original_and_modified_data(self) -> Tuple[List[Dict], List[Dict]]:
        original = self.movies
        modified = deepcopy(self.movies)
        for movie in modified:
            if movie.get("genre_ids"):
                movie["genre_ids"][0] = 22
        return original, modified

    def get_summary_data(self) -> List[Dict]:
        result = []
        for movie in self.movies:
            try:
                release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d")
                last_day = release_date + timedelta(weeks=10)  # 2 months + 2 weeks = 10 weeks
                result.append({
                    "title": movie.get("title", ""),
                    "popularity": round(movie.get("popularity", 0.0), 1),
                    "score": int(movie.get("vote_average", 0)),
                    "last_day_in_cinema": last_day.strftime("%Y-%m-%d")
                })
            except:
                continue
        return sorted(result, key=lambda x: (-x["score"], -x["popularity"]))

    def write_summary_to_csv(self, path: str):
        summary = self.get_summary_data()
        with open(path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["title", "popularity", "score", "last_day_in_cinema"])
            writer.writeheader()
            writer.writerows(summary)


if __name__ == "__main__":
    fetcher = MovieDataFetcher(pages=2)
    fetcher.fetch_data()

    print(" Most popular title:", fetcher.most_popular_title())
    print(" Titles with keyword 'love':", fetcher.find_by_keywords("love"))
    print(" Unique genres:", fetcher.get_unique_genres())
    print(" Most common genres:", fetcher.most_common_genres())
    print(" Movie groups with common genres:", fetcher.group_movies_by_common_genre())

    # Запис результату в CSV
    fetcher.write_summary_to_csv("movies_summary.csv")
    print(" CSV saved to movies_summary.csv")
