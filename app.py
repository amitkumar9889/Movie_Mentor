import pickle
from flask import Flask, request, render_template
import requests

app = Flask(__name__)


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=392a0c2691aceaf42a49a1b953660189&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


def fetch_movie_details(movie_id):
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=392a0c2691aceaf42a49a1b953660189&language=en-US"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=392a0c2691aceaf42a49a1b953660189&language=en-US"

    movie_data = requests.get(movie_url).json()
    credits_data = requests.get(credits_url).json()

    # Include cast information in the movie data
    movie_data['cast'] = credits_data.get('cast', [])

    return movie_data


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_ids.append(movie_id)
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids


movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))


@app.route('/')
def home():
    movie_list = movies['title'].values
    return render_template('index.html', movie_list=movie_list)


@app.route('/recommend', methods=['GET', 'POST'])
def recommend_movies():
    if request.method == 'POST':
        selected_movie = request.form['selected_movie']
    else:
        selected_movie = request.args.get('selected_movie')

    recommended_movie_names, recommended_movie_posters, recommended_movie_ids = recommend(selected_movie)
    return render_template('recommend.html',
                           movie_names=recommended_movie_names,
                           movie_posters=recommended_movie_posters,
                           movie_ids=recommended_movie_ids,
                           selected_movie=selected_movie,
                           zip=zip)


@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie_data = fetch_movie_details(movie_id)
    selected_movie = request.args.get('selected_movie')
    return render_template('details.html', movie=movie_data, selected_movie=selected_movie)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
