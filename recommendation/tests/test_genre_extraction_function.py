from recommendation.services.genre_service import GenreService


anime_a = [
    {"id": "1", "name": "Action"},
    {"id": "2", "name": "Adventure"},
    {"id": "3", "name": "Fantasy"},
]

anime_b = [
    {"id": "4", "name": "Action"},
    {"id": "5", "name": "Fantasy"},
    {"id": "6", "name": "Comedy"},
]

source_genres = GenreService.extract_genre_names(anime_a)
candidate_genres = GenreService.extract_genre_names(anime_b)

score = GenreService.calculate_genre_similarity(
    source_genres,
    candidate_genres,
)

print(type(score) is int) 
print(score == 2) # True
print(score)  # 2