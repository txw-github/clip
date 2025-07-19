
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from subtitle_analyzer import SubtitleAnalyzer
from video_clipper import VideoClipper

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """分析字幕并返回精彩片段"""
    try:
        analyzer = SubtitleAnalyzer()
        all_segments = []
        
        # 获取所有字幕文件
        subtitle_files = [f for f in os.listdir('.') if f.endswith('.txt') and f.startswith('S01E')]
        subtitle_files.sort()
        
        for filename in subtitle_files:
            subtitles = analyzer.parse_subtitle_file(filename)
            exciting = analyzer.find_exciting_segments(subtitles)
            all_segments.extend(exciting)
        
        # 生成剪辑点
        cut_points = analyzer.generate_cut_points(all_segments, max_clips=50)
        
        return jsonify({
            'success': True,
            'clips': cut_points,
            'total': len(cut_points)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/clip', methods=['POST'])
def create_clip():
    """创建单个视频片段"""
    try:
        data = request.json
        clipper = VideoClipper()
        
        episode = data['episode']
        start_time = float(data['start_time'])
        end_time = float(data['end_time'])
        clip_name = data.get('name', f"clip_{int(start_time)}")
        
        video_file = clipper.get_episode_video_file(episode)
        if not video_file:
            return jsonify({
                'success': False,
                'error': f'未找到视频文件: {episode}'
            })
        
        output_path = os.path.join(clipper.output_folder, f"{clip_name}.mp4")
        success = clipper.cut_video_segment(video_file, start_time, end_time, output_path)
        
        return jsonify({
            'success': success,
            'output_file': output_path if success else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download/<filename>')
def download_file(filename):
    """下载生成的视频文件"""
    try:
        return send_file(os.path.join('clips', filename), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    # 创建templates文件夹
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(host='0.0.0.0', port=5000, debug=True)
