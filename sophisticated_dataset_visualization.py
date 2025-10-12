#!/usr/bin/env python3
"""
Sophisticated Deepfake Dataset Distribution Visualization
Enhanced alignment, structure, and professional appearance
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Wedge
from matplotlib.gridspec import GridSpec
import matplotlib.patheffects as path_effects
import warnings
warnings.filterwarnings('ignore')

# Set professional style with enhanced parameters
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.edgecolor'] = '#2c3e50'
plt.rcParams['xtick.color'] = '#495057'
plt.rcParams['ytick.color'] = '#495057'

class SophisticatedDatasetVisualizer:
    def __init__(self):
        self.colors = {
            'real': '#2E8B57',      # Sea Green
            'fake': '#DC143C',      # Crimson
            'accent': '#2196F3',    # Blue
            'warning': '#FF9800',   # Orange
            'success': '#4CAF50',   # Green
            'info': '#9C27B0',      # Purple
            'light_gray': '#f8f9fa',
            'dark_gray': '#495057',
            'border': '#dee2e6'
        }
        
    def create_sophisticated_dataset_distribution(self):
        """Create sophisticated, properly aligned dataset distribution chart"""
        # Create figure with precise grid layout
        fig = plt.figure(figsize=(20, 14))
        gs = GridSpec(3, 4, figure=fig, 
                     height_ratios=[0.8, 2.5, 1.2], 
                     width_ratios=[1, 1, 1, 1], 
                     hspace=0.25, wspace=0.15)
        
        # Main title area
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        
        # Sophisticated main title with proper hierarchy
        title_text = ax_title.text(0.5, 0.7, 'Deepfake Dataset Distribution', 
                                 ha='center', va='center', transform=ax_title.transAxes,
                                 fontsize=28, fontweight='bold', color='#2c3e50',
                                 path_effects=[path_effects.withStroke(linewidth=4, foreground='white')])
        
        subtitle_text = ax_title.text(0.5, 0.3, 'DFDC + FaceForensics++ + Custom Dataset Analysis', 
                                    ha='center', va='center', transform=ax_title.transAxes,
                                    fontsize=16, fontweight='normal', color='#6c757d')
        
        # Main pie chart area with enhanced 3D effect
        ax_pie = fig.add_subplot(gs[1, :2])
        ax_pie.set_xlim(-1.5, 1.5)
        ax_pie.set_ylim(-1.5, 1.5)
        ax_pie.axis('off')
        
        # Data with precise values
        labels = ['Real Videos', 'Fake Videos']
        sizes = [52.3, 47.7]
        colors = [self.colors['real'], self.colors['fake']]
        explode = (0.1, 0.1)  # Enhanced separation for better 3D effect
        
        # Create sophisticated pie chart
        wedges, texts, autotexts = ax_pie.pie(
            sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90,
            textprops={'fontsize': 18, 'weight': 'bold', 'color': 'white'},
            wedgeprops={'linewidth': 4, 'edgecolor': 'white', 'alpha': 0.95},
            pctdistance=0.85, labeldistance=1.25
        )
        
        # Enhanced text appearance with sophisticated styling
        for i, (autotext, wedge) in enumerate(zip(autotexts, wedges)):
            autotext.set_color('white')
            autotext.set_fontsize(20)
            autotext.set_weight('bold')
            # Create sophisticated text boxes with shadows
            autotext.set_bbox(dict(boxstyle="round,pad=0.5", 
                                 facecolor='black', 
                                 edgecolor='white', 
                                 linewidth=3, 
                                 alpha=0.8))
            # Add sophisticated text effects
            autotext.set_path_effects([
                path_effects.withStroke(linewidth=4, foreground='black')
            ])
        
        # Enhanced labels with perfect positioning
        for i, (text, wedge) in enumerate(zip(texts, wedges)):
            text.set_fontsize(18)
            text.set_weight('bold')
            text.set_color('#2c3e50')
            # Perfect label positioning
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = 1.4 * np.cos(np.radians(angle))
            y = 1.4 * np.sin(np.radians(angle))
            text.set_position((x, y))
            # Add sophisticated text effects
            text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
        
        # Sophisticated description panel
        ax_desc = fig.add_subplot(gs[1, 2:])
        ax_desc.axis('off')
        
        # Create sophisticated description box with gradient effect
        desc_box = FancyBboxPatch(
            (0.05, 0.05), 0.9, 0.9, 
            boxstyle="round,pad=0.03",
            facecolor=self.colors['light_gray'],
            edgecolor=self.colors['border'],
            linewidth=3,
            alpha=0.95
        )
        ax_desc.add_patch(desc_box)
        
        # Sophisticated description content
        description = """Dataset Composition Analysis

• Real Videos (52.3%):
  Authentic video content from multiple
  verified sources and datasets

• Fake Videos (47.7%):
  Synthetically generated content using
  various GAN architectures

• Total Samples: 125,000+ video frames
• Resolution Range: 256x256 to 1024x1024 pixels
• Data Sources: DFDC, FaceForensics++, 
  Celeb-DF, Custom Collection
• Quality Control: Multi-stage validation
  and manual verification process"""
        
        ax_desc.text(0.5, 0.5, description, transform=ax_desc.transAxes, 
                    fontsize=14, ha='center', va='center', 
                    color=self.colors['dark_gray'], fontweight='normal',
                    linespacing=1.4)
        
        # Sophisticated statistics panel
        ax_stats = fig.add_subplot(gs[2, :])
        ax_stats.axis('off')
        
        # Create sophisticated statistics boxes
        stats_data = [
            ("Total Frames", "125,000+", self.colors['accent'], "Comprehensive dataset"),
            ("Real Videos", "65,375", self.colors['real'], "Authentic content"),
            ("Fake Videos", "59,625", self.colors['fake'], "Synthetic content"),
            ("Avg Resolution", "512×512", self.colors['info'], "High quality"),
            ("Data Sources", "4", self.colors['warning'], "Diverse origins")
        ]
        
        box_width = 0.18
        box_height = 0.8
        for i, (label, value, color, description) in enumerate(stats_data):
            x_pos = 0.02 + i * 0.195
            y_pos = 0.1
            
            # Create sophisticated stat box with shadow
            shadow_box = FancyBboxPatch(
                (x_pos + 0.01, y_pos - 0.01), box_width, box_height,
                boxstyle="round,pad=0.02",
                facecolor='black',
                edgecolor='none',
                alpha=0.2
            )
            ax_stats.add_patch(shadow_box)
            
            stat_box = FancyBboxPatch(
                (x_pos, y_pos), box_width, box_height,
                boxstyle="round,pad=0.02",
                facecolor=color,
                edgecolor='white',
                linewidth=3,
                alpha=0.95
            )
            ax_stats.add_patch(stat_box)
            
            # Sophisticated text with proper hierarchy
            ax_stats.text(x_pos + box_width/2, y_pos + box_height/2 + 0.15, value,
                        ha='center', va='center', fontsize=18, fontweight='bold', 
                        color='white', transform=ax_stats.transAxes,
                        path_effects=[path_effects.withStroke(linewidth=2, foreground='black')])
            
            ax_stats.text(x_pos + box_width/2, y_pos + box_height/2, label,
                        ha='center', va='center', fontsize=13, fontweight='bold', 
                        color='white', transform=ax_stats.transAxes,
                        path_effects=[path_effects.withStroke(linewidth=1, foreground='black')])
            
            ax_stats.text(x_pos + box_width/2, y_pos + box_height/2 - 0.15, description,
                        ha='center', va='center', fontsize=10, fontweight='normal', 
                        color='white', transform=ax_stats.transAxes,
                        path_effects=[path_effects.withStroke(linewidth=1, foreground='black')])
        
        # Add sophisticated figure number and reference
        fig_text = fig.text(0.02, 0.98, 'Fig 5.1', transform=fig.transFigure,
                           fontsize=16, fontweight='bold', color='#6c757d',
                           ha='left', va='top')
        
        # Add sophisticated border
        border = plt.Rectangle((0.01, 0.01), 0.98, 0.98, 
                              transform=fig.transFigure, 
                              fill=False, 
                              edgecolor='#dee2e6', 
                              linewidth=2)
        fig.patches.append(border)
        
        plt.tight_layout()
        plt.savefig('sophisticated_dataset_distribution.png', 
                   dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none',
                   pad_inches=0.2)
        plt.close()
        
        print("Sophisticated dataset distribution chart generated successfully!")
        print("File saved: sophisticated_dataset_distribution.png")

if __name__ == "__main__":
    # Create sophisticated visualization generator
    viz_gen = SophisticatedDatasetVisualizer()
    
    # Generate the sophisticated dataset distribution chart
    viz_gen.create_sophisticated_dataset_distribution()
