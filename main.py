import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QSpinBox, QLabel, QPushButton, QFileDialog, QGraphicsView, QGraphicsScene, QCheckBox
from PyQt6.QtCore import Qt
import cv2
import mido
import numpy as np
import os
import subprocess
import random
from PyQt6.QtGui import QImage, QPixmap

class MusicCompositionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Untitled Music Composition Project')
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # Layout
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        
        # Video File Input
        self.load_button = QPushButton('Load Video File')
        self.load_button.clicked.connect(self.load_video_file)
        self.layout.addWidget(self.load_button)

        # Generate MIDI Button
        self.generate_button = QPushButton('Generate MIDI')
        self.generate_button.clicked.connect(self.generate_midi)
        self.layout.addWidget(self.generate_button)

        # Display for number of frames processed
        self.frames_label = QLabel('Frames Processed: 0')
        self.layout.addWidget(self.frames_label)

        # Track Selection Checkboxes
        self.track1_checkbox = QCheckBox('Include Jazz Bass Line')
        self.track1_checkbox.setChecked(True)
        self.layout.addWidget(self.track1_checkbox)

        self.track2_checkbox = QCheckBox('Include Snare Drum')
        self.track2_checkbox.setChecked(True)
        self.layout.addWidget(self.track2_checkbox)

        self.track3_checkbox = QCheckBox('Include Open Hi-Hat')
        self.track3_checkbox.setChecked(True)
        self.layout.addWidget(self.track3_checkbox)

        self.track4_checkbox = QCheckBox('Include Crash Cymbal')
        self.track4_checkbox.setChecked(True)
        self.layout.addWidget(self.track4_checkbox)

        self.track5_checkbox = QCheckBox('Include Toms')
        self.track5_checkbox.setChecked(True)
        self.layout.addWidget(self.track5_checkbox)

        # Variables
        self.video_file = ''

    def load_video_file(self):
        video_path, _ = QFileDialog.getOpenFileName(self, 'Select Video File', '', 'Video Files (*.mp4 *.avi)')
        if video_path:
            self.video_file = video_path
            print(f'Loaded video file: {self.video_file}')

    def generate_midi(self):
        if not self.video_file:
            print('No video file loaded.')
            return
        
        print('Generating MIDI...')
        self.process_video()

    def process_video(self):
        # Open video file
        cap = cv2.VideoCapture(self.video_file)
        
        # Check if video opened successfully
        if not cap.isOpened():
            print('Error: Could not open video.')
            return
        
        # Prepare MIDI file
        midi_file = mido.MidiFile()
        track1 = mido.MidiTrack()  # Kick Drum
        track2 = mido.MidiTrack()  # Snare Drum
        track3 = mido.MidiTrack()  # Open Hi-Hat
        track4 = mido.MidiTrack()  # Crash Cymbal
        track5 = mido.MidiTrack()  # Toms
        midi_file.tracks.append(track1)
        midi_file.tracks.append(track2)
        midi_file.tracks.append(track3)
        midi_file.tracks.append(track4)
        midi_file.tracks.append(track5)

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Update frame count display
            self.frames_label.setText(f'Frames Processed: {frame_count}')

            # Process every frame
            height, width, _ = frame.shape
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Calculate time per frame in MIDI ticks
            time_per_frame = int(mido.second2tick(1/24, ticks_per_beat=480, tempo=mido.bpm2tempo(120)))

            # Track 1: Jazz Bass Line using C minor pentatonic scale
            if self.track1_checkbox.isChecked():
                pentatonic_scale = [48, 51, 53, 55, 58]  # C, Eb, F, G, Bb
                if frame_count % 6 == 0:  # Adjusted to trigger every 6 frames
                    note = random.choice(pentatonic_scale)
                    # Occasionally repeat the previous note
                    if frame_count % 24 == 0:
                        note = previous_note if 'previous_note' in locals() else note
                    previous_note = note
                    # Vary note duration for syncopation
                    duration_factor = random.uniform(0.8, 1.2)
                    note_duration = int(time_per_frame * duration_factor)
                    # Vary velocity for dynamic feel
                    velocity = random.randint(60, 100)
                    track1.append(mido.Message('note_on', channel=9, note=note, velocity=velocity, time=0))
                    track1.append(mido.Message('note_off', channel=9, note=note, velocity=velocity, time=note_duration))
                else:
                    # Insert silence
                    track1.append(mido.Message('note_off', channel=9, note=48, velocity=0, time=time_per_frame))

            # Track 2: Snare Drum (MIDI Note 38)
            if self.track2_checkbox.isChecked():
                mask_orange = cv2.inRange(hsv_frame, (15, 40, 20), (50, 255, 255))
                orange_area = np.sum(mask_orange > 0) / (height * width) * 100
                if orange_area > 5:
                    track2.append(mido.Message('note_on', channel=9, note=38, velocity=64, time=0))
                    track2.append(mido.Message('note_off', channel=9, note=38, velocity=64, time=time_per_frame))
                else:
                    # Insert silence
                    track2.append(mido.Message('note_off', channel=9, note=38, velocity=0, time=time_per_frame))

            # Track 3: Open Hi-Hat (MIDI Note 46)
            if self.track3_checkbox.isChecked():
                black_pixels = np.sum(np.all(frame < [50, 50, 50], axis=2)) / (height * width) * 100
                if black_pixels < 40:
                    track3.append(mido.Message('note_on', channel=9, note=46, velocity=64, time=0))
                    track3.append(mido.Message('note_off', channel=9, note=46, velocity=64, time=time_per_frame))
                else:
                    # Insert silence
                    track3.append(mido.Message('note_off', channel=9, note=46, velocity=0, time=time_per_frame))

            # Track 4: Crash Cymbal (MIDI Note 49)
            if self.track4_checkbox.isChecked():
                if frame_count % 6 == 0:  # Adjusted to trigger every 6 frames
                    track4.append(mido.Message('note_on', channel=9, note=49, velocity=64, time=0))
                    track4.append(mido.Message('note_off', channel=9, note=49, velocity=64, time=time_per_frame))
                else:
                    # Insert silence
                    track4.append(mido.Message('note_off', channel=9, note=49, velocity=0, time=time_per_frame))

            # Toms (MIDI Notes 41, 43, 45)
            if self.track5_checkbox.isChecked():
                if np.sum(mask_orange > 0) / width > 0.3:
                    vertical_position = np.mean(np.where(mask_orange > 0)[0]) / height
                    if vertical_position < 0.33:
                        note = 45  # High Tom
                    elif vertical_position < 0.66:
                        note = 43  # Mid Tom
                    else:
                        note = 41  # Low Tom
                    track5.append(mido.Message('note_on', channel=9, note=note, velocity=64, time=0))
                    track5.append(mido.Message('note_off', channel=9, note=note, velocity=64, time=time_per_frame))
                else:
                    # Insert silence
                    track5.append(mido.Message('note_off', channel=9, note=41, velocity=0, time=time_per_frame))

            frame_count += 1
        
        cap.release()
        
        # Save MIDI file
        midi_file.save('output.mid')
        print('MIDI file generated: output.mid')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MusicCompositionApp()
    window.show()
    sys.exit(app.exec()) 