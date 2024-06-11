from flask import Flask, render_template, request, jsonify
import os

from src.models import Base, engine, session, Tweet, User

app = Flask(__name__)

def save_uploaded_file(file):
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    return file_path


@app.route("/api/tweets", methods=['POST'])
def create_tweet():
    tweet_data = request.json.get('tweet_data')
    # tweet_media_ids = request.json.get('tweet_media_ids')

    new_tweet = Tweet(tweet_data=tweet_data,
                      # tweet_media_ids=tweet_media_ids
                      )
    session.add(new_tweet)
    session.commit()

    tweet_id = new_tweet.id
    session.close()

    return jsonify({
        'result': True,
        'tweet_id': tweet_id
    })


@app.route("/api/medias", methods=['POST'])
def upload_media():
    api_key = request.form.get('api-key')
    if api_key != 'your_api_key':
        return jsonify({'result': False, 'error': 'Invalid API key'}), 403

    uploaded_file = request.files['form']
    if uploaded_file.filename == '':
        return jsonify({'result': False, 'error': 'No file selected'}), 400

    file_path = save_uploaded_file(uploaded_file)

    return jsonify({
        'result': True,
        'media_id': file_path
    })


@app.route("/api/tweets/<int:tweet_id>", methods=['DELETE'])
def delete_tweet(tweet_id):
    api_key = request.json.get('api-key')

    if api_key != '1234':
        return jsonify({'result': False, 'error': 'Invalid API key'}), 403

    tweet = session.query(Tweet).filter(Tweet.id == tweet_id).first()
    if tweet:
        session.delete(tweet)
        session.commit()
        return jsonify({'result': True})
    else:
        return jsonify({'result': False, 'error': 'Tweet not found'}), 404


@app.route("/api/tweets/<int:tweet_id>/likes", methods=['POST'])
def like_tweet(tweet_id, self=None):
    api_key = request.json.get('api-key')

    tweet = session.query(Tweet).filter(Tweet.id == tweet_id).first()
    if tweet:
        Tweet.like(self, tweet)
        session.commit()
        return jsonify({'result': True})
    else:
        return jsonify({'result': False, 'error': 'Tweet not found'}), 404


@app.route("/api/tweets/<int:tweet_id>/likes", methods=['DELETE'])
def unlike_tweet(tweet_id, self=None):
    api_key = request.json.get('api-key')

    tweet = session.query(Tweet).filter(Tweet.id == tweet_id).first()
    if tweet:
        Tweet.unlike(self, tweet)
        session.commit()
        return jsonify({'result': True})
    else:
        return jsonify({'result': False, 'error': 'Tweet not found'}), 404


@app.route('/api/users/<int:user_id>/follow', methods=['POST'])
def follow_user(user_id):
    api_key = request.json.get('api-key')
    if api_key != 'your_api_key':
        return jsonify({'result': False, 'message': 'Invalid API key'}), 401

    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'result': False, 'message': 'User not found'}), 404

    if user.getUserId() not in ...:
        #code here
        ...

    return jsonify({'result': True, 'message': 'Successfully followed user'})


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)
