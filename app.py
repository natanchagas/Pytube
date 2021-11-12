from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for,
    send_file
)

from flask_bootstrap import Bootstrap
from forms import GetVideoForm
from pytube import YouTube

import os, ffmpeg

app = Flask(__name__)

configuration = os.path.join(
    os.getcwd(),
    'config',
    'config.py'
)
app.config.from_pyfile(configuration)

bootstrap = Bootstrap()
bootstrap.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def pytube():

    video_form = GetVideoForm()

    if request.method == 'POST' and video_form.validate_on_submit():
        
        if 'youtu.be/' in video_form.video.data:
            video = (video_form.video.data).split('https://youtu.be/')[1]
        else:
            video = (video_form.video.data).split('https://www.youtube.com/watch?v=')[1]
        
        return redirect(url_for('properties', video=video))

    return render_template('index.html', form = video_form)

@app.route('/videos')
def list_videos():
    return 'List videos'

@app.route('/youtube/<video>/properties', methods=['GET', 'POST'])
def properties(video):

    youtube_video = YouTube('http://youtube.com/watch?v=' + video)

    video_resolution = []
    audio_quality = []

    for stream in youtube_video.streams.filter(file_extension='webm'):
        if stream.resolution:
            resolution = int(stream.resolution.split('p')[0])
            if resolution not in video_resolution:
                video_resolution.append(resolution)

        else:
            if stream.abr.split('kbps')[0] not in audio_quality:
                audio_quality.append(int(stream.abr.split('kbps')[0]))

    audio_quality.sort()
    video_resolution.sort()

    return render_template('properties.html', video_options = video_resolution, audio_options = audio_quality, video = video, title = youtube_video.title, thumbnail = youtube_video.thumbnail_url)

@app.route('/youtube/<video>/download', methods=['GET', 'POST'])
def download(video):

    print(request.form['resolution'], request.form['quality'], sep='\n')

    video_streams = []
    audio_streams = []
    
    youtube_video = YouTube('http://youtube.com/watch?v=' + video)

    for stream in youtube_video.streams.filter(file_extension='webm'):
        if stream.resolution:
            if stream.resolution == request.form['resolution']:
                video_streams.append(stream)
        else:
            if request.form['quality'].split(' Kbps')[0] in stream.abr:
                audio_streams.append(stream)

    video_streams[0].download(
        output_path = './videos/raw', 
        filename = video + '_video'
    )

    audio_streams[0].download(
        output_path = './videos/raw', 
        filename = video + '_audio'
    )

    video_file = ffmpeg.input('./videos/raw/' + video + '_video')
    audio_file = ffmpeg.input('./videos/raw/' + video + '_audio')

    ffmpeg.concat(video_file, audio_file, v=1, a=1).output('./videos/processed/' + video + '.mp4').run()

    return render_template('download.html', video = video, title = youtube_video.title, thumbnail = youtube_video.thumbnail_url, file_path ='./videos/processed/' + video + '.mp4')

@app.route('/processed/<video>', methods=['GET', 'POST'])
def download_file(video):    
    return send_file('./videos/processed/' + video + '.mp4', as_attachment = True)
